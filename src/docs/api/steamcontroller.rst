.. _steam-controller-label:

Steam Controller Support
========================

The Valve Steam controller is a strange beast, intended as it is to allow control of games which never expected to use
a controller. Because of this the actual hardware and the way it interacts with the system is a little different to a
regular game controller, and we have to use an additional driver which pulls information from the controller and pushes
it to a virtual device to which we then bind.

The steam controller userland driver can be found on github at SteamController_, you need to follow the instructions
there to obtain and build the driver. You'll need to add appropriate udev rules as specified on that page.

Once you have it, there's a script 'scripts/sc-xbox.py' directory of the driver which you must run as root:

.. code-block:: bash

    sudo ~/viridia-env/bin/python ../scripts/sc-xbox.py start

(In this case I've installed into my virtual environment, so I need to specify the full path to the Python interpreter)

This will run in the background and create a virtual joystick device, the steam controller support in approxeng.input
finds this device automatically just the same way it finds 'real' controllers.

.. automodule:: approxeng.input.steamcontroller
    :members:

.. _SteamController: https://github.com/ynsta/steamcontroller