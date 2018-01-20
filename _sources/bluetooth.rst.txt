.. _bluetooth:

Pairing Controllers over Bluetooth
==================================

.. note::

    The XBox One S controller is the only XBox controller with bluetooth support. This won't work for regular (older)
    XBox wireless controllers. In addition, there's a bit of setup required before the bluetooth stack will stay
    connected to the controller, see :ref:`api_xboxone` for instructions.

This guide will show you how to discover and pair with a bluetooth device entirely using the command line. Because this
is a one-time process (controllers will, once paired, connect automatically) you could use the graphical tools to pair
the controller in the first place, but I prefer to run everything on my robots without a display so this is how I do it.

Dependencies
------------

A standard Raspberry Pi will now come with the necessary bluetooth services installed and running, largely because both
the Pi3 and Pi Zero W have built-in bluetooth and wifi chips. This guide assumes you're using one of these newer
versions, if you aren't you may need to explicitly install the bluetooth stack:

.. code-block:: bash

    pi@raspberrypi ~ $ sudo apt-get install bluetooth libbluetooth3 libusb-dev
    pi@raspberrypi ~ $ sudo systemctl enable bluetooth.service
    pi@raspberrypi ~ $ sudo usermod -G bluetooth -a pi

If you have to do the above, you should power cycle your pi, don't just restart it. It might be okay, but you'll make
life more predictable by actually pulling the plug and waiting a few seconds.

Pairing with Bluetoothctl
-------------------------

Once you have a working bluetooth stack, you can use the bluetoothctl command to configure it. You don't need to run
this as root, just use your regular user account.

.. code-block:: bash

    pi@raspberrypi ~ $ bluetoothctl

This will put you into a shell-like mode where you can type commands to manipulate the bluetooth stack. It will also
show messages related to connections, controllers (in this context a controller is a bluetooth master, you'll normally
only have one of these), pairing, scans etc.

The first thing you should do is enable the default agent. The agent is the code which handles pairing requests, and is
necessary to successfully pair with devices which don't have displays or pairing codes. Once you have the bluetoothctl
shell open, type the following (expected responses from bluetoothctl are shown):

.. code-block:: bash

    [bluetooth]# agent on
    Agent registered
    [bluetooth]# default-agent
    Default agent request successful

The next step is to start a bluetooth scan. This is used to discover devices which are either connected already or which
are ready to pair. You need to do this in conjunction with putting your device into pairing mode (the exact mechanism
for this varies from device to device, for example on the XBox One controller you hold down the share button while
pressing the home one, but look up the specifics for your particular controller).

.. code-block:: bash

    [bluetooth]# scan on
    Discovery started
    [CHG] Controller 5C:F3:70:66:5C:E2 Discovering: yes
    .... Messages about devices will follow here

You need to look for messages about your device. Devices are identified by MAC addresses; six part hexadecimal IDs
unique to that particular device. The controller (the bluetooth chipset on your pi) also has a MAC address, in my case
this is the '5C:F3:70:66:5C:E2' part in the above example, yours will be different.

Once you have your device address, you need to issue a 'pair', 'connect' and 'trust' command, to pair with the device,
connect to its services, and to tell the agent that it should trust the device automatically in the future and allow it
to pair with no further checks. You may be asked to confirm these processes (in my example below I'm not because I had
already trusted the device before un-pairing and re-pairing for the example, but if it does just do what it says on the
console).

.. code-block:: bash

    .... after running the 'scan on' and telling my XBox controller to enter pairing mode
    [NEW] Device C8:3F:26:1E:C3:7F Xbox Wireless Controller
    [bluetooth]# pair C8:3F:26:1E:C3:7F
    Attempting to pair with C8:3F:26:1E:C3:7F
    [CHG] Device C8:3F:26:1E:C3:7F Connected: yes
    [CHG] Device C8:3F:26:1E:C3:7F Modalias: usb:v045Ep02E0d0903
    [CHG] Device C8:3F:26:1E:C3:7F UUIDs: 00001124-0000-1000-8000-00805f9b34fb
    [CHG] Device C8:3F:26:1E:C3:7F UUIDs: 00001200-0000-1000-8000-00805f9b34fb
    [CHG] Device C8:3F:26:1E:C3:7F ServicesResolved: yes
    [CHG] Device C8:3F:26:1E:C3:7F Paired: yes
    Pairing successful
    [CHG] Device C8:3F:26:1E:C3:7F ServicesResolved: no
    [CHG] Device C8:3F:26:1E:C3:7F Connected: no
    [bluetooth]# connect C8:3F:26:1E:C3:7F
    Attempting to connect to C8:3F:26:1E:C3:7F
    [CHG] Device C8:3F:26:1E:C3:7F Connected: yes
    Connection successful
    [CHG] Device C8:3F:26:1E:C3:7F ServicesResolved: yes
    [Xbox Wireless Controller]# trust C8:3F:26:1E:C3:7F
    [CHG] Device C8:3F:26:1E:C3:7F Trusted: yes
    Changing C8:3F:26:1E:C3:7F trust succeeded
    [CHG] Device 54:60:09:ED:2E:2F RSSI: -81
    [CHG] Device 54:60:09:ED:2E:2F RSSI: -89
    [Xbox Wireless Controller]#

You can now exit bluetoothctl by pressing CTRL-D or typing 'quit' into the shell.

From now on, your controller (the XBox One S controller in my example) will pair automatically with the bluetooth
adapter on your pi (or other machine if you've configured it). Note that if you're using a bluetooth dongle, the pairing
will have to be re-done if you move the dongle to another computer, so you can't, say, configure a dongle on a linux
desktop and expect it to just work if you move it to your pi.
