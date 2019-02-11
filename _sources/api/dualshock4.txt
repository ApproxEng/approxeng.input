.. _api_dualshock4:

PlayStation 4 Controller Support
================================

.. figure:: /images/ps4.jpg

    DualShock4 Controller

Nothing more to do for this controller, it pairs over :ref:`bluetooth` with no issues. This library doesn't provide any
support for the motion sensing, or for the trackpad (other than using it as a button). This is partly because it's the
only controller with those controls, and partly because only some sub-versions of the controller hardware actually work
with the current Linux driver (mine, for example, doesn't).

.. automodule:: approxeng.input.dualshock4
    :members: