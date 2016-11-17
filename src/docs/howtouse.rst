Usage Guide
===========

This module contains general support for game controllers. It includes the top level classes such as buttons and
joystick axes which are used for any kind of controller, particular controllers and binding mechanisms are implemented
in sub-modules. The key classes shared across all controllers are:

- :class:`approxeng.input.CentredAxis` and :class:`approxeng.input.TriggerAxis` represents a different kinds of axis of
  an analogue control. The centred axis is used for joysticks with a negative value at one end of the range and positive
  at the other, whereas the trigger axis is used for axes with zero at the resting position and increasingly positive
  values as the control is pressed. As the names suggest, these are used for centred and trigger controls respectively -
  a PS3 joystick consists of two centred axes, an XBox One front trigger consists of a single trigger axis.

- :class:`approxeng.input.Button` represents a single button. As with the Axis class you don't create these, instead you
  need to use the instances provided by the driver classes.

- :class:`approxeng.input.Buttons` represents the state of all the buttons on the controller. You'll use the provided
  instance of this class to register button handlers, ask whether any buttons were pressed, and get information about
  how long a button has been held down.

- Finally, all controller classes inherit from :class:`approxeng.input.Controller`. This provides a
  :class:`approxeng.input.Buttons` instance called 'buttons', and an :class:`approxeng.input.Axes` instance called
  'axes'. Controller-specific implementations will also provide :class:`approxeng.input.Button`,
  :class:`approxeng.input.CentredAxis` and :class:`approxeng.input.TriggerAxis` instances corresponding to each physical
  control on the controller hardware, you should check the class documentation for the particular controller you're
  using to find out exactly what these are.

Constructing and Binding a Controller
-------------------------------------

Once your controller is physically connected to the computer (whether by USB, bluetooth or magic) and you have a
corresponding entry in the dev filesystem, you need to create an object to receive and interpret events from the
hardware, and you need to set up a mechanism by which events will be sent to that object. The object in this case will
be a subclass of :class:`approxeng.input.Controller`, currently there are three implementations:

- :class:`approxeng.input.dualshock3.DualShock3` handles PS3 controllers

- :class:`approxeng.input.dualshock4.DualShock4` is for PS4 controllers

- :class:`approxeng.input.xboxone.XBoxOneSPad` is for the newer XBox One controllers, but is still incomplete.

You'll create one of these objects, and then use the method described at :ref:`binding-reference-label` to connect it to
the event stream. From that point, you use the classes described on this page to read analogue axes and buttons.

Handling Buttons
----------------

You can read from buttons on the controller either by attaching an event handler, or by polling the buttons:

Handling Button Presses as Events
*********************************

.. code-block:: python

    from approxeng.input.asyncorebinder import ControllerResource
    from approxeng.input.dualshock3 import DualShock3
    # Get a joystick
    with ControllerResource(DualShock3()) as joystick:
        # Create a handler function
        def button_handler(button):
            print 'Button clicked {}'.format(button)
        # Register the handler to the SQUARE button
        joystick.buttons.register_button_handler(button_handler, joystick.BUTTON_SQUARE)
        # We can also register a handler to multiple buttons in one call
        joystick.buttons.register_button_handler(button_handler, [joystick.BUTTON_CIRCLE, joystick.BUTTON_TRIANGLE])
        while 1:
            # Do stuff here, only register the button handlers once, not in this loop!
            # If the buttons are pressed, your handlers will be called but not from this thread.
            pass

Registering a button handler, a function which is called whenever the button is pressed, can be useful when you don't
want to repeatedly check whether something's been pressed. I used event handlers in Triangula's code to jump the robot
back to her main menu any time I pressed the home button on the controller. Because I used an event to do this, I didn't
need to worry about getting into some kind of locked state where the robot was out of control and I couldn't stop her -
the button always did the same thing.

The register_button_handler function actually returns a function which can be called to de-register the handler, you
should do this to stop your handler being called when it's no longer needed.

As you can see, there's quite a lot of thinking required to make button handlers work properly. They may be the right
way to do things (for example, you might want a handler which reset the centre point of the analogue sticks, this would
be best done as a handler because it could be called at any time from anywhere else in your code and you wouldn't have
to worry about it). If, however, you're in a polling loop such as Triangula's task framework or PyGame's event loop you
probably just want to know whether a button was pressed since you last checked.

Checking for Button Presses
***************************

The most common requirement you'll have will be to find out whether the user pressed a button. This sounds obvious, but
in fact it's slightly more subtle - what you really want to know is whether the user pressed a button at any point since
you last asked this question! That way, even if you don't ask very often you won't miss button presses and you don't
have to worry about the user pressing so fast you can't detect it.

You can do this with the get_and_clear_button_press_history function. The :class:`approxeng.input.Buttons` instance
maintains a set of flags, one for each button, indicating whether that button has been pressed. These flags are set
when the button is pressed, and all cleared when the function is called, so in effect a flag will be set if the button
was pressed since the last time you asked. The return value from this function is a list of
:class:`approxeng.input.Button` objects representing the buttons that were pressed since you last asked.

.. note::

    Note - previous versions of this code, in particular all of the versions that were part of Triangula's code, worked
    slightly differently. They returned a bit-mask, and you then had to use that to work out what buttons were pressed.
    Hopefully this version is a bit easier to use!

.. code-block:: python

    from approxeng.input.dualshock3 import DualShock3
    from approxeng.input.asyncorebinder import ControllerResource
    # Get a joystick as before
    with ControllerResource(DualShock3()) as joystick:
        # No need for any button handlers, go straight into our loop
        while 1:
            buttons_pressed = joystick.buttons.get_and_clear_button_press_history()
            if joystick.BUTTON_SQUARE in buttons_pressed:
                print 'SQUARE pressed since last check'

