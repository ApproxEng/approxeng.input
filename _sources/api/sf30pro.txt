.. _api_sf30pro:

8Bitdo SF30Pro/SN30Pro Controller Support
=========================================

.. figure:: /images/sf30pro.jpg

    The 8Bitdo SF30Pro

Solidly built replica Super Nintendo (SNES) controllers with added thumb sticks and L/R triggers from 8Bitdo_.

Connection
**********

These are bluetooth controllers so no need for a dongle.  Preconfigured for use with Switch, PC, MacOSX and Android with
variations on powering on for different device modes.  The option I have found works most straight froward to pair with is
android mode (start + B) as described here in the manual_.

Tested only with the SF30Pro (hence the component name) though the SN30Pro is exactly the same controller apart from colour so this implementation should work for that too.

Button Names
************

=============  ===========
Standard name  sf30pro
-------------  -----------
square         Y
triangle       X
circle         A
cross          B
ls             Left Stick
rs             Right Stick
select         Select
start          Start
home           mode
dleft          D-Pad Horizontal
dup            D-Pad Vertical
dright         D-Pad Horizontal
ddown          D-Pad Vertical
l1             L1
l2             L2
r1             R1
r2             R2
lt             Left Trigger
rt             Right Trigger
lx             Left Horizontal
rx             Right Horizontal
ly             Left Vertical
ry             Right Vertical
=============  ===========

Supported by code added by Tom Broughton (`\@dpolymath <https://twitter.com/dpolymath>`__).

.. automodule:: approxeng.input.sf30pro
    :members:

.. _8Bitdo: http://www.8bitdo.com/sn30pro-sf30pro/

.. _manual: http://download.8bitdo.com/Manual/Controller/SN30pro+SF30pro/SN30pro+SF30pro_Manual.pdf
