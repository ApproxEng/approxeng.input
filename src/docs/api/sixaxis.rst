approxeng.input.sixaxis: PlayStation3 Controller Support
========================================================

The SixAxis class contains the logic to read from a PlayStation3 controller connected over BlueTooth, including axis
calibration, centering and dead-zones, and the ability to bind functions to button presses. This uses evdev for event
handling, attempting to use this on any other platform than Linux will probably not work.

.. autoclass:: approxeng.input.sixaxis.SixAxis
:members:

    An additional class allows for use within a 'with' binding. The connection and disconnection is managed automatically
    by the resource, so there's no need to call connect() on the generated :class:`approxeng.input.sixaxis.SixAxis` instance.

.. autoclass:: approxeng.input.sixaxis.SixAxisResource
:members:

    As an example, the following code will bind to an already paired PS3 controller and continuously print its axes:

.. code-block:: python

    from approxeng.input.sixaxis import SixAxisResource
    # Get a joystick, this will fail unless the SixAxis controller is paired and active
    with SixAxisResource() as joystick:
        while 1:
            # Default behaviour is to print the values of the four analogue axes
            print joystick

Axes
----

The SixAxis class exposes four :class:`approxeng.input.Axis` instances, one for each of the axes from the analogue
sticks (yes, I know, it's called a SixAxis and it has four Axis instances. The tilt sensor isn't supported, sorry!). The
axes are accessible through the `axes` member of the :class:`approxeng.input.sixaxis.SixAxis` class, and are as follows:

axes[0]
    Left stick, horizontal axis.

axes[1]
    Left stick, vertical axis.

axes[2]
    Right stick, horizontal axis.

axes[3]
    Right stick, vertical axis.

In all cases the positive direction is up or to the right.

Buttons
-------

An instance of the :class:`approxeng.input.Buttons` is exposed through the `buttons` member of the
:class:`approxeng.input.sixaxis.SixAxis` class. This can be used to bind event handlers, monitor button presses etc. as
described in the `Buttons` class documentation.