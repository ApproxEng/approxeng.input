Welcome to Approximate Engineering's Python Game Controller Documentation!
==========================================================================

.. note::

    This documentation, and the code it documents, is the original SixAxis controller code from my PiWars_ robot,
    Triangula. I've moved this code in particular out of the main repository because it should be useful in its own
    right, and also because I plan in the long term to add support for other controllers as and when I feel like I need
    them for my own projects!

Getting the code
----------------

You can install the code using pip, you'll have to add a few native libraries first though:

.. code-block:: bash

    $ sudo apt-get install python-dev python-pip gcc
    $ pip install approxeng.input

(The exact dependencies may vary depending on your operating system, they come from using evdev and having to compile
that particular python module against whatever underlying libraries your OS is using). I *strongly* recommend using a
virtual environment (virtualenv) so you don't have to install python libraries as root.

.. note::

    The controller support code is written in Python, but relies on some underlying operating system functionality which
    is exclusive to Linux based computers like the Pi. As a result, it won't work on Windows or OSX. If you need to
    handle joysticks on those platforms I recommend taking a look at PyGame_, which includes joystick support amongst
    its other functionality.

To work with the code on other platforms you'll want to clone it from GitHub_, it's available under the ASL, the same as
almost everything Python based. Documentation (this site) is generated using Sphinx.

Follow me on twitter (approx_eng_) for updates!

.. toctree::
    :maxdepth: 4
    :glob:

    howtouse
    dualshock3
    api

.. _GitHub: https://github.com/ApproxEng/approxeng.input

.. _PiWars: http://piwars.org

.. _PyGame: http://pygame.org

.. _approx_eng: https://twitter.com/approx_eng