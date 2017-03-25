from approxeng.input import Controller, Button, CentredAxis, TriggerAxis

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
        self.BUTTON_CIRCLE = Button("Circle", 306)
        self.BUTTON_CROSS = Button("Cross", 305)
        self.BUTTON_SQUARE = Button("Square", 304)
        self.BUTTON_TRIANGLE = Button("Triangle", 307)
        self.BUTTON_HOME = Button("Home (PS)", 316)
        self.BUTTON_SHARE = Button("Share", 312)
        self.BUTTON_OPTIONS = Button("Options", 313)
        self.BUTTON_L1 = Button("L1", 308)
        self.BUTTON_R1 = Button("R1", 309)
        self.BUTTON_L2 = Button("L2", 310)
        self.BUTTON_R2 = Button("R2", 311)
        self.BUTTON_LEFT_STICK = Button("Left Stick", 314)
        self.BUTTON_RIGHT_STICK = Button("Right Stick", 315)
        self.AXIS_LEFT_HORIZONTAL = CentredAxis("Left Horizontal", 0, 255, 0)
        self.AXIS_LEFT_VERTICAL = CentredAxis("Left Vertical", 0, 255, 1, invert=True)
        self.AXIS_RIGHT_HORIZONTAL = CentredAxis("Right Horizontal", 0, 255, 2)
        self.AXIS_RIGHT_VERTICAL = CentredAxis("Right Vertical", 0, 255, 5, invert=True)
        self.AXIS_TRIGGER_LEFT = TriggerAxis("Left Trigger", 0, 255, 3)
        self.AXIS_TRIGGER_RIGHT = TriggerAxis("Right Trigger", 0, 255, 4)
        self.AXIS_D_HORIZONTAL = CentredAxis("D-pad Horizontal", -1, 1, 16)
        self.AXIS_D_VERTICAL = CentredAxis("D-pad Vertical", -1, 1, 17, invert=True)
        super(DualShock4, self).__init__(vendor_id=1356,
                                         product_id=2508,
                                         name=CONTROLLER_NAME,
                                         buttons=[self.BUTTON_CIRCLE, self.BUTTON_CROSS, self.BUTTON_SQUARE,
                                                  self.BUTTON_TRIANGLE,
                                                  self.BUTTON_HOME, self.BUTTON_SHARE, self.BUTTON_OPTIONS,
                                                  self.BUTTON_L1, self.BUTTON_R1,
                                                  self.BUTTON_L2, self.BUTTON_R2, self.BUTTON_LEFT_STICK,
                                                  self.BUTTON_RIGHT_STICK],
                                         axes=[self.AXIS_LEFT_HORIZONTAL, self.AXIS_LEFT_VERTICAL,
                                               self.AXIS_RIGHT_VERTICAL,
                                               self.AXIS_RIGHT_HORIZONTAL, self.AXIS_D_HORIZONTAL, self.AXIS_D_VERTICAL,
                                               self.AXIS_TRIGGER_LEFT, self.AXIS_TRIGGER_RIGHT],
                                         dead_zone=dead_zone,
                                         hot_zone=hot_zone)
