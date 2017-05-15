.. _example_failover:

Controller Failover
===================

New in version 1.0.7 is the ability to detect when a controller has disconnected. This means you can write code which will
not only wait for a controller, but will gracefully handle the controller failing (generally from going out of range or
batteries dying!). Because the simplest form of the controller resource or explicit binding will bind to any available
controller, you can easily make your robot able to switch from one controller to another without any extra code. PS4
controller battery dead? No problem, just turn on your spare one, or even your spare XBox1 controller that you had in
your bag for some reason. As long as the controller has been previously paired with the Pi (or other computer) it'll be
possible for your code to find it.

The example below waits for a controller, prints some details about it, then goes into a loop where it prints the values
of any active (non-zero) axes, along with any buttons that are pressed. If you disconnect the controller, the code will
detect this and go back into the search mode. If you then (or previously) pair another controller it'll go back into the
loop, and so on.

.. literalinclude:: ../../../scripts/select_binder_resource_example.py
    :language: python
    :linenos: