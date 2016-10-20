Usage Guide
===========

First you'll need to get the code. The libraries can be installed using the `pip` tool, but you'll need to install a few
linux packages first otherwise they won't build properly. Everything can (and ideally should) be run from within a
virtual environment, nothing requires root permissions:

.. code-block:: bash

    pi@raspberrypi ~ $ sudo apt-get install libpython2.7-dev libusb-dev
    pi@raspberrypi ~ $ pip install approxeng.input

The general pattern for using this code is that you'll create an object representing the controller, for example an
instance of the :class:`approxeng.input.sixaxis.SixAxis` class for a PS3 controller. You then need to connect this
object to something in the operating system that in turn talks to the hardware and feeds the object with events. The
controller object interprets these events, turning them into button presses and movement on well defined joystick axes
which your code can use.

.. note::

    Code from Triangula wraps up the creation of the PS3 controller and the event feed into a single class; in this new
    version of the code these are separated, but it's still easy to use!

The first step is to configure your controller to talk to the operating system (this process varies depending on the
hardware and how it's communicating, it's going to be different connecting a PS3 controller over bluetooth to an XBox
one with a cable). Exactly how to do this is described elsewhere in this documentation.

At the moment the only implementation is for the PS3 SixAxis controller, and the only mechanism for retrieving events
and sending them to a controller object is one based on asyncore (this is slightly out of date, and will hopefully soon
be updated to something more modern!). So, to get this working we need to create a new
object that represents the controller (and which can understand the messages the hardware sends), then wire that to a
source of events. For example:

.. code-block:: python

    from approxeng.input.sixaxis import SixAxis, CONTROLLER_NAME
    from approxeng.input.asyncorebinder import bind_controller
    # Build a new joystick object
    joystick = SixAxis()
    # Use the bind_controller function to connect it to a source of events and start it working
    bind_controller(joystick, CONTROLLER_NAME)

The above code doesn't contain any error checking (the bind_controller method may fail if you don't have an appropriate
controller connected, for example), but other than that it's all you need to set up a PS3 joystick ready for use.

Once a controller is bound, all messages from the physical hardware are routed through to the controller object, and
used to update its internal state - this happens in a background thread, there's no need to tell it to update, you just
use the controller object to get information about the controller.

If you find you want to un-bind from a controller (stopping the background thread and no longer receiving events), the
code is only slightly more complicated:

.. code-block:: python

    from approxeng.input.sixaxis import SixAxis, CONTROLLER_NAME
    from approxeng.input.asyncorebinder import bind_controller
    # Build a new joystick object
    joystick = SixAxis()
    # Use the bind_controller function to connect it to a source of events and start it working, this time we capture
    # the return value, which is a function that can be used to shut down the background thread and stop event reception
    stop_function = bind_controller(joystick, CONTROLLER_NAME)
    # ... do stuff with your controller
    # Shut it down
    stop_function()

Note that we're using the default options here when configuring the :class:`approxeng.input.sixaxis.SixAxis` object, you
should look at the docs for that class to see what else you can specify (mostly relating to how sensitive the joysticks
are, whether to apply auto-calibration, invert the axes etc).

In order to read data from the controller object, you will need to get hold of either :class:`approxeng.input.Axis`
objects (for analogue joysticks and similar), or a :class:`approxeng.input.Buttons` to handle button presses. How you
get these will depend on the controller object, but in the case of the PS3 controller they can be acquired as follows:

.. code-block:: python

    from approxeng.input.sixaxis import SixAxis, CONTROLLER_NAME
    from approxeng.input.asyncorebinder import bind_controller
    # Build a new joystick object
    joystick = SixAxis()
    # Use the bind_controller function to connect it to a source of events and start it working
    bind_controller(joystick, CONTROLLER_NAME)
    # Get the analogue axes as a list of Axis objects
    axes = joystick.axes
    # ..and get a Buttons object to work with button presses
    buttons = joystick.buttons