#!/usr/bin/python

# example server run command: python rfcomm.py -p "/my_serial_port" -n "Serial Port" -s -C 1 -u "0x1101"

# This file is adapted from the original 'test-profile' file in BlueZ's (v5.45) 'test' folder.

from __future__ import absolute_import, print_function, unicode_literals

#from optparse import OptionParser, make_option
import argparse
import os
import sys
import uuid
import dbus
import dbus.service
import dbus.mainloop.glib
import bluezutils
import multiprocessing as mp
import time
import subprocess

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

g_named_pipe_to_create_path = None
g_srcfd = None
g_targetfd = None
MAX_READ_SIZE = 2048


def _read_fd_to_targetfd(fd, targetfd):
    print("_read_fd_and_print: fd " + str(fd))

    i = 0

    while (True):
        i += 1

        read = None

        try:
            read = os.read(fd, MAX_READ_SIZE)
        except Exception as e:
            #print("os.read (likely nothing to read yet...) exception: "+str(e))
            #print("waiting 1 sec before retry reading...")
            time.sleep(1.0)

        if not read is None:
            try:
                os.write(targetfd, read)
            except Exception as e:
                print("WARNING: write to targetfd (maybe nobody is reading the named-pipe yet?) exception: " + str(e) +" "+str(time.time()))
                time.sleep(1.0)

    print("_read_fd_and_print: fd " + str(fd) + " exit proc")
    return


def _write_fd_from_srcfd(fd, srcfd):
    print("_write_fd_from_srcfd: fd " + str(fd))

    i = 0

    while (True):
        i += 1

        s = None

        try:
            s = os.read(srcfd, MAX_READ_SIZE)
        except Exception as e:
            print("WARNING: read from srcfd (maybe nobody is writing the named-pipe yet?) exception: " + str(e) +" "+str(time.time()))
            time.sleep(1.0)

        if not s is None:
            os.write(fd, s)

    print("_write_fd_from_srcfd: fd " + str(fd) + " exit proc")
    return


class Profile(dbus.service.Object):
    fd = -1

    @dbus.service.method("org.bluez.Profile1",
                         in_signature="", out_signature="")
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method("org.bluez.Profile1",
                         in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method("org.bluez.Profile1",
                         in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):

        global g_srcfd
        global g_targetfd

        self.fd = fd.take()
        print("NewConnection(%s, %d)" % (path, self.fd))
        print("type fd", type(fd))
        print("self.fd", str(self.fd))
        for key in properties.keys():
            if key == "Version" or key == "Features":
                print("  %s = 0x%04x" % (key, properties[key]))
            else:
                print("  %s = %s" % (key, properties[key]))
                self.fd = fd.take()

        print("pre reader_proc cre")
        reader_proc = mp.Process(target=_read_fd_to_targetfd, args=(self.fd, g_targetfd,))
        print("pre reader_proc start")
        reader_proc.start()
        print("reader_proc started")

        print("pre writer_proc cre")
        writer_proc = mp.Process(target=_write_fd_from_srcfd, args=(self.fd, g_srcfd,))
        print("pre writer_proc start")
        writer_proc.start()
        print("writer_proc started")

        ###

        while (True):
            #print("pre seleep")
            time.sleep(1.0)

        print("NewConnection - func exit")
        return

    @dbus.service.method("org.bluez.Profile1",
                            in_signature="o", out_signature=""
    )
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)" % (path))

        if (self.fd > 0):
            os.close(self.fd)
            self.fd = -1


if __name__ == '__main__':

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    manager = dbus.Interface(bus.get_object("org.bluez",
                                            "/org/bluez"), "org.bluez.ProfileManager1")

    parser = argparse.ArgumentParser(description="Just trying to emulate *some* rfcomm commands",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                     )

    parser.add_argument("-u", "--uuid", dest="uuid",
                    default=None)
    parser.add_argument("-p", "--path", dest="path",
                    default="/foo/bar/profile"),
    parser.add_argument("-n", "--name", dest="name",
                    default=None),
    parser.add_argument("-s", "--server",
                    action="store_const",
                    const="server", dest="role"),
    parser.add_argument("-c", "--client",
                    action="store_const",
                    const="client", dest="role"),
    parser.add_argument("-a", "--auto-connect",
                    action="store_true",
                    dest="auto_connect", default=False),
    parser.add_argument("-P", "--PSM", dest="psm",
                    default=None),
    parser.add_argument("-C", "--channel",
                    dest="channel",
                    default=None),
    parser.add_argument("-r", "--record",
                    dest="record",
                    default=None),
    parser.add_argument("-S", "--service",
                        dest="service",
                    default=None),
    parser.add_argument("-N", "--create-named-pipe",
                    help="""If not specified, stdout and stdin would be used (read/type directly in this run).
                         Otherwise, we'll create a named pipe at the specified path and redirect read/writes there.""",
                    dest="npp",
                    default=None),

    parser.add_argument('cmd_args',
                        nargs='*'
                        )

    args = vars(parser.parse_args())

    profile = Profile(bus, args['path'])

    mainloop = GObject.MainLoop()

    opts = {
        "AutoConnect": args['auto_connect'],
    }

    if (args['name']):
        opts["Name"] = args['name']

    if (args['role']):
        opts["Role"] = args['role']

    if (args['psm'] is not None):
        opts["PSM"] = dbus.UInt16(int(args['psm']))

    if (args['channel'] is not None):
        opts["Channel"] = dbus.UInt16(int(args['channel']))

    if (args['record']):
        opts["ServiceRecord"] = args['record']

    if (args['service']):
        opts["Service"] = args['service']

    if not args['uuid']:
        args['uuid'] = str(uuid.uuid4())

    if (args['npp']):
        g_named_pipe_to_create_path = args['npp']
        print("g_named_pipe_to_create_path: "+str(g_named_pipe_to_create_path))
        try:
            print("remove any existing file at: " + str(g_named_pipe_to_create_path))
            os.remove(g_named_pipe_to_create_path)
        except:
            pass

        print("creating the named-pipe...")
        os.mkfifo(g_named_pipe_to_create_path)

        print("opening the created named-pipe at: " + str(g_named_pipe_to_create_path))
        print("opening read fd")
        g_srcfd = os.open(g_named_pipe_to_create_path, os.O_RDONLY|os.O_NONBLOCK)
        print("opening write fd")
        g_targetfd = os.open(g_named_pipe_to_create_path, os.O_WRONLY|os.O_NONBLOCK)
        print("open named-pipe success")

        print("create named-pipe success")
    else:
        g_named_pipe_to_create_path = None
        print("Using stdin/stdout for read/writes...")
        g_targetfd = sys.stdout.fileno()
        g_srcfd = sys.stdin.fileno()

    print("rfcomm.py calling RegisterProfile")
    manager.RegisterProfile(args['path'], args['uuid'], opts)
    print("rfcomm.py calling RegisterProfile - done - waiting for incoming connections...")

    mainloop.run()
