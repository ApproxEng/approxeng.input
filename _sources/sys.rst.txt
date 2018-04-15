.. _sys:

LEDs and Battery Monitoring
---------------------------

New in version 2.2 is the ability to control the LEDs, and read the battery level, of some controllers. In this initial
release the library supports LEDs on the PS3 and PS4 controllers, and battery monitoring for the PS3, PS4 and XB1 with
the last of those only reporting battery levels when connected over bluetooth.

Enabling access to LEDs
=======================

.. note::

    You must do the steps below if you want to write to LED state on your controller. If you do not, it will not work
    and you'll probably encounter file permission errors.

We write to files in `/sys/class/leds` to change LED state on a connected controller. By default under linux these file
nodes are not writeable for non-root users. To fix this, we need to add some udev rules, create a new group for users
who should be able to access LEDs, and then add the appropriate user to that group.

Firstly create a new file, `90-led-permission.rules` in `/etc/udev/rules.d/` with the following contents:

.. literalinclude:: ../90-led-permissions.rules
    :linenos:

Then create a new `leds` group:

.. code-block:: bash

    > sudo groupadd leds

Then add membership of that new group to the appropriate user. In this case we'll use the user `pi`, the default user
on the Raspberry Pi:

.. code-block:: bash

    > sudo usermod -a -G leds pi

Once you've done all the above, you need to either restart the pi (simplest option) or, if you know what you're doing,
force a re-load of the udev rules and log out then back in again to pick up the new group membership. Once this is done,
any new nodes corresponding to LEDs will be writeable for users in the `leds` group, and the user you selected will be
a member of that group.

Writing to LEDs
===============

There is no single standard API used to write to LEDs, because each controller is different. If your controller supports
this, and in version 2.2 this is restricted to the DS3 and DS4 controllers, it will be described in the documentation
for the controller class itself. Specifically, for the DS3 controller you can control each individual red LED to be on
or off with :meth:`approxeng.input.dualshock3.DualShock3.set_led`, and on the DS4 controller you can set the hue,
saturation and value (brightness) of the front bar RGB LED with :meth:`approxeng.input.dualshock4.DualShock4.set_leds`
method. Because these methods are entirely controller specific, you should either user a form of the binder that
requires that controller type, or explicitly check that you've got the right kind of controller (or handle the absence
of these methods in your own code when you call them).

The examples below show how to use the LEDs on the DS3 (scanning across the four LEDs), and the light bar on the DS4
(animating a rainbow of colours):

.. literalinclude:: ../../scripts/cylon.py
    :language: python
    :linenos:

.. literalinclude:: ../../scripts/ds4_rainbow.py
    :language: python
    :linenos:

Reading Battery Levels
======================

Controllers now all have a property `battery_level`. Controllers that support battery monitoring (currently the DS3, DS4
and XB1 controller when connected wirelessly) will return a floating point value between 0.0 (empty) and 1.0 (full) to
indicate the battery level of the associated controller. Controllers that do not support this feature will return None,
so you potentially need to handle the return value not being a number.

Not all controllers report fine-grained battery levels. For example, the DS3 only reports four partial battery levels,
so you'll probably only see 0, 0.25, 0.5, 0.75, and 1.0, whereas the DS4 reports to the nearest 0.1 and the XB1 is
slightly finer grained.

.. note::

    Be aware that every time you read the `battery_level` property, the code has to open a file and read the value from
    it. While this is fast, because the file is a virtual one, the battery level only changes quite slowly so you should
    only query this property fairly infrequently to avoid excessive IO access. Checking every minute or so is almost
    certainly going to be good enough.

The updated `show_controls.py` script now indicates battery level if the controller supports it (see line 67 below):

.. literalinclude:: ../../scripts/show_controls.py
    :language: python
    :linenos:
