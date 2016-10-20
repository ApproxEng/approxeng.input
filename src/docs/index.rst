Welcome to Approximate Engineering's Python Game Controller Documentation!
==========================================================================

.. note::

    This documentation, and the code it documents, is the original SixAxis controller code from my PiWars_ robot,
    Triangula. I've moved this code in particular out of the main repository because it should be useful in its own
    right, and also because I plan in the long term to add support for other controllers as and when I feel like I need
    them for my own projects!

The code here is intended to run on the Raspberry Pi. It might work on other Linux based systems, but it won't work
on Windows or OSX due to missing underlying support libraries. If you need to handle joysticks on those platforms I
recomment taking a look at PyGame_, which includes joystick support amongst its other functionality.

The controller support code is written in Python. To get the code from
PyPi you can run ``pip install approxeng.input``, although this will only work properly when run on a
Raspberry Pi as it depends on some native libraries which are exclusive to Linux. I haven't tried using it on other
Linux systems.

To work with the code on other platforms you'll want to clone it from GitHub_, it's available under the ASL, the same as
almost everything Python based.

Follow me on twitter (approx_eng_) for updates!

.. toctree::
    :maxdepth: 4
    :glob:

    sixaxis
    api

.. _GitHub: https://github.com/ApproxEng/approxeng.input

.. _PiWars: http://piwars.org

.. _PyGame: http://pygame.org

.. _approx_eng: https://twitter.com/approx_eng