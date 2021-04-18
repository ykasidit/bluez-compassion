import dbus
import subprocess
import os
import re

# modified iteritems to items() for python3 - from bluez-5.7/test/bluezutils.py

SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"
MIN_BLUEZ_VER = 5.44

# touch a file named 'debug' to activate debug dprint()
debug = os.path.isfile(
    os.path.join(
        os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        ),
        "debug"
    )
)

print(("dprint() debug mode: ",debug))
def dprint(s):
        if debug:
                print(s)

def raise_ex_if_bluez_ver_too_old():
	is_bluez_ver_compatiable(do_raise=True)


def is_bluez_ver_compatiable(do_raise=False):
	ver = float(get_bluez_ver_str())
	if ver > MIN_BLUEZ_VER:
		return True
	emsg = "bluez-compassion requires bluez version {} or newer. (found ver {})".format(MIN_BLUEZ_VER, ver)
	if do_raise:
		raise Exception(emsg)
	print(emsg)
	return False


def get_bluez_ver_str():
	return re.findall("\d+\.\d+", subprocess.check_output("bluetoothctl -v", shell=True).decode('ascii').strip())[0]


def get_managed_objects():
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("org.bluez", "/"),
				"org.freedesktop.DBus.ObjectManager")
	return manager.GetManagedObjects()

def find_adapter(pattern=None):
	return find_adapter_in_objects(get_managed_objects(), pattern)

def find_adapter_in_objects(objects, pattern=None):
	bus = dbus.SystemBus()
	for path, ifaces in list(objects.items()):
		adapter = ifaces.get(ADAPTER_INTERFACE)
		if adapter is None:
			continue
		if not pattern or pattern == adapter["Address"] or \
							path.endswith(pattern):
			obj = bus.get_object(SERVICE_NAME, path)
			return dbus.Interface(obj, ADAPTER_INTERFACE)
	raise Exception("Bluetooth adapter not found")

def find_device(device_address, adapter_pattern=None):
	return find_device_in_objects(get_managed_objects(), device_address,
								adapter_pattern)

def find_device_in_objects(objects, device_address, adapter_pattern=None):
	bus = dbus.SystemBus()
	path_prefix = ""
	if adapter_pattern:
		adapter = find_adapter_in_objects(objects, adapter_pattern)
		path_prefix = adapter.object_path
	for path, ifaces in list(objects.items()):
		device = ifaces.get(DEVICE_INTERFACE)
		if device is None:
			continue
		if (device["Address"] == device_address and
						path.startswith(path_prefix)):
			obj = bus.get_object(SERVICE_NAME, path)
			return dbus.Interface(obj, DEVICE_INTERFACE)

	raise Exception("Bluetooth device not found")


# run to check on import
raise_ex_if_bluez_ver_too_old()
