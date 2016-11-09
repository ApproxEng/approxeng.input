from approxeng.input import CentredAxis, Controller, Button

CONTROLLER_NAMES = ["Sony PLAYSTATION(R)3 Controller", "PLAYSTATION(R)3 Controller"]
"""Names used to find the controller when searching evdev devices
"""


class DualShock3(Controller):
    """
    Driver for the Sony PlayStation 3 controller, the DualShock3

    :ivar approxeng.input.Button BUTTON_CIRCLE: the circle button.
    :ivar approxeng.input.Button BUTTON_CROSS: the cross button.
    :ivar approxeng.input.Button BUTTON_SQUARE: the square button.
    :ivar approxeng.input.Button BUTTON_TRIANGLE: the triangle button.
    :ivar approxeng.input.Button BUTTON_HOME: the home (PS) button.
    :ivar approxeng.input.Button BUTTON_D_UP: the d-pad up button.
    :ivar approxeng.input.Button BUTTON_D_RIGHT: the d-pad right button.
    :ivar approxeng.input.Button BUTTON_D_DOWN: the d-pad down button.
    :ivar approxeng.input.Button BUTTON_D_LEFT: the d-pad left button.
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
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.0):
        """
        Discover and initialise a PS3 SixAxis controller connected to this computer.

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        self.BUTTON_SELECT = Button("Select", 288)
        self.BUTTON_LEFT_STICK = Button("Left Stick", 289)
        self.BUTTON_RIGHT_STICK = Button("Right Stick", 290)
        self.BUTTON_START = Button("Start", 291)
        self.BUTTON_D_UP = Button("D Up", 292)
        self.BUTTON_D_RIGHT = Button("D Right", 293)
        self.BUTTON_D_DOWN = Button("D Down", 294)
        self.BUTTON_D_LEFT = Button("D Left", 295)
        self.BUTTON_L2 = Button("L2", 296)
        self.BUTTON_R2 = Button("R2", 297)
        self.BUTTON_L1 = Button("L1", 298)
        self.BUTTON_R1 = Button("R1", 299)
        self.BUTTON_TRIANGLE = Button("Triangle", 300)
        self.BUTTON_CIRCLE = Button("Circle", 301)
        self.BUTTON_CROSS = Button("Cross", 302)
        self.BUTTON_SQUARE = Button("Square", 303)
        self.BUTTON_HOME = Button("Home (PS)", 704)
        self.AXIS_LEFT_VERTICAL = CentredAxis("Left Vertical", 0, 255, 1, invert=True)
        self.AXIS_RIGHT_VERTICAL = CentredAxis("Right Vertical", 0, 255, 5, invert=True)
        self.AXIS_LEFT_HORIZONTAL = CentredAxis("Left Horizontal", 0, 255, 0, )
        self.AXIS_RIGHT_HORIZONTAL = CentredAxis("Right Horizontal", 0, 255, 2)
        super(DualShock3, self).__init__(name=CONTROLLER_NAMES[0],
                                         axes=[self.AXIS_LEFT_HORIZONTAL, self.AXIS_LEFT_VERTICAL,
                                               self.AXIS_RIGHT_HORIZONTAL,
                                               self.AXIS_RIGHT_VERTICAL],
                                         buttons=[self.BUTTON_SELECT, self.BUTTON_LEFT_STICK, self.BUTTON_RIGHT_STICK,
                                                  self.BUTTON_START, self.BUTTON_D_UP, self.BUTTON_D_RIGHT,
                                                  self.BUTTON_D_DOWN, self.BUTTON_D_LEFT, self.BUTTON_L2,
                                                  self.BUTTON_R2, self.BUTTON_L1, self.BUTTON_R1, self.BUTTON_TRIANGLE,
                                                  self.BUTTON_CROSS, self.BUTTON_SQUARE, self.BUTTON_CIRCLE,
                                                  self.BUTTON_HOME],
                                         dead_zone=dead_zone, hot_zone=hot_zone)