Checking for Held Buttons
*************************

You might want to check to see whether a button is being pressed right now, and, if so, how long it has been pressed -
you could have an effect which requires a long press, accelerate your robot more if the button is held down for more
than a second etc etc.

The :class:`approxeng.input.Buttons` class provides a button_pressed() function you can use to do exactly this. You give
it a :class:`approxeng.input.Button` and it tells you how long the button has been held down (in seconds) or returns
None if the button isn't held down.

.. code-block:: python

    from approxeng.input.dualshock3 import DualShock3
    from approxeng.input.asyncorebinder import ControllerResource
    # Get a joystick as before
    with ControllerResource(DualShock3()) as joystick:
        while 1:
            # Get the amount of time the circle button has been held
            held_time = joystick.buttons.is_held(joystick.BUTTON_CIRCLE)
            if held_time is not None:
                # If not none, the time will be the number of seconds it's been held. If None the button isn't pressed.
                print "Circle held for {} seconds".format(held_time)

Reading and Configuring Analogue Axes
-------------------------------------

Analogue axes on the controller are those which can vary continuously over their range. Typically these are joysticks
and triggers. This code maps all axes either to a range from -1.0 to 1.0 (for centred axes such as joysticks) or from
0.0 to 1.0 (for things like triggers where the resting point is at one end of the range of movement). Joysticks are
modelled as two independent centred axes, one for the horizontal part and one for the vertical.

We could just read out the value supplied by the controller hardware and provide that value, but there are a few things
we might want to do first, and which the code provides:

- The centre point of the hardware is often not the numeric centre of the range. This is because hardware exists in the
  real world, where things can be slightly messy. It's generally not far off, but often the resting position isn't at
  0.0.

- The theoretical range of the controller is often larger than the actual range produced. For example, we might have a
  controller which claims to produce values from -255 to 255 (before we normalise down to -1.0 to 1.0) but which
  actually only ever produces values between, say, -251 and 243.

- It's often desirable to have a dead zone near the resting position, so only intentional movements of the controller
  are detected as motion. Analogue controls often have a bit of noise - the joystick may rest at 0 in theory, but in
  practice we might see a string of values such as -1, -1, 0, 1, 1, 0, 0 etc etc.

- Similarly, we might want a 'hot zone' near the extreme positions of the axis, where any higher magnitude values should
  be interpreted as the maximum value. This means we're able to get to the highest value without having to worry about
  controller noise.

Different controllers report different ranges (for example, the PS3 controller range is from 0 to 255 whereas the XBox
controller is from -32768 to 32768), but you don't have to worry about this as the controller implementations specify
this internally and you'll only ever see values between -1.0 and 1.0.

The :class:`approxeng.input.CentredAxis` and :class:`approxeng.input.TriggerAxis` both auto-range, in that they start
off with a maximum and minimum value that's well within the theoretical range, and expand this out when they see higher
values from the controller. This means we don't have to worry that the theoretical range of the controller isn't fully
used, we'll always have our -1.0 to 1.0 correspond to the actual controller movement.

Auto-centring isn't possible as we can't know whether the user is touching the controller, but you can set the centre
point for an individual :class:`approxeng.input.CentredAxis` by setting its 'centre' property, or for a complete set
defined by an :class:`approxent.input.Axes` object by calling the set_axis_centres() function on the Axes object. This
function takes an arbitrary number of parameters and ignores all of them - this is done so you can specify the function
as a button handler.

Dead zones and hot zones are defined as a proportion of the range of the axis:

- For a trigger axis the dead zone is from the 0.0 raw position of the controller up to the specified value, and the hot
  zone is from 1.0 - the value to 1.0. Values below the dead zone value will be returned as 0.0, and values above the
  hot zone will be returned as 1.0, with values inbetween scaling from 0.0 at the edge of the dead zone to 1.0 at the
  edge of the hot zone.

- For centred axes the same applies, but with the dead zone and hot zone values specifying the proportion of each half
  (positive and negative) of the range. So, if the dead zone is set to 0.1 and hot zone to 0.2, positive raw values
  above 0.8 will return a corrected value of 1.0, and those below 0.1 will return 0.0. For negative values the same
  applies, except that values below -0.8 will return -1.0 and those above -0.1 will return 0.0

To obtain the corrected values for an axis you need to call the corrected_value() function on the axis object.

As an example, the PS3 controller exposes four axes, two for each analogue stick. The following code will get a
controller, bind an event handler to a button which will reset the centre points of all axes, and will run around in
a loop printing the corrected value of the left horizontal axis:

.. code-block:: python

    from approxeng.input.dualshock3 import DualShock3, CONTROLLER_NAMES
    from approxeng.input.asyncorebinder import ControllerResource

    with ControllerResource(DualShock3(dead_zone=0.1, hot_zone=0.2), device_name=CONTROLLER_NAMES) as joystick:

        # Bind the square button to call the set_axis_centres function
        joystick.buttons.register_button_handler(joystick.axes.set_axis_centres, joystick.BUTTON_SQUARE)
        # Bind the triangle button to reset any auto-calibration for all axes
        joystick.buttons.register_button_handler(joystick.axes.reset_axis_calibration, joystick.BUTTON_TRIANGLE)

        while 1:
            # Loop, printing the corrected value from the left axis
            print joystick.AXIS_LEFT_HORIZONTAL.corrected_value()

