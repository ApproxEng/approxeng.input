.. _api_steamcontroller:

Steam Controller Support
========================

.. figure:: /images/steam-controller.jpg

    Steam Controller

As of version 2.6.0, the library supports the steam controller natively, meaning you can access all its
controls. While this controller does require a specific USB dongle, unlike most dongle-based controllers
it is able to report disconnections - the device nodes only appear if the controller is turned on.

.. automodule:: approxeng.input.steamcontroller
    :members:
