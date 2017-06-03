bluez-compassion - Compat Simple Scripts for Input Output Needs on newer BlueZ versions
=======================================================================================

bluez-compassion aims to provide simple/scriptable commands to get Bluetooth classic IO (starting for 'server' needs) working on newer BlueZ versions, through simple 'legacy-like' command naming (these commands have been deprecated/removed from newer bluez releases - v5.44 onwards) like:
  - hciconfig
  - rfcomm

However, the goal is *not* to exactly emulate all options or all of the deprecated bluez commands.

Credit to the [BlueZ](http://www.bluez.org) project for providing many useful 'test' code/examples in the 'test' folder of their source distribution. Most of the code here is based on source in that folder.

**NOTE:** This is a very early stage of development and we're just trying to implement *some* commands we used in the past (and maybe some additional commands too). If you need more commands, please see tools like 'btmgmt' and maybe even scripting 'bluetoothctl' or please help code more features you need/use - for example, you might open hciconfig.py and add your new command into the g_commands_dict dict and add a function named do_<your_command> then access the command args from 'cmd_args' as shown in the example/existing functions.


Setup and examples
------------------

- Please make sure you've installed bluez (either newer bluez versions through source or packages) bluez-utils (for btmgmt) python and related dbus packages listed in example below:
<pre>python-dbus python-gobject dbus-glib</pre>

- Clone this repo
<pre>
git clone http://github.com/ykasidit/bluez-compassion
cd bluez-compassion
</pre>

- Try power off the Bluetooth adapter:
<pre>./hciconfig -a hci0 down</pre>

- Try power on the Bluetooth adapter:
<pre>./hciconfig -a hci0 up</pre>

- Get the power state:
<pre>./hciconfig -a hci0 get_power</pre>

- Set discoverable on:
<pre>./hciconfig -a hci0 piscan</pre>

- Set pairable:
<pre>./hciconfig -a hci0 pairable 1</pre>

- Run a 'rfcomm server' waiting for incomming connections:


- Set device class:
TODO: re-implement through python-dbus
Note: This is using btmgmt which needs root and also I don't know how to use it to set the 'service class' yet so only major/minor (last 4 hex digits) will go through. And it seems to fail as 'invalid' in many cases too.
<pre>sudo ./hciconfig -a hci0 class 0x000100</pre>








