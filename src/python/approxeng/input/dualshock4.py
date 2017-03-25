from approxeng.input import Controller, Button, CentredAxis, TriggerAxis, BinaryAxis

CONTROLLER_NAME = "Wireless Controller"
"""Names used to find the controller when searching evdev devices
"""


class DualShock4(Controller):
    """
    Driver for the Sony PlayStation 4 controller, the DualShock4

    :ivar approxeng.input.Button BUTTON_CIRCLE: the circle button.
    :ivar approxeng.input.Button BUTTON_CROSS: the cross button.
    :ivar approxeng.input.Button BUTTON_SQUARE: the square button.
    :ivar approxeng.input.Button BUTTON_TRIANGLE: the triangle button.
    :ivar approxeng.input.Button BUTTON_HOME: the home (PS) button.
    :ivar approxeng.input.Button BUTTON_SHARE: the share button.
    :ivar approxeng.input.Button BUTTON_OPTIONS: the options button.
    :ivar approxeng.input.Button BUTTON_L1: the upper left front trigger.
    :ivar approxeng.input.Button BUTTON_R1: the upper right front trigger.
    :ivar approxeng.input.Button BUTTON_L2: the lower left front trigger.
    :ivar approxeng.input.Button BUTTON_R2: the lower right front trigger.
    :ivar approxeng.input.Button BUTTON_LEFT_STICK: the left stick click button.
    :ivar approxeng.input.Button BUTTON_RIGHT_STICK: the right stick click button.
    :ivar approxeng.input.CentredAxis AXIS_LEFT_HORIZONTAL:
        the horizontal axis for the left stick, negative to the left relative to the user.
    :ivar approxeng.input.CentredAxis AXIS_LEFT_VERTICAL:
        the horizontal axis for the left stick, negative when the stick is pulled towards the user.
    :ivar approxeng.input.CentredAxis AXIS_RIGHT_HORIZONTAL:
        the horizontal axis for the right stick, negative to the left relative to the user.
    :ivar approxeng.input.CentredAxis AXIS_RIGHT_VERTICAL:
        the horizontal axis for the right stick, negative when the stick is pulled towards the user.
    :ivar approxeng.input.CentredAxis AXIS_D_HORIZONTAL:
        the horizontal part of the d-pad; this isn't a real analogue axis and will only ever report -1.0, 0.0, or 1.0.
    :ivar approxeng.input.CentredAxis AXIS_D_VERTICAL:
        the vertical part of the d-pad; this isn't a real analogue axis and will only ever report -1.0, 0.0, or 1.0.
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        """
        Create a new DualShock4 driver

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        self.BUTTON_CIRCLE = Button("Circle", 306, sname='circle')
        self.BUTTON_CROSS = Button("Cross", 305, sname='cross')
        self.BUTTON_SQUARE = Button("Square", 304, sname='square')
        self.BUTTON_TRIANGLE = Button("Triangle", 307, sname='triangle')
        self.BUTTON_HOME = Button("Home (PS)", 316, sname='home')
        self.BUTTON_SHARE = Button("Share", 312, sname='start')
        self.BUTTON_OPTIONS = Button("Options", 313, sname='select')
        self.BUTTON_L1 = Button("L1", 308, sname='l1')
        self.BUTTON_R1 = Button("R1", 309, sname='r1')
        self.BUTTON_L2 = Button("L2", 310, sname='l2')
        self.BUTTON_R2 = Button("R2", 311, sname='r2')
        self.BUTTON_LEFT_STICK = Button("Left Stick", 314, sname='ls')
        self.BUTTON_RIGHT_STICK = Button("Right Stick", 315, sname='rs')
        self.AXIS_LEFT_HORIZONTAL = CentredAxis("Left Horizontal", 0, 255, 0, sname='lx')
        self.AXIS_LEFT_VERTICAL = CentredAxis("Left Vertical", 0, 255, 1, invert=True, sname='ly')
        self.AXIS_RIGHT_HORIZONTAL = CentredAxis("Right Horizontal", 0, 255, 2, sname='rx')
        self.AXIS_RIGHT_VERTICAL = CentredAxis("Right Vertical", 0, 255, 5, invert=True, sname='ry')
        self.AXIS_TRIGGER_LEFT = TriggerAxis("Left Trigger", 0, 255, 3, sname='lt')
        self.AXIS_TRIGGER_RIGHT = TriggerAxis("Right Trigger", 0, 255, 4, sname='rt')
        self.AXIS_D_HORIZONTAL = BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright')
        self.AXIS_D_VERTICAL = BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
        super(DualShock4, self).__init__(vendor_id=1356,
                                         product_id=2508,
                                         name=CONTROLLER_NAME,
                                         buttons=[self.BUTTON_CIRCLE, self.BUTTON_CROSS, self.BUTTON_SQUARE,
                                                  self.BUTTON_TRIANGLE,
                                                  self.BUTTON_HOME, self.BUTTON_SHARE, self.BUTTON_OPTIONS,
                                                  self.BUTTON_L1, self.BUTTON_R1,
                                                  self.BUTTON_L2, self.BUTTON_R2, self.BUTTON_LEFT_STICK,
                                                  self.BUTTON_RIGHT_STICK, self.AXIS_D_HORIZONTAL,
                                                  self.AXIS_D_VERTICAL],
                                         axes=[self.AXIS_LEFT_HORIZONTAL, self.AXIS_LEFT_VERTICAL,
                                               self.AXIS_RIGHT_VERTICAL, self.AXIS_RIGHT_HORIZONTAL,
                                               self.AXIS_TRIGGER_LEFT, self.AXIS_TRIGGER_RIGHT, self.AXIS_D_VERTICAL,
                                               self.AXIS_D_HORIZONTAL],
                                         dead_zone=dead_zone,
                                         hot_zone=hot_zone)
