Change Log
==========

.. note::

    This documentation, and the code it documents, is the original SixAxis controller code from my PiWars_ 2015 robot,
    Triangula. It has subsequently been extensively modified, and now supports the PS4 and XBox One controllers in
    addition to the original support for PS3 controllers.

    A newer version was used for my PiWars_ 2017 entry, this time using a PS4 controller. Several other robots in that
    year also used the library, and my aim is to make this the definitive library for connecting game controllers to
    Python code, especially for robots (but it'll work elsewhere if needed!)

Version 2.0.0
-------------

Simplified API, breaks compatibility with previous versions but allows for more pythonic access via property accessors
and overridden attribute access. The API described at :ref:`simple_api` should now be all you need!

Version 1.0.7
-------------

Added support (pending documentation!) for the WiiMote controller, contributed once again by Keith Ellis! It also adds
controller disconnection detection, enabling :ref:`example_failover` .

Version 1.0.6
-------------

Minor tweak to fix some of the internals

Version 1.0.5
-------------

Added support for the Wii Remote Pro from Nintendo - I'd have added the WiiMote at this point as well but my cheap
clone was dead on arrival...

Version 1.0.4
-------------

Added support for the Steam Controller from Valve, although it needs an extra third party user space driver
(see :ref:`api_steamcontroller`)

Version 1.0.2
-------------

Added support for the Rock Candy PS3 clones thanks to Keith Ellis.

.. _PiWars: http://piwars.org
