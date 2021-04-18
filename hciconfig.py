#/usr/bin/env python3

import argparse
import bluezutils
import dbus
import inspect
import subprocess


g_commands_dict = {

    'up':"Power up (on)",
    'down':"Power down (off)",    
    'get_power':"Get the adapter's power state",
    
    'piscan':"Set device discoverable on",
    'noscan':"Set device discoverable off",
    'get_discov':"Get device discoverable state",
    
    'pairable':"Set pairable mode (0=off 1=on -1=get).",

    'class':"Set device class. Example: sudo ./hciconfig -a hci0 class 0x000100", # no dbus api and I'm too lazy to implement mgmt-api - just call the 'btmgmt class'.

    'get_name':"Get device name",
    'name':"Set device name"
}


def print_dict_items(d):
    for i in list(d.items()):
        print(i)


def get_property(iface, prop):
    # if you know of a simpler way to get/set the properties - please suggest - this is from http://stackoverflow.com/questions/9493494/mpris-python-dbus-reading-and-writing-properties
    properties_manager = dbus.Interface(iface, 'org.freedesktop.DBus.Properties')
    return properties_manager.Get(iface.dbus_interface, prop)


def set_property(iface, prop, val):
    properties_manager = dbus.Interface(iface, 'org.freedesktop.DBus.Properties')
    return properties_manager.Set(iface.dbus_interface, prop, val)


############### command implementation functions


def do_piscan(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    set_property(adapter,'DiscoverableTimeout',dbus.UInt32(0))
    set_property(adapter, 'Discoverable',True)
    print("done piscan")


def do_noscan(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    set_property(adapter, 'Discoverable',False)
    print("done noscan")


def do_get_discov(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    print((get_property(adapter, 'Discoverable')))


def do_pairable(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    if int(cmd_args[1]) == 1:
        print("enable Pairable")
        set_property(adapter, "Pairable", True)
    elif int(cmd_args[1]) == 0:
        print("disable Pairable")
        set_property(adapter, "Pairable", False)
    elif int(cmd_args[1]) == -1:
        print(("get Pairable:",get_property(adapter, "Pairable")))
    else:
        print("INVALID: only options 0, 1 and -1 are allowed for pairable (disable, enable, and get respectively).")
    

def do_class(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    "NOTE: We're calling btmgmt here so make sure you have rights (root)."
    leg_class = cmd_args[1] # like 0x020300 means service_class 02 - device_class: major 03 minor 00
    leg_class = leg_class.replace("0x","",1)
    serv_class = "0x"+leg_class[0:2]
    major = "0x"+leg_class[2:4]
    minor = "0x"+leg_class[4:6]
    print(("splitted hex string parts: ",serv_class,major,minor))
    shell_cmd = "btmgmt class "+str(int(major,16))+" "+str(int(minor,16))
    print(("run shell_cmd:",shell_cmd))
    out = subprocess.check_output(shell_cmd,shell=True)
    print(("set class through btmgmt output: "+str(out)))


def do_get_power(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    print(("current power state: ",get_property(adapter, 'Powered')))


def do_down(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    set_property(adapter, 'Powered', False)
    print("done powered false")


def do_up(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    set_property(adapter, 'Powered', True)
    print("done powered true")

    
def do_get_name(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    print(("current dev name: ",get_property(adapter, 'Alias')))

    
def do_name(adapter, cmd_args):
    print(('starting function:', inspect.stack()[0][3]))
    # spaces in name might have got split
    name = " ".join(cmd_args[1:])
    print(("start set name:", name))
    set_property(adapter, 'Alias', name)
    print("done set name")
            

def parse_cmd_args():

    parser = argparse.ArgumentParser(description="Just trying to emulate *some* hciconfig commands",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-a',
	                help="Specify hci device, like 'hci0'.",
                        default='hci0',
    )
    
    parser.add_argument('cmd_args',
                        nargs='*'
    )

    args = vars(parser.parse_args())
    return args


##################### main
if __name__ == '__main__':
    args = parse_cmd_args()
    cmd_args = args['cmd_args']
    print(("cmd_args len",len(args['cmd_args'])))
    if len(args['cmd_args']) == 0:
        print("INVALID: command not specified - supported_commands:")
        print_dict_items(g_commands_dict)
        exit(-1)
    print(('cmd_args:',cmd_args))

    bus = dbus.SystemBus()

    adapter_path = bluezutils.find_adapter(args['a']).object_path
    print(("adapter_path:",adapter_path))

    adapter = dbus.Interface(
        bus.get_object("org.bluez", adapter_path),
	"org.bluez.Adapter1"
    )
    print(("adapter:",adapter))

    # read and work through commands
    cmd = args['cmd_args'][0]
    if cmd in g_commands_dict:
        print(("starting command: ", cmd))
        globals()['do_'+cmd](adapter, cmd_args)
    else:
        print(("ERROR: command","'"+args['cmd_args'][0]+"'","is not in the supported list - we currently only support: "))
        print_dict_items(g_commands_dict)
        exit(-2)
