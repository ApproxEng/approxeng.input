triangula.input: PlayStation3 Controller Support
================================================

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

Handling Buttons
----------------

The PS3 controller has a large number of buttons. You can use these in two ways:

Firstly you can register callback functions which will be called whenever a button is pressed. These functions will be
called from the internal thread running in the background, so you'll have to deal with potential synchronisation, but
you get the relative convenience of an asynchronous framework in return. To use this method you need to create a
handler function, then register that function with the :class:`approxeng.input.sixaxis.SixAxis` instance:

.. code-block:: python

    from approxeng.input.sixaxis import SixAxisResource, SixAxis
    # Get a joystick
    with SixAxisResource() as joystick:
        # Create a handler function
        def button_handler(button):
            print 'Button clicked {}'.format(button)
        # Register the handler to the SQUARE button
        joystick.register_button_handler(button_handler, SixAxis.BUTTON_SQUARE)
        # We can also register a handler to multiple buttons in one call
        joystick.register_button_handler(button_handler, [SixAxis.BUTTON_CIRCLE, SixAxis.BUTTON_TRIANGLE])
        while 1:
            # Do stuff here, only register the button handlers once, not in this loop!
            # If the buttons are pressed, your handlers will be called but not from this thread.
            pass

The register_button_handler function actually returns a function which can be called to de-register the handler, you
should do this to stop your handler being called when it's no longer needed.

As you can see, there's quite a lot of thinking required to make button handlers work properly. They may be the right
way to do things (for example, you might want a handler which reset the centre point of the analogue sticks, this would
be best done as a handler because it could be called at any time from anywhere else in your code and you wouldn't have
to worry about it). If, however, you're in a polling loop such as Triangula's task framework or PyGame's event loop you
probably just want to know whether a button was pressed since you last checked.

You can do this with the get_and_clear_button_press_history function. The :class:`approxeng.input.sixaxis.SixAxis` instance
maintains a set of flags, one for each button, indicating whether that button has been pressed. These flags are set
when the button is pressed, and all cleared when the function is called, so in effect a flag will be set if the button
was pressed since the last time you asked. The return value from this function is an integer, which is used in this case
as a bit-field - a binary number where each digit represents whether a single button has been pressed (1) or not (0).
This sounds like it might be hard to use, but actually it's very simple due to Python's bitwise operators (if you're not
familiar with these don't worry, but you should probably go and look them up, they're really useful!).

.. code-block:: python

    from approxeng.input.sixaxis import SixAxisResource, SixAxis
    # Get a joystick as before
    with SixAxisResource() as joystick:
        # No need for any button handlers, go straight into our loop
        while 1:
            buttons_pressed = joystick.get_and_clear_button_press_history()
            if buttons_pressed & 1 << SixAxis.BUTTON_SQUARE:
                print 'SQUARE pressed since last check'

How does this work? Well, SixAxis.SQUARE is actually an integer, in this particular case it's 15. The expression
``1 << SixAxis.BUTTON_SQUARE`` means 'Take the number 1, and then shift its binary representation 15 places to the left
adding zeros as we go' so we end up with 0b1000000000000000. The ``buttons_pressed`` value is a similar looking number,
it has '1' where a button was pressed and '0' where it wasn't. The ``&`` operator is a so called 'bitwise AND', it takes
two numbers and compares their binary representations - if both numbers have a '1' in a column it will put a '1' in the
result, otherwise it puts a '0'. So what this is doing is masking out everything that isn't the BUTTON_SQUARE value, and
then seeing if that particular bit (a binary digit is called a 'bit') is set. Finally, the ``if ...`` statement relies
on the Python behaviour that '0' is False, and anything that isn't '0' is True when using numbers. If this all feels a
bit mysterious, don't worry! You don't need to know it to use this class, but it's all good basic knowledge - probably
worth learning at some point.