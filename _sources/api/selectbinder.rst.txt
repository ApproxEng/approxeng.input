.. _binding-reference-label:

Binding - approxeng.input.selectbinder
======================================

.. note::

    This has been re-written almost entirely in version 2.3. The simplest usage of the controller resource remains
    compatible, but all more sophisticated use will have changed. In general the binder now only handles the binding
    between controllers and the evdev events, leaving all forms of discovery to :ref:`discovery-reference-label`

    A significant change is that you can now bind to and use multiple controllers by simply specifying multiple
    requirements for discovery.

The binder provides a bridge between the low level operating system representation of your connected controller and the
high level python classes such as :class:`approxeng.input.dualshock3.DualShock3` which your code uses. The binder starts
a new thread to pull events out of the operating system and update your controller object, this is the bit that means
you don't have to continuously poll the controller, it just updates in the background. It's also the thread which calls
any functions you've bound to buttons as event handlers. You can either manually bind the controller yourself (in which
case you're also responsible for un-binding it after you're done!) or you can use the python 'with' functionality.

To bind a controller manually you'll need to have already discovered it using the discovery layer. Once you have one
or more instances of :class:`approxeng.input.controllers.ControllerDiscovery` you can bind them manually as follows:

.. code-block:: python

    from approxeng.input.controllers import find_matching_controllers, ControllerRequirement
    from approxeng.input.selectbinder import bind_controllers

    discoveries = find_matching_controllers(ControllerRequirement(require_snames=['lx','ly']))

    unbind_function = bind_controllers(*discoveries)
    # At this point the joystick object is bound to the device and will receive updates. You can get the controller
    # object itself, used to read axes and buttons etc, from the discovery - in this case the discoveries value is a
    # single item list because we only asked for a single controller:
    controller = discoveries[0].controller
    # .... do stuff ....
    # When we're finished, call the unbind function to free up the resources used by the binder
    unbind_function()

Binding a controller manually works, but there's a simpler way to handle the process (and one which avoids ever having
to worry about explicitly unbinding the controller!):

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource
    from approxeng.input.dualshock3 import DualShock3

    with ControllerResource(ControllerRequirement(require_class=DualShock3)) as joystick:
        # .... do stuff, the controller is bound to 'joystick' which is a DualShock3 instance....

On exit from the 'with' block the binder is automatically unbound, this includes cases where we break out of the block
because of exceptions or other error conditions. It's a simpler and more robust way to handle the binding and I suggest
you use it instead of explicitly binding it yourself.

Either form can be used to bind multiple controllers as well. Either by calling `bind_controllers` with more than one
controller discovery, or by specifying multiple controller requirements to the `ControllerResource`:

.. code-block:: python

    from approxeng.input.selectbinder import ControllerResource
    from approxeng.input.dualshock3 import DualShock3

    with ControllerResource(ControllerRequirement(require_class=DualShock3),
                            ControllerRequirement(require_snames=['lx','ly'])) as ds3, joystick:
        # Do stuff, if we didn't raise an error, two controllers are now bound and receiving events.
        # The first controller is a DualShock3, the second is any connected controller with lx and ly
        # controls.

.. automodule:: approxeng.input.selectbinder
    :members:
