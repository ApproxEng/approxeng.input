from approxeng.input import CentredAxis, TriggerAxis, Button, Controller, BinaryAxis

__all__ = ['SteamController']


class SteamController(Controller):
    """
    Wireless steam controller. As of Jan 2021 this works with modern linux installations without
    any messing around, and supports a lot of extra controls as a result!

    The unusual controls are as follows, firstly buttons. Note that both the trackpads have
    touch buttons as well as the click (on the right trackpad) and the d-pad 'buttons' on the
    left one. The controller doesn't have a true d-pad, but you can use the left trackpad in
    place of one (although it's heavy to activate)

    =============  ================
    Standard name  Steam Controller
    -------------  ----------------
    square         X
    triangle       Y
    circle         B
    cross          A
    ls             Left stick click
    rs             Right trackpad click
    rtouch         Right trackpad touch
    select         Left arrow
    start          Right arrow
    home           Steam button
    dleft          DPad left click
    dup            DPad up click
    dright         DPad right click
    ddown          DPad down click
    dtouch         DPad (left trackpad) touch
    l1             Top left trigger
    l2             Middle left trigger
    l3             Base left trigger
    r1             Top right trigger
    r2             Middle right trigger
    r3             Base right trigger
    =============  ================

    The controller has three xy axes with corresponding circular axes as well as analogue
    triggers on the middle trigger buttons:

    =============  ================
    Standard name  Steam Controller
    -------------  ----------------
    lx             Stick horizontal
    ly             Stick vertical
    rx             Right trackpad horizontal
    ry             Right trackpad vertical
    dx             Left trackpad horizontal
    dy             Left trackpad vertical
    lt             Middle left trigger
    rt             Middle right trigger
    =============  ================
    """

    def __init__(self, dead_zone=0.1, hot_zone=0.05, **kwargs):
        super(SteamController, self).__init__(
            controls=[
                Button("X", 307, sname='square'),
                Button("Y", 308, sname='triangle'),
                Button("B", 305, sname='circle'),
                Button("A", 304, sname='cross'),
                Button("Left", 314, sname='select'),
                Button("Right", 315, sname='start'),
                Button("Steam", 316, sname='home'),
                Button("Left Stick Click", 317, sname='ls'),
                Button("Right Trackpad Click", 318, sname='rs'),
                Button("Right Trackpad Touch", 290, sname='rtouch'),
                Button("Left Trackpad Touch", 289, sname='dtouch'),
                Button('Top Left Trigger', 310, sname='l1'),
                Button('Mid Left Trigger', 312, sname='l2'),
                Button('Bottom Left Trigger', 336, sname='l3'),
                Button('Top Right Trigger', 311, sname='r1'),
                Button('Mid Right Trigger', 313, sname='r2'),
                Button('Bottom Right Trigger', 337, sname='r3'),
                Button('D-pad left', 546, sname='dleft'),
                Button('D-pad right', 547, sname='dright'),
                Button('D-pad up', 544, sname='dup'),
                Button('D-pad down', 545, sname='ddown'),
                CentredAxis("Left Stick Horizontal", -32768, 32768, 0, sname='lx'),
                CentredAxis("Left Stick Vertical", 32768, -32768, 1, sname='ly'),
                CentredAxis("Right Trackpad Horizontal", -32768, 32768, 3, sname='rx'),
                CentredAxis("Right Trackpad Vertical", 32768, -32768, 4, sname='ry'),
                CentredAxis("Left Trackpad Horizontal", -32768, 32768, 16, sname='dx'),
                CentredAxis("Left Trackpad Vertical", 32768, -32768, 17, sname='dy'),
                TriggerAxis("Left Trigger", 0, 255, 21, sname='lt'),
                TriggerAxis("Right Trigger", 0, 255, 20, sname='rt')
            ],
            dead_zone=dead_zone,
            hot_zone=hot_zone,
            **kwargs)

    @staticmethod
    def registration_ids():
        return [(10462, 4418)]

    def __repr__(self):
        return 'Valve Steam Controller'
