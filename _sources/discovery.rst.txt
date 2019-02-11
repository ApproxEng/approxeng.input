.. _discovery-reference-label:

Controller Discovery - approxeng.input.controllers
==================================================

.. note::
    New in 2.3, the discovery layer tidies up and abstracts the process of finding a controller or controllers matching
    a particular set of requirements. In previous versions you had to handle evdev device nodes directly which wasn't
    particularly friendly, especially as some controllers used multiple OS devices.

.. note::
    If you are using the resource binding via :class:`approxeng.input.selectbinder.ControllerResource` the same classes
    are used within that binding to specify controllers.

Simple discovery
----------------

Before you can use a controller, you need to find it:

.. code-block:: python

    from approxeng.input.controllers import find_matching_controllers

    discoveries = find_matching_controllers()

This is all you need to perform the most basic discovery process, specifically one which will attempt to find a single
connected controller.

Specifying properties
---------------------

You may not want to just pick the first controller available (although the library does attempt to order controllers
such that the first one will be the most capable). You can use the
:class:`approxeng.input.controllers.ControllerRequirement` to specify exactly what you want. At the moment this class
supports two filters:

1. You can specify an exact controller class with 'require_class', such as specifying that you only want a DualShock4
2. You can specify a set of controls on the controller, identified by sname, with 'require_snames' that any controller
   must have to be included in the results. This is great when you know that you need a pair of analogue triggers but
   don't care what exact controller type you get as long as it has them.

.. code-block:: python


    from approxeng.input.controllers import find_matching_controllers, ControllerRequirement

    discoveries = find_matching_controllers(ControllerRequirement(require_snames=['lx','ly']))


Specifying multiple controllers
-------------------------------

Both the above examples return a single controller. This is because they both have a single requirement - when you
don't provide any requirements as in the first example the library treats it as if you'd given it a single requirement
with no filters applied.

The result of the `find_matching_controllers` call is a list of :class:`approxeng.input.controllers.ControllerDiscovery`
objects, each of which contains both the actual controller class and the matching evdev device nodes. In both these
cases this list contains a single item.

To discover multiple controllers, specify multiple requirements when calling:

.. code-block:: python


    from approxeng.input.controllers import find_matching_controllers, ControllerRequirement

    discoveries = find_matching_controllers(ControllerRequirement(require_snames=['lx','ly']),
                                            ControllerRequirement())



The above will attempt to find two controllers. The first one must have the specified axes, the second can be any
connected device. The result will be a two item list, with the controller discoveries in the same order as the supplied
controller requirements.

Discovery failures
------------------

If the system does not have the controllers you've requested, the discovery process will raise a
:class:`approxeng.input.controllers.ControllerNotFoundError`, in general you should catch this and wait before trying
to bind again.