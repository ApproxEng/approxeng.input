.. _binding-reference-label:

Binding - approxeng.input.asyncorebinder
========================================

The binder provides a bridge between the low level operating system representation of your connected controller and the
high level python classes such as :class:`approxeng.input.dualshock3.DualShock3` which your code uses. The binder starts
a new thread to pull events out of the operating system and update your controller object, this is the bit that means
you don't have to continuously poll the controller, it just updates in the background. It's also the thread which calls
any functions you've bound to buttons as event handlers. You can either manually bind the controller yourself (in which
case you're also responsible for un-binding it after you're done!) or you can use the python 'with' functionality.

To bind a controller manually you need code like the following:

.. code-block:: python

    from approxeng.input.asyncorebinder import bind_controller
    from approxeng.input.dualshock3 import DualShock3

    joystick = DualShock3()
    unbind_function = bind_controller(controller=joystick, device_path='/dev/input/event20')
    # At this point the joystick object is bound to the device and will receive updates.
    # .... do stuff ....
    # When we're finished, call the unbind function to free up the resources used by the binder
    unbind_function()

The bind function can be called with either a device path (such as above), or a device name or names. In general the
controller driver modules provide module level names if you're not sure what to use, i.e.

.. code-block:: python

    bind_controller(controller=joystick, device_name=approxeng.input.dualshock3.CONTROLLER_NAMES[0])

Binding a controller manually works, but there's a simpler way to handle the process (and one which avoids ever having
to worry about explicitly unbinding the controller!):

.. code-block:: python

    from approxeng.input.asyncorebinder import ControllerResource
    from approxeng.input.dualshock3 import DualShock3, CONTROLLER_NAMES

    with ControllerResource(DualShock3(), device_name=CONTROLLER_NAMES) as joystick:
        # .... do stuff, the controller is bound to 'joystick' which is a DualShock3 instance....

On exit from the 'with' block the binder is automatically unbound, this includes cases where we break out of the block
because of exceptions or other error conditions. It's a simpler and more robust way to handle the binding and I suggest
you use it instead of explicitly binding it yourself.

.. automodule:: approxeng.input.asyncorebinder
    :members: