.. _simple_api:

Simple Usage
------------

In version 2.0 of this library, the API has been simplified and made more Python-like. Rather than having to fetch
nested objects containing axis and button information, all the most common operations are now available as methods and
attributes of the controller class itself. Read on...

Connecting to a controller
**************************

To connect to a controller you do the following (including error handling):

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource

    while True:
        try:
            with ControllerResource() as joystick:
                print('Found a joystick and connected')
                while joystick.connected:
                    # Do stuff with your joystick here!
                    # ....
                    # ....
            # Joystick disconnected...
            print('Connection to joystick lost')
        except IOError:
            # No joystick found, wait for a bit before trying again
            print('Unable to find any joysticks')
            sleep(1.0)


This example will loop forever. It will attempt to connect to any supported joystick - the ControllerResource will raise
IOError if it can't find one, otherwise it will do all the necessary background work, create a controller object and, in
this case, bind it to the 'joystick' variable which can then be used to read axes, buttons etc.

The :meth:`~approxeng.input.Controller.connected` property on the joystick object indicates whether the underlying
device is connected or not - if, for example, you have a controller that goes out of range, runs out of batteries, or is
turned off while in use this will be set to False and you can handle the case correctly (if using this code in a robot,
this would be an excellent time to turn of all your motors, for instance!)

The :class:`~approxeng.input.selectbinder.ControllerResource` class accepts a number of, optional, arguments. These can be
used to tell it which controller type to use (the default is to connect to the first controller it can understand, but
if you have multiple controllers connected for some reason you might want to tell it to use your XBox1 rather than your
PS4 controller). They can also be used to configure the default settings for axes, and there's an option to print out
debug information. In general though you'll only ever need the simple form shown here.

Once you have a controller object you can use it to read axes and buttons, both of which are referenced by a standard
name (see  :ref:`sname-label`) - this allows you to not worry too much about exactly what controller's going to be
present. Rather than having to know that the XBox controller has 'A','B'... and so on, whereas the Playstation
controllers have 'cross', 'circle' etc the API defines a standard set of names for buttons and axes (they're based on
the PS3 controller as it happens, mostly because that's the one I first used when I started writing the library!).

Connecting to multiple controllers
**********************************

To connect to multiple controllers, or to be more specific about the types and capabilities of controllers you need,
see :ref:`discovery-reference-label`. The example below shows binding to two controllers, the first of which must be
a PS3 controller, the second of which must have a left X and Y axis:

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource
    from approxeng.input.dualshock3 import DualShock3
    from approxeng.input.controllers import ControllerRequirement

    while True:
        try:
            with ControllerResource(ControllerRequirement(require_class=DualShock3),
                                    ControllerRequirement(require_snames=['lx','ly'])) as ds3, joystick:
                print('Found two joysticks and connected')
                while joystick.connected and ds3.connected:
                    # Do stuff with your joystick here!
                    # ....
                    # ....
            # One or both joystick(s) disconnected...
            print('Connection to joystick(s) lost')
        except IOError:
            # No matching joystick found, wait for a bit before trying again
            print('Unable to find matching joysticks')
            sleep(1.0)

Reading Analogue Axes
*********************

Analogue axes are those which vary continuously, allowing for fine control of motion. Unlike buttons, which are either
on or off, an analogue axis has a floating point value associated with its current position.

    * Centred axes have a value ranging from -1.0 to 1.0
    * Trigger axes have a value ranging from 0.0 to 1.0

Axis values are read as properties of the joystick object (in this and other examples we're not showing the exception
handling from the first example, but you should still do it!):

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource

    # Get a joystick
    with ControllerResource() as joystick:
        # Loop until disconnected
        while joystick.connected:
            # Get a corrected value for the left stick x-axis
            left_x = joystick['lx']
            # We can also get values as attributes:
            left_y = joystick.ly


...and that's it! You might have used other libraries which require you to do event handling and similar, but in this
case all that stuff is taken care of in the background and you just have to read the information you want from the
joystick object.

Circular Analogue Axes
======================

As of version 2.4, if a controller defines pairs of `(lx,ly)`, or `(rx,ry)`, a new virtual axis is created called `l` or
`r` respectively. This is an instance of :class:`~approxeng.input.CircularCentredAxis`. Unlike other axes which return
a single floating point value, this axis type returns a tuple of `(x,y)` floats. Obviously you could do this yourself
by calling the individual horizontal and vertical axes, but this circular axis has a subtle improvement to how it
handles dead and hot zones - areas where you want either no output (the deadzone in the middle) or full output (the hot
zones at either end of the range). Specifically, it judges whether a position is in the dead or hot zone based on the
overall distance of the stick from the centre, taking both axes into account, and then scales both values such that the
direction is preserved and the magnitude scaled. For cases where you genuinely want to control a two dimensional
quantity with the stick this will result in much smoother, more consistent, motion, without the pauses in response as
the stick crosses each of the independent x and y axis dead zones.

If you're using a single stick to control two different quantities, such as a four wheel robot where you've mapped
acceleration and steering onto a single stick, you probably want to continue to use the individual axes! Experiment and
see which setting feels best for you.

As with other axes and buttons, you can fetch the values of these extra axes in a couple of different ways:

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource

    # Get a joystick
    with ControllerResource() as joystick:
        # Loop until disconnected
        while joystick.connected:
            # Get a corrected tuple of values from the left stick, assign the two values to x and y
            x, y = joystick['l']
            # We can also get values as attributes:
            x, y = joystick.l



Checking for Held Buttons
*************************

You can also check whether a button is currently held, and, if so, how long it's been held for to-date in seconds:

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource

    # Get a joystick
    with ControllerResource() as joystick:
        # Loop until disconnected
        while joystick.connected:
            # Hold times are accessible as attributes on the joystick object, passing a button name
            held = joystick['square']
            # If the button isn't held at the moment this will be None
            if held is not None:
                # If the button was held, this is the number of seconds since it was initially pressed
                print('Square held for {} seconds'.format(held))
            # We can also access directly as an attribute
            circle_held = joystick.circle


Reading multiple Axis or Button Hold values
*******************************************

You can read multiple axis values and button hold times in a single call, simply by passing multiple names into the
call (you can, as the example below shows, query a mix of button hold times and axis values in one call):

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource

    # Get a joystick
    with ControllerResource() as joystick:
        # Loop until disconnected
        while joystick.connected:
            # Get the left x and y axes, and the hold time for the home button. The result is a list, and we can
            # use Python's implicit decomposition to read the values of that list into three variables in one go:
            x, y, hold = joystick['lx','ly','home']


.. _poll-presses-label:

Querying Button Presses
***********************

Another common requirement you'll have will be to find out whether the user pressed a button, even if they're not
currently holding it down. This sounds obvious, but in fact it's slightly more subtle - what you really want to know is
whether the user pressed a button at any point since you last asked this question! That way, even if you don't ask very
often you won't miss button presses and you don't have to worry about the user pressing so fast you can't detect it.

This is therefore a two-part process - you must first tell the controller to read out whether any buttons were pressed,
this actually both returns a :class:`~approxeng.input.ButtonPresses` object, and also stores that object as the :meth:`~approxeng.input.Controller.presses`
property of the controller for later access.

.. note::

    This means the button presses are those buttons which were pressed between the most recent call to :meth:`~approxeng.input.Controller.check_presses`
    and the one before that. Only call :meth:`~approxeng.input.Controller.check_presses` once per loop, before the code you then want to read the presses
    attribute

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource

    # Get a joystick
    with ControllerResource() as joystick:
        # Loop until we're disconnected
        while joystick.connected:
            # This is an instance of approxeng.input.ButtonPresses
            presses = joystick.check_presses()
            if presses['square']
                print('SQUARE pressed since last check')
            # We can also use attributes directly, and get at the presses object from the controller:
            if joystick.presses.circle:
                print('CIRCLE pressed since last check')
            # Or we can use the 'x in y' syntax:
            if 'triangle' in presses:
                print('TRIANGLE pressed since last check')

            # If we had any presses, print the list of pressed buttons by standard name
            if joystick.has_presses:
                print(joystick.presses)


.. _sname-label:

Standard Names
--------------

All the controllers supported by this library are fairly similar - they have two analogue joysticks, a bunch of buttons,
some triggers etc. It would be helpful therefore to be able to make use of one controller type but make it as easy as
possible to use others without substantial code changes in your own code.

To do this the library assigns a standard name, or `sname` to each button and axis on every controller. These are based
loosely on the buttons found on a PS3 controller, at the cost of minor confusion for the XBox users (where, for example,
the `X` button is referred to by the name `square`). As long as you use controls which are common to all three
controllers you should be able to transparently make use of whichever of them is available at the time. You can also
choose to make use of facilities which are only available on specific hardware (such as the analogue triggers on the PS4
and XBoxOne controllers) but you should bear in mind that this will preclude use of a less well equipped controller. Up
to you.

A look at the source for each of the controller subclasses should make it obvious what names are available, but the
standard ones are as follows:

Button Names
************

=============  =============  ===============  =============  =============  ===========  ============
Standard name  PS3            PS4              XBoxOne        Rock Candy     Steam        Wii Pro
-------------  -------------  ---------------  -------------  -------------  -----------  ------------
square         Square         Square           X              4 Dot          X            Y
triangle       Triangle       Triangle         Y              3 Dot          Y            X
circle         Circle         Circle           B              6 Dot          B            A
cross          Cross          Cross            A              5 Dot          A            B
ls             Left Stick     Left Stick       Left Stick     Left Stick     Left Stick   Left Stick
rs             Right Stick    Right Stick      Right Stick    Right Stick    Right Stick  Right Stick
select         Select         Share            View           Select         Left Arrow   Select
start          Start          Options          Menu           Start          Right Arrow  Start
home           PS             PS               XBox           Home           Steam        Home
dleft          DPad Left      DPad Left        DPad Left      DPad Left      DPad Left    DPad Left
dup            DPad Up        DPad Up          DPad Up        DPad Up        DPad Up      DPad Up
dright         DPad Right     DPad Right       DPad Right     DPad Right     DPad Right   DPad Right
ddown          DPad Down      DPad Down        Dpad Down      DPad Down      DPad Down    DPad Down
l1             L1 Trigger     L1 Trigger       LB Trigger     L1 Trigger     LB           L
l2             L2 Trigger     L2 Trigger       LT Trigger     L2 Trigger     ---          LZ
r1             R1 Trigger     R1 Trigger       RB Trigger     R1 Trigger     RB           R
r2             R2 Trigger     R2 Trigger       RT Trigger     R2 Trigger     ---          RZ
ps4_pad        ---            Trackpad         ---            ---            ---          ---
=============  =============  ===============  =============  =============  ===========  ============

...and some more, because we now have too many controllers to fit on one table!

=============  ===========
Standard name  PiHut
-------------  -----------
square         Square
triangle       Triangle
circle         Circle
cross          Cross
ls             Left Stick
rs             Right Stick
select         Select
start          Start
home           Analog
dleft          DPad Left
dup            DPad Up
dright         DPad Right
ddown          DPad Down
l1             L1 Trigger
l2             L2 Trigger
r1             R1 Trigger
r2             R2 Trigger
ps4_pad        ---
=============  ===========

.. note::

    The PiHut controller has a `turbo` button which isn't currently mapped to any button in the API.

.. note::

    The lack of `l2` and `r2` for the Steam controller is because these buttons don't appear as buttons in the
    event stream.

.. note::

    The DualShock4 trackpad now (as of 2.1.0) works as both a button when pressed, and a pair of absolute axes `tx`
    and `ty` representing a single touch point. While the controller supports a pair of touches, the library doesn't!
    The touch coordinates range from -1.0 to 1.0, with positive to the right and forwards when holding the controller.

.. note::

    Yes, the Wii Remote Pro buttons really are that way around. Although it has the same buttons as an XBox controller
    they're in different locations. The standard names are set to prioritise location (and therefore kinetic memory)
    so, for example, the `X` button on the Wii Remote Pro is in the same place as the triangle button on the PS3 and PS4
    so we call it `triangle`, whereas the XBox controller has a `Y` button there instead.

Axis Names
**********

.. note::

    With a new kernel (4.13 upwards, tested with 4.15) the Sony controllers expose their motion events in a way we can
    handle, so I've added pitch and roll for both controllers, and yaw rate for the DS4. There is no absolute yaw value
    available, you'd have to calculate this from the rates (tricky to do with any accuracy). Roll is positive clockwise
    when holding the controller, pitch is positive aiming the front of the controller towards the ceiling. Available
    in 2.1.0 of this library onwards.

=============  =============  ===============  =============  ==========  =============  ==========
Standard name  PS3            PS4              XBoxOne        Rock Candy  Steam          Wii Pro
-------------  -------------  ---------------  -------------  ----------  -------------  ----------
lx             Left X         Left X           Left X         Left X      Left X         Left X
ly             Left Y         Left Y           Left Y         Left Y      Left Y         Left Y
rx             Right X        Right X          Right X        Right X     Right X        Right X
ry             Right Y        Right Y          Right Y        Right Y     Right Y        Right Y
lt             L2 Trigger     L2 Trigger       LT Trigger     ---         Left Trigger   ---
rt             R2 Trigger     R2 Trigger       RT Trigger     ---         Right Trigger  ---
tx             ---            Touch X          ---            ---         ---            ---
ty             ---            Touch Y          ---            ---         ---            ---
pitch          Motion         Motion           ---            ---         ---            ---
roll           Motion         Motion           ---            ---         ---            ---
yaw_rate       ---            Motion           ---            ---         ---            ---
=============  =============  ===============  =============  ==========  =============  ==========

=============  =========  =========
Standard name  PiHut      SF30 Pro
-------------  ---------  ---------
lx             Left X     Left X
ly             Left Y     Left Y
rx             Right X    Right X
ry             Right Y    Right Y
lt             L Trigger  L Trigger
rt             R Trigger  R Trigger
tx             ---        ---
ty             ---        ---
pitch          ---        ---
roll           ---        ---
yaw_rate       ---        ---
=============  =========  =========
