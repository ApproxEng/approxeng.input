.. _binding-reference-label:

Binding - approxeng.input.selectbinder
======================================

.. note::

    This replaces the previous approxeng.input.asyncorebinder. The main advantage is that it is compatible with both
    Python 2 and 3, removing the only feature of the library that wasn't working with Python 3, but it's also much
    simpler to use. Where the asyncore binder used device names and paths to try to find an appropriate controller, the
    new code uses vendor and product identifiers - these are much more consistent and are guaranteed to be unique. You
    don't need to care about any of these things though, you just need to know that this new version is much easier to
    use!

The binder provides a bridge between the low level operating system representation of your connected controller and the
high level python classes such as :class:`approxeng.input.dualshock3.DualShock3` which your code uses. The binder starts
a new thread to pull events out of the operating system and update your controller object, this is the bit that means
you don't have to continuously poll the controller, it just updates in the background. It's also the thread which calls
any functions you've bound to buttons as event handlers. You can either manually bind the controller yourself (in which
case you're also responsible for un-binding it after you're done!) or you can use the python 'with' functionality.

To bind a controller manually you'll need both an instance of the controller class, and one or more evdev InputDevice
instances from which events should be extracted. The following code shows use of the 'find_single_controller' function
to make this reasonably easy:

.. code-block:: python

    from approxeng.input.selectbinder import bind_controller
    from approxeng.input.dualshock3 import DualShock3
    from approxeng.input.controllers import find_single_controller

    # Locate a controller, instantiate it, and retrieve the InputDevice devices with which it's associated
    # This will raise IOError if it can't find an appropriate controller
    devices, controller, p = find_single_controller(controller_class = DualShock3)

    unbind_function = bind_controller(devices = devices, controller = controller)
    # At this point the joystick object is bound to the device and will receive updates.
    # .... do stuff ....
    # When we're finished, call the unbind function to free up the resources used by the binder
    unbind_function()



Binding a controller manually works, but there's a simpler way to handle the process (and one which avoids ever having
to worry about explicitly unbinding the controller!):

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource
    from approxeng.input.dualshock3 import DualShock3

    # Locate a controller, instantiate it, and retrieve the InputDevice devices with which it's associated
    # This will raise IOError if it can't find an appropriate controller
    devices, controller, p = find_single_controller(controller_class = DualShock3)

    with ControllerResource(devices = devices, controller = controller) as joystick:
        # .... do stuff, the controller is bound to 'joystick' which is a DualShock3 instance....

On exit from the 'with' block the binder is automatically unbound, this includes cases where we break out of the block
because of exceptions or other error conditions. It's a simpler and more robust way to handle the binding and I suggest
you use it instead of explicitly binding it yourself.

This still requires you to go and find your controller, in most cases you'll only have one controller of a given kind.
There's a shorter form of the resource binding that takes advantage of this case:

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource
    from approxeng.input.dualshock3 import DualShock3

    # Specifying a controller_class here will search for an attached controller of the given kind
    # If one can't be found we'll raise IOError as with the previous code
    with ControllerResource(controller_class = DualShock3) as joystick:
        # .... do stuff, the controller is bound to 'joystick' which is a DualShock3 instance....

This can be made even simpler in the case where you're not bothered about what kind of controller you have, or you
explicitly want to be able to work with one of a range of controllers. Omitting the controller_class argument will bind
to the first controller of any kind that's found! This, along with the use of standardised names for the axes and
buttons on the controllers, means you can create a robot that works with PS3, PS4 or XBoxOne controllers based on what
you have lying around, very handy for those PiWars moments when your controller dies and you need to borrow one from the
next table along...

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource

    # No controller_class is specified, so we look for any joystick from the list we support, and use the first one!
    # If one can't be found we'll raise IOError as with the previous code
    with ControllerResource() as joystick:
        # .... do stuff, the controller is bound to 'joystick' is definitely a subclass of Controller but could be
        # a PS3, PS4, XBoxOne....

.. automodule:: approxeng.input.selectbinder
    :members: