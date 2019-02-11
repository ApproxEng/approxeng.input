Advanced Usage Guide
====================

This module contains general support for game controllers. It includes the top level classes such as buttons and
joystick axes which are used for any kind of controller, particular controllers and binding mechanisms are implemented
in sub-modules. The key classes shared across all controllers are:

- :class:`approxeng.input.CentredAxis` :class:`approxeng.input.TriggerAxis` and :class:`approxeng.input.BinaryAxis`
  represent different kinds of axis of an analogue control. The centred axis is used for joysticks with a negative value
  at one end of the range and positive at the other, whereas the trigger axis is used for axes with zero at the resting
  position and increasingly positive values as the control is pressed. As the names suggest, these are used for centred
  and trigger controls respectively - a PS3 joystick consists of two centred axes, an XBox One front trigger consists of
  a single trigger axis. The BinaryAxis is used for controllers which export buttons as axes (both the PS4 and the XBox
  controller D-pads are actually a pair of axes in terms of implementation, although they don't have any analogue
  control, they just emit either -1, 0 or 1)

- :class:`approxeng.input.Button` represents a single button. As with the Axis class you don't create these, instead you
  need to use the instances provided by the driver classes.

- :class:`approxeng.input.Buttons` represents the state of all the buttons on the controller. You'll use the provided
  instance of this class to register button handlers, ask whether any buttons were pressed, and get information about
  how long a button has been held down.

- Finally, all controller classes inherit from :class:`approxeng.input.Controller`. This provides a
  :class:`approxeng.input.Buttons` instance called 'buttons', and an :class:`approxeng.input.Axes` instance called
  'axes'. These will come in handy later!

Constructing and Binding a Controller
-------------------------------------

Once your controller is physically connected to the computer (whether by USB, bluetooth, or magic) and you have a
corresponding entry in the dev filesystem, you need to create an object to receive and interpret events from the
hardware, and you need to set up a mechanism by which events will be sent to that object. The object in this case will
be a subclass of :class:`approxeng.input.Controller`, currently the following controllers are supported:

- :class:`approxeng.input.dualshock3.DualShock3` handles PS3 controllers

- :class:`approxeng.input.dualshock4.DualShock4` is for PS4 controllers

- :class:`approxeng.input.xboxone.WiredXBoxOneSPad` and :class:`approxeng.input.xboxone.WirelessXBoxOneSPad` are for the
  newer XBox One controllers. For whatever reason this controller reports different axes and buttons when connected over
  bluetooth to when it's connected with a wire, so you'll need to use the correct one!

- :class:`approxeng.input.rockcandy.RockCandy` for the Rock Candy PS4 controller clone (it appears to describe itself as
  a PS3 controller, but has the controls of a PS4 one!)

- :class:`approxeng.input.steamcontroller.SteamController` for the Valve Steam controller. This is a bit of a strange
  one, and you'll need to be running a driver which creates a virtual XBox360 device to use it, but it does work. See
  :ref:`api_steamcontroller` for details.

- :class:`approxeng.input.wii.WiiRemotePro` for the Nintendo Wii Remote Pro. If you're running in a graphical
  environment you'll probably want to disable the default behaviour where the left stick controls the mouse - see
  :ref:`wii-remote-pro-label` for instructions.

- :class:`approxeng.input.wiimote.WiiMote` for :ref:`api_wiimote`.

- :class:`approxeng.input.sf30pro.SF30Pro` for :ref:`api_sf30pro`.

- :class:`approxeng.input.pihut.PiHut` for :ref:`api_pihut`.

- :class:`approxeng.input.spacemousepro.SpaceMousePro` for :ref:`api_spacemousepro`.

In general you will not explicitly create these objects yourself, instead you can use the binding layer to discover a
connected controller (optionally supplying a particular kind of controller you want, otherwise it just finds the first
one it can). This will create the controller object from which you can read things like axis values, and also set up the
necessary logic to pull events out of the evdev linux system and update the values without you having to do anything.

The only time you're likely to use these classes is to reference them when binding, this allows you to wait for a
specific kind of controller to become available - handy if, say, you really have to have a PS4 controller but you've
got a rock candy dongle plugged in. The details of the discovery process are at :ref:`discovery-reference-label`, once
you've discovered the appropriate controllers you use the binding API to attach to their event streams; the details of
the binding process are described at :ref:`binding-reference-label`.

Handling Buttons
----------------

There are two styles of button handler. The simplest, and the one you're likely to use in almost all cases, is a polling
mechanism - you can ask the Controller object what buttons have been pressed since you last asked that question. This
is easy to use, you don't have to worry you'll miss a button press because you were off doing something else, and it
uses the standard name system. At its simplest you get back an array of standard names of buttons which were pressed
since last time. This part of the API also allows you to test for held buttons, including the duration for which the
button has been held. Handy for where you want the magnitude of a response to be determined by how long a button is held
(could be useful for simulating a 'power charge' or similar).

The second kind is to register a callback function which should be called when a button is pressed. In general you no
longer need to do this - it was used primarily for cases where e.g. a button should interrupt whatever was going on with
a robot and bounce the system back to some safe state, but there are better ways to do this. Nonetheless, this mechanism
is still present and you can use it if you really need to.


Handling Button Presses as Events
*********************************

.. note::

    Only use this method if you are absolutely sure it's what you need. Callback functions will be called from the event
    processing thread - you need to handle these extremely fast or you'll cause issues with missed events! It's almost
    never going to be the right thing to do, you're almost certainly better off using the polling for buttons mechanism
    described in :ref:`poll-presses-label`. With that caveat, here's how to do it if you insist!

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource
    from approxeng.input.dualshock3 import DualShock3
    # Get a joystick
    with ControllerResource(controller_class = DualShock3) as joystick:
        # Create a handler function
        def button_handler(button):
            print('Button clicked {}'.format(button))
        # Register the handler to the SQUARE button
        joystick.buttons.register_button_handler(button_handler, joystick.buttons.for_name('square'))
        # We can also register a handler to multiple buttons in one call
        joystick.buttons.register_button_handler(button_handler, [joystick.buttons.for_name('circle'),
                                                                  joystick.buttons.for_name('triangle')])
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

More about Analogue Axes
------------------------

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
controller is from -32768 to 32768 when plugged in and, for some ungodly reason, 0 to 65335 when wireless), but you
don't have to worry about this as the controller implementations specify this internally and you'll only ever see values
between -1.0 and 1.0, or between 0.0 and 1.0 for trigger axes.

The :class:`approxeng.input.CentredAxis` and :class:`approxeng.input.TriggerAxis` both auto-range, in that they start
off with a maximum and minimum value that's well within the theoretical range, and expand this out when they see higher
values from the controller. This means we don't have to worry that the theoretical range of the controller isn't fully
used, we'll always have our -1.0 to 1.0 correspond to the actual controller movement.

Auto-centring isn't possible as we can't know whether the user is touching the controller, but you can set the centre
point for an individual :class:`approxeng.input.CentredAxis` by setting its 'centre' property, or for a complete set
defined by an :class:`approxeng.input.Axes` object by calling the set_axis_centres() function on the Axes object. This
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

To obtain the corrected values for an axis you need to retrieve the 'value' property on the axis object.

.. _pitutorials: https://twitter.com/pitutorials