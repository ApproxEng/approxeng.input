.. _api_dualshock4:

PlayStation 4 Controller Support
================================

.. figure:: /images/ps4.jpg

    DualShock4 Controller

Nothing more to do for this controller, it pairs over :ref:`bluetooth` with no issues. On modern kernels this now does
support motion events as well as the touchpad, treating the touchpad as a pair of axes reading the last location of a
single touch. See the last part of :ref:`sname-label` for details on how to access these properties.

.. automodule:: approxeng.input.dualshock4
    :members: