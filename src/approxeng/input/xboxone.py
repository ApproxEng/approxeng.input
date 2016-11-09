from approxeng.input import CentredAxis, TriggerAxis, Button, Controller

CONTROLLER_NAME = "Microsoft X-Box One S pad"
"""Names used to find the controller when searching evdev devices
"""


class XBoxOneSPad(Controller):
    """
    Support for the newer XBox One controllers with Bluetooth radios. Currently doesn't work sensibly with bluetooth,
    we can pair and stay connected as long as ERTM is disabled in the bluetooth stack, but this then ends up with it
    being treated as a mouse and all the axis values are kind of wrong. Works fine when connected over USB, but that's
    obviously not hugely useful at this point.

    http://www.spinics.net/lists/linux-bluetooth/msg68184.html for bluez development thread

    :ivar approxeng.input.Button BUTTON_X: the X button.
    :ivar approxeng.input.Button BUTTON_Y: the Y button.
    :ivar approxeng.input.Button BUTTON_A: the A button.
    :ivar approxeng.input.Button BUTTON_B: the B button.
    :ivar approxeng.input.Button BUTTON_RIGHT_STICK: the right stick click button.
    :ivar approxeng.input.Button BUTTON_LEFT_STICK: the left stick click button.
    :ivar approxeng.input.Button BUTTON_VIEW: the view button.
    :ivar approxeng.input.Button BUTTON_MENU: the menu button.
    :ivar approxeng.input.Button BUTTON_XBOX: the XBox (home) button.
    :ivar approxeng.input.Button BUTTON_LB: the upper left front trigger.
    :ivar approxeng.input.Button BUTTON_RB: the upper right front trigger.
    :ivar approxeng.input.CentredAxis AXIS_LEFT_HORIZONTAL:
        the horizontal axis for the left stick, negative to the left relative to the user.
    :ivar approxeng.input.CentredAxis AXIS_LEFT_VERTICAL:
        the horizontal axis for the left stick, negative when the stick is pulled towards the user.
    :ivar approxeng.input.CentredAxis AXIS_RIGHT_HORIZONTAL:
        the horizontal axis for the right stick, negative to the left relative to the user.
    :ivar approxeng.input.CentredAxis AXIS_RIGHT_VERTICAL:
        the horizontal axis for the right stick, negative when the stick is pulled towards the user.
    :ivar approxeng.input.TriggerAxis AXIS_TRIGGER_LEFT: the left front trigger.
    :ivar approxeng.input.TriggerAxis AXIS_TRIGGER_RIGHT: the right front trigger.
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.0):
        """
        Create a new xbox one s controller instance

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        """
        self.BUTTON_X = Button("X", 307)
        self.BUTTON_Y = Button("Y", 308)
        self.BUTTON_B = Button("B", 305)
        self.BUTTON_A = Button("A", 304)
        self.BUTTON_RIGHT_STICK = Button("Right Stick", 318)
        self.BUTTON_LEFT_STICK = Button("Left Stick", 317)
        self.BUTTON_VIEW = Button("View", 314)
        self.BUTTON_MENU = Button("Menu", 315)
        self.BUTTON_XBOX = Button("XBox", 316)
        self.BUTTON_LB = Button("LB", 310)
        self.BUTTON_RB = Button("RB", 311)
        self.AXIS_LEFT_HORIZONTAL = CentredAxis("Left Horizontal", -32768, 32768, 0)
        self.AXIS_LEFT_VERTICAL = CentredAxis("Left Vertical", -32768, 32768, 1, invert=True)
        self.AXIS_RIGHT_HORIZONTAL = CentredAxis("Right Horizontal", -32768, 32768, 3)
        self.AXIS_RIGHT_VERTICAL = CentredAxis("Right Vertical", -32768, 32768, 4, invert=True)
        self.AXIS_TRIGGER_LEFT = TriggerAxis("Left Trigger", 0, 1023, 2)
        self.AXIS_TRIGGER_RIGHT = TriggerAxis("Right Trigger", 0, 1023, 5)
        super(XBoxOneSPad, self).__init__(name=CONTROLLER_NAME,
                                          axes=[self.AXIS_LEFT_HORIZONTAL, self.AXIS_LEFT_VERTICAL,
                                                self.AXIS_RIGHT_HORIZONTAL, self.AXIS_RIGHT_VERTICAL,
                                                self.AXIS_TRIGGER_LEFT, self.AXIS_TRIGGER_RIGHT],
                                          buttons=[self.BUTTON_X, self.BUTTON_Y, self.BUTTON_B, self.BUTTON_A,
                                                   self.BUTTON_RIGHT_STICK, self.BUTTON_LEFT_STICK, self.BUTTON_VIEW,
                                                   self.BUTTON_MENU, self.BUTTON_XBOX, self.BUTTON_LB, self.BUTTON_RB],
                                          dead_zone=dead_zone, hot_zone=hot_zone)
