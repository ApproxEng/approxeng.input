from approxeng.input import CentredAxis, Controller, Button

DS3_VENDOR_ID = 1356
DS3_PRODUCT_ID = 616


class DualShock3(Controller):
    """
    Driver for the Sony PlayStation 3 controller, the DualShock3
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.0):
        """
        Discover and initialise a PS3 SixAxis controller connected to this computer.

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        super(DualShock3, self).__init__(vendor_id=DS3_VENDOR_ID,
                                         product_id=DS3_PRODUCT_ID,
                                         controls=[
                                             Button("Select", 288, sname='select'),
                                             Button("Left Stick", 289, sname='ls'),
                                             Button("Right Stick", 290, sname='rs'),
                                             Button("Start", 291, sname='start'),
                                             Button("D Up", 292, sname='dup'),
                                             Button("D Right", 293, sname='dright'),
                                             Button("D Down", 294, sname='ddown'),
                                             Button("D Left", 295, sname='dleft'),
                                             Button("L2", 296, sname='l2'),
                                             Button("R2", 297, sname='r2'),
                                             Button("L1", 298, sname='l1'),
                                             Button("R1", 299, sname='r1'),
                                             Button("Triangle", 300, sname='triangle'),
                                             Button("Circle", 301, sname='circle'),
                                             Button("Cross", 302, sname='cross'),
                                             Button("Square", 303, sname='square'),
                                             Button("Home (PS)", 704, sname='home'),
                                             CentredAxis("Left Vertical", 0, 255, 1, invert=True, sname='ly'),
                                             CentredAxis("Right Vertical", 0, 255, 5, invert=True, sname='ry'),
                                             CentredAxis("Left Horizontal", 0, 255, 0, sname='lx'),
                                             CentredAxis("Right Horizontal", 0, 255, 2, sname='rx')
                                         ],
                                         dead_zone=dead_zone,
                                         hot_zone=hot_zone)

    def __repr__(self):
        return 'Sony DualShock3 (Playstation 3) controller'
