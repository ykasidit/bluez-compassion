bluez-compassion - compat simple scripts for legacy bluez tools
===============================================================

A collection of *some* compat simple scripts to provide *some* of the features in classic bluez tools like 'hciconfig' - which have been deprecated/removed from newer bluez releases like version '5.44'. (Just to avoid re-implementing old code that uses these tools...)

**NOTE:** This is a very early stage of development and we're just trying implementing *some* commands we used in the past. If you need more commands, please see tools like 'btmgmt' and maybe even scripting 'bluetoothctl' or please help code more features you need/use - for example, you might open hciconfig.py and add your new command into the g_commands_dict dict and add a function named do_<your_command> then access the command args from 'cmd_args' as shown in the example/existing functions. (I'm a C programmer for many years now, please forgive me if my Python code looks awkward.)

Setup and examples
------------------

<pre>
git clone http://github.com/ykasidit/bluez-compassion
cd bluez-compassion
./hciconfig -a hci0 up
<pre>



