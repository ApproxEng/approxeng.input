from approxeng.input import Controller, CentredAxis, Button

__all__ = ['SpaceMousePro']


class SpaceMousePro(Controller):
    """
    Driver for the wired SpaceMouse Pro from 3dConnexion. This controller has a single six-axis puck which can respond
    to motion in all available axes, as well as a set of buttons. Buttons 1-4 seem to act differently to the others,
    they don't generate events on presses consistently so while they do work they should be used with caution. Other
    buttons respond instantly and do the right thing in terms of press detection and hold times. Details of the
    hardware can be found `here <https://www.3dconnexion.co.uk/index.php?id=271>`_

    I've had to largely abandon the normal snames for axes for this controller, it's sufficiently different from all
    the others that there's not really any way to directly substitute it. The puck uses lx and ly for linear X and Y
    movement, but it then also uses lz for up and down, and pitch, roll, and yaw for the rotational axes. As such, it
    will 'just work' if your code only uses the left stick and the motion sensing axes, but there aren't any trigger
    buttons or axes, and there's no right joystick x and y. On the other hand, if you've got one of these you already
    know you'll need to code specifically for it!
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.01):
        super(SpaceMousePro, self).__init__(controls=[
            CentredAxis('X', -350, 350, 0, sname='lx'),
            CentredAxis('Y', 350, -350, 1, sname='ly'),
            CentredAxis('Z', 350, -350, 2, sname='lz'),
            CentredAxis('Roll', -350, 350, 3, sname='pitch'),
            CentredAxis('Pitch', 350, -350, 4, sname='roll'),
            CentredAxis('Yaw', -350, 350, 5, sname='yaw'),
            Button('Menu', 256, sname='menu'),
            Button('Alt', 279, sname='alt'),
            Button('Ctrl', 281, sname='ctrl'),
            Button('Shift', 280, sname='shift'),
            Button('Esc', 278, sname='esc'),
            Button('1', 268, sname='1'),
            Button('2', 269, sname='2'),
            Button('3', 270, sname='3'),
            Button('4', 271, sname='4'),
            Button('Rotate', 264, sname='rotate'),
            Button('T', 258, sname='t'),
            Button('F', 261, sname='f'),
            Button('R', 260, sname='r'),
            Button('Lock', 282, sname='lock'),
            Button('Fit', 257, sname='fit')
        ],
            dead_zone=dead_zone,
            hot_zone=hot_zone)

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x46d, 0xc62b)]
