.. _api_wii:

Wii Remote Pro Controller Support
=================================

Version 1.0.5 adds support for the Wii Remote Pro controller - this is the one that looks like a regular game controller
and not the motion sensing wand thing.

.. figure:: /images/wii-pro.jpg

    Wii-Pro Remote

.. _wii-remote-pro-label:

Disabling 'Stick as Mouse' functionality
----------------------------------------

If you pair your Wii Remote Pro controller under Linux within a graphical environment you may find that your mouse
suddenly starts behaving strangely. This is because on modern Linux distributions the system will treat the left stick
on your controller as a mouse. That's quite neat, but probably not what you want. To prevent this happening you need
to create, as root, a file in `xorg.conf.d` - the exact location of this file depends on your distribution, for example
on Linux Mint and Raspbian it's at `/usr/share/X11/xorg.conf.d/`. It'll be there somewhere if it's not there - you might
need to search around a bit to locate it.

You need to create a file in this directory, it can be any name ending with .conf (I use
`50-xorg-no-wiipro-joystick.conf`) with the following contents:

.. code-block:: none

    Section "InputClass"
    Identifier "Nintendo Wii Remote Pro Controller Blacklist"
    MatchProduct "Nintendo Wii Remote Pro Controller"
    MatchDevicePath "/dev/input/event*"
    Option "Ignore" "on"
    EndSection

This will blacklist the controller from acting as an input device for your desktop. If you're using a clone of this
controller rather than the original Nintendo one you may need to change the `MatchProduct` part of the file above to
match whatever's returned by the `approxeng_input_list_devices` command.

