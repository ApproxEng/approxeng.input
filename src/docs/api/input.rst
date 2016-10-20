approxeng.input: General Game Controller Support
================================================

This module contains general support for game controllers. It includes the top level classes such as buttons and
joystick axes which are used for any kind of controller, with sub-modules implementing the specific bits required to
read data from particular controllers. At the present time there's a single implementation which can read from a Sony
Playstation 3 SixAxis controller - it's worth noting that only genuine controllers appear to be supported by the linux
bluetooth stack at this point in time, it's possible that some clones might work but your best bet is to find a genuine
controller.

All controller implementations will make instances of the following classes available. You use these classes to read
data from the controllers:

- :class:`approxeng.input.Axis` represents a single axis of an analogue control. The PS3 implementation provides
  four of these, two for each analogue stick (the tilt sensors aren't supported at the moment). You won't create these,
  they are initialised by the controller implementations.

- :class:`approxeng.input.Button` represents a single button. As with the Axis class you don't create these, instead you
  need to use the instances provided by the implementation packages, i.e. `approxeng.input.sixaxis.BUTTON_CIRCLE`.

- :class:`approxeng.input.Buttons` represents the state of all the buttons on the controller. You'll use the provided
  instance of this class to register button handlers, ask whether any buttons were pressed, and get information about
  how long a button has been held down.

Handling Buttons
----------------

The :class:`approxeng.input.sixaxis.SixAxis` contains a :class:`approxeng.input.Buttons` instance, called, appropriately
enough, 'buttons'. You can use this to see whether buttons are pressed (and how long they've been held, if so), ask
whether buttons were pressed since you last checked, and register event handlers so that any time a button is pressed
some code will be run even if you're not checking.

Handling Button Presses as Events
*********************************

.. code-block:: python

    import approxeng.input.sixaxis
    from approxeng.input.sixaxis import SixAxisResource, SixAxis
    # Get a joystick
    with SixAxisResource() as joystick:
        # Create a handler function
        def button_handler(button):
            print 'Button clicked {}'.format(button)
        # Register the handler to the SQUARE button
        joystick.buttons.register_button_handler(button_handler, sixaxis.BUTTON_SQUARE)
        # We can also register a handler to multiple buttons in one call
        joystick.buttons.register_button_handler(button_handler, [sixaxis.BUTTON_CIRCLE, sixaxis.BUTTON_TRIANGLE])
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

    from approxeng.input.sixaxis import SixAxisResource, BUTTON_SQUARE
    # Get a joystick as before
    with SixAxisResource() as joystick:
        # No need for any button handlers, go straight into our loop
        while 1:
            buttons_pressed = joystick.buttons.get_and_clear_button_press_history()
            if BUTTON_SQUARE in buttons_pressed:
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

    from approxeng.input.sixaxis import SixAxisResource, BUTTON_CIRCLE
    # Get a joystick as before
    with SixAxisResource() as joystick:
        while 1:
            # Get the amount of time the circle button has been held
            held_time = joystick.buttons.is_held(BUTTON_CIRCLE)
            if held_time is not None:
                # If not none, the time will be the number of seconds it's been held. If None the button isn't pressed.
                print "Circle held for {} seconds".format(held_time)

APIs
----

.. autoclass:: approxeng.input.Axis
:members:

.. autoclass:: approxeng.input.Button
:members:

.. autoclass:: approxeng.input.Buttons
:members: