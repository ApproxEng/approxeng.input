.. _api_xboxone:

XBox-One S Controller Support
=============================

.. figure:: /images/xbox-one.jpg

    XBox-One S Controller

The XBox One S controller (the most modern, with bluetooth support) can be used without any dongles, but you will have
to change a configuration option in the bluetooth driver. This is done by creating a file in `/etc/modprobe.d/`. The
file can be called anything, you'll need to be root to create it, and must specify a single line. In my case I used

.. code-block:: bash

    tom@Ogre ~ $ sudo nano /etc/modprobe.d/bluetooth.conf

...to create a file, with a single line:

.. code-block:: bash

    options bluetooth disable_ertm=Y

After doing this you'll need to reboot your computer. If you don't perform this step your controller will pair, but will
not stay connected for more than a couple of seconds (if you're using the graphical bluetooth manager you'll see it
connecting and disconnecting forever). There don't appear to be any drawbacks to setting this option, at least none that
I've found in the context of making robots.

Once this is done you should be able to pair with :ref:`bluetooth` as with any normal bluetooth device.

Problems with button mappings
-----------------------------

When you first pair your controller, it may not work! If you're seeing messages about button codes not being recognised,
or buttons are mapping to the wrong controls, you need to un-pair the controller and go through the pairing process
again. We're not sure why, but in three separate cases this has fixed the issue. See
`Issue #17 <https://github.com/ApproxEng/approxeng.input/issues/17>`__ for discussion!

Controller Classes
------------------

.. automodule:: approxeng.input.xboxone
    :members: