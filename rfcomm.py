#!/usr/bin/python

# example server run: python rfcomm.py -p "/my_serial_port" -n "spp" -s -C 1 -u "0x1101"

# This file is adapted from the original 'test-profile' file in BlueZ's (v5.45) 'test' folder.

from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import os
import sys
import uuid
import dbus
import dbus.service
import dbus.mainloop.glib
import bluezutils
import multiprocessing as mp
import time

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

MAX_READ_SIZE = 2048


def _read_fd_to_targetfd(fd, targetfd):
    print("_read_fd_and_print: fd " + str(fd))

    i = 0

    while (True):
        i += 1
        read = None
        try:
            read = os.read(fd, MAX_READ_SIZE)
            os.write(targetfd, read)
        except Exception as e:
            #print("os.read (likely nothing to read yet...) exception: "+str(e))
            #print("waiting 1 sec before retry reading...")
            time.sleep(1.0)

    print("_read_fd_and_print: fd " + str(fd) + " exit proc")
    return


def _write_fd_from_srcfd(fd, srcfd):
    print("_write_fd_from_srcfd: fd " + str(fd))

    i = 0

    while (True):
        i += 1
        s = os.read(srcfd, MAX_READ_SIZE)
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

        targetfd = sys.stdout.fileno()
        print("pre reader_proc cre")
        reader_proc = mp.Process(target=_read_fd_to_targetfd, args=(self.fd, targetfd,))
        print("pre reader_proc start")
        reader_proc.start()
        print("reader_proc started")

        print("pre writer_proc cre")
        srcfd = sys.stdin.fileno()
        writer_proc = mp.Process(target=_write_fd_from_srcfd, args=(self.fd, srcfd,))
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

    option_list = [
        make_option("-u", "--uuid", action="store",
                    type="string", dest="uuid",
                    default=None),
        make_option("-p", "--path", action="store",
                    type="string", dest="path",
                    default="/foo/bar/profile"),
        make_option("-n", "--name", action="store",
                    type="string", dest="name",
                    default=None),
        make_option("-s", "--server",
                    action="store_const",
                    const="server", dest="role"),
        make_option("-c", "--client",
                    action="store_const",
                    const="client", dest="role"),
        make_option("-a", "--auto-connect",
                    action="store_true",
                    dest="auto_connect", default=False),
        make_option("-P", "--PSM", action="store",
                    type="int", dest="psm",
                    default=None),
        make_option("-C", "--channel", action="store",
                    type="int", dest="channel",
                    default=None),
        make_option("-r", "--record", action="store",
                    type="string", dest="record",
                    default=None),
        make_option("-S", "--service", action="store",
                    type="string", dest="service",
                    default=None),
    ]

    parser = OptionParser(option_list=option_list)

    (options, args) = parser.parse_args()

    profile = Profile(bus, options.path)

    mainloop = GObject.MainLoop()

    opts = {
        "AutoConnect": options.auto_connect,
    }

    if (options.name):
        opts["Name"] = options.name

    if (options.role):
        opts["Role"] = options.role

    if (options.psm is not None):
        opts["PSM"] = dbus.UInt16(options.psm)

    if (options.channel is not None):
        opts["Channel"] = dbus.UInt16(options.channel)

    if (options.record):
        opts["ServiceRecord"] = options.record

    if (options.service):
        opts["Service"] = options.service

    if not options.uuid:
        options.uuid = str(uuid.uuid4())

    print("rfcomm.py calling RegisterProfile")
    manager.RegisterProfile(options.path, options.uuid, opts)
    print("rfcomm.py calling RegisterProfile - done - waiting for incoming connections...")

    mainloop.run()
