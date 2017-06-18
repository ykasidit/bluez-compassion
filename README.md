bluez-compassion - Compat-like 'easily Scriptable' Scripts for rfcomm I/O on Newer bluez versions
=================================================================================================

bluez-compassion aims to provide simple/scriptable commands to get Bluetooth classic IO (starting for 'server' needs) working on newer BlueZ versions, through simple 'legacy-like' command naming (these commands have been deprecated/removed from newer bluez releases - v5.44 onwards) like:
  - hciconfig
  - rfcomm (different syntax - see example below - only server mode - syntax from bluez's 'test/test-profile')

However, the goal is *not* to exactly emulate all options or all of the deprecated bluez commands.

Credit to the [BlueZ](http://www.bluez.org) project for providing many useful 'test' code/examples in the 'test' folder of their source distribution. Most of the code here is based on source in that folder.

**NOTE:** This is a very early stage of development and we're just trying to implement *some* commands we used in the past (and maybe some additional commands too). If you need more commands, please see tools 'bluetoothctl' or please help code more features you need/use - for example, you might open hciconfig.py and add your new command into the g_commands_dict dict and add a function named do_<your_command> then access the command args from 'cmd_args' as shown in the example/existing functions.


Setup and examples
------------------

- Please make sure you've removed older bluez versions (this may break your existing bluetooth tools though). Then, install bluez 5.45 or newer. You can see http://blog.mrgibbs.io/bluez-5-39-ble-setup-on-the-raspberry-pi/ for examples. In my case, below worked for me on Ubuntu 16.04:
**WARNING:** This step will remove the official 'bluez' from your system and most of your existing/legacy bluetooth tools/commands would not work! ('bluetoothctl' would exist though, and is the recommended/updated tool.)
<pre>
sudo apt-get remove bluez
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.45.tar.xz
tar xvf bluez-5.45.tar.xz 
cd bluez-5.45
./configure
make
sudo make install
sudo rm /etc/systemd/system/bluetooth.service
sudo ln -s /lib/systemd/system/bluetooth.service /etc/systemd/system/bluetooth.service
sudo systemctl daemon-reload
sudo systemctl enable bluetooth
</pre>

- Reboot this host/computer/device.

- Please install python and related dbus packages below:
<pre>
python-dbus python-gobject dbus-glib
</pre>

- Clone this repo
<pre>
git clone http://github.com/ykasidit/bluez-compassion
cd bluez-compassion
</pre>

- Get the power state:
<pre>./hciconfig -a hci0 get_power</pre>

- Try power on the Bluetooth adapter:
<pre>./hciconfig -a hci0 up</pre>

- Set discoverable on:
<pre>./hciconfig -a hci0 piscan</pre>

- Set pairable:
<pre>./hciconfig -a hci0 pairable 1</pre>

- Run the [EcoDroidLink's](https://github.com/ykasidit/ecodroidlink) auto pair/accept agent - keep it in the background:
<pre>./edl_agent &</pre>

- Run a 'rfcomm server' (to make a wireless character device - Serial/COM port) waiting for incomming connections:
<pre>./rfcomm -p "/my_serial_port" -n "spp" -s -C 1 -u "0x1101"</pre>

- Connect from your rfcomm 'client' device. (You can use an Android device connecting via the 'Bluetooth Terminal' app.)

Then you can type and press enter here to get it sent/shown on the remote device, type/send from the remote device to get it shown here! Congratulatons! You can now implement the above in your own scripts then redirect this stage's stdin/stdout to/from your script/program.

You can either diconnect using 'Control-C' in this terminal or disconnect from the remote device (like press back in the Bluetooth terminal app on Android) - auto cleanup would take place here and this program would exit.

---

Redirecting read/writes to rx/tx pipes instead of stdout/stdin
--------------------------------------------------------------

NOTE: Since pipes in linux are only 'one-way' direction so we have to use two pipes, one for tx, one for rx, unlike the legacy 'character device where you can both read/write with /dev/rfcomm0'.

Use the -N parameter to created 'named pipes' for reads at <the -N option param>_rx and writes at <the -N option param>_tx.

Example command to run a bluetooth serial port for reads/writes at '/dev/rfcomm0_rx' and '/dev/rfcomm0_tx' respectively:
<pre>python rfcomm.py -p "/my_serial_port" -n "Serial Port" -s -C 1 -u "0x1101" -N "/dev/rfcomm0"</pre>

The above command would wait for a 'pipe reader process' to start first (required for opening a named pipe from this side) so do below in another terminal:
<pre>cat /dev/rfcomm0_rx</pre>

Then connect from your Bluetooth device (or Android app as in the stdin/stdout first example further above). Whatever you write from the remote device would appear in the 'cat' terminal.

If you want to send anything to the connected remote device, just write to /dev/rfcomm0_tx - for example:
<pre>echo "hello from server" > /dev/rfcomm0_tx</pre>

---

Other notable commands
----------------------

- Try power off the Bluetooth adapter:
<pre>./hciconfig -a hci0 down</pre>

- Set device class:

Note: This is using deprecated btmgmt which needs root, and doesn't get built in the default settings of new bluez source like 5.45 - and also I don't know how to use it to set the 'service class' yet so only major/minor (last 4 hex digits) will go through. And it seems to fail as 'invalid' in many cases too. (TODO: re-implement set device class through python-dbus)

<pre>sudo ./hciconfig -a hci0 class 0x000100</pre>


---

LICENSE
-------

This project is released under the same license as 'BlueZ' - GNU GPL - Please see the LICENSE file.

---

AUTHORS
-------

Kasidit Yusuf