from approxeng.input import Controller, Button, CentredAxis, TriggerAxis, BinaryAxis

DS4_VENDOR_ID = 1356
DS4_PRODUCT_ID = 2508


class DualShock4(Controller):
    """
    Driver for the Sony PlayStation 4 controller, the DualShock4
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        """
        Create a new DualShock4 driver

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        super(DualShock4, self).__init__(vendor_id=DS4_VENDOR_ID,
                                         product_id=DS4_PRODUCT_ID,
                                         controls=[
                                             Button("Circle", 306, sname='circle'),
                                             Button("Cross", 305, sname='cross'),
                                             Button("Square", 304, sname='square'),
                                             Button("Triangle", 307, sname='triangle'),
                                             Button("Home (PS)", 316, sname='home'),
                                             Button("Share", 312, sname='select'),
                                             Button("Options", 313, sname='start'),
                                             Button("Trackpad", 317, sname='ps4_pad'),
                                             Button("L1", 308, sname='l1'),
                                             Button("R1", 309, sname='r1'),
                                             Button("L2", 310, sname='l2'),
                                             Button("R2", 311, sname='r2'),
                                             Button("Left Stick", 314, sname='ls'),
                                             Button("Right Stick", 315, sname='rs'),
                                             CentredAxis("Left Horizontal", 0, 255, 0, sname='lx'),
                                             CentredAxis("Left Vertical", 0, 255, 1, invert=True, sname='ly'),
                                             CentredAxis("Right Horizontal", 0, 255, 2, sname='rx'),
                                             CentredAxis("Right Vertical", 0, 255, 5, invert=True, sname='ry'),
                                             TriggerAxis("Left Trigger", 0, 255, 3, sname='lt'),
                                             TriggerAxis("Right Trigger", 0, 255, 4, sname='rt'),
                                             BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
                                             BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
                                         ],
                                         dead_zone=dead_zone,
                                         hot_zone=hot_zone)

    def __repr__(self):
        return 'Sony DualShock4 (Playstation 4) controller'
