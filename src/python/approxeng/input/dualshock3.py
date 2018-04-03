from approxeng.input import CentredAxis, Controller, Button, TriggerAxis

DS3_VENDOR_ID = 0x54c
DS3_PRODUCT_ID = 0x268


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
                                             Button("Select", 314, sname='select'),
                                             Button("Left Stick", 317, sname='ls'),
                                             Button("Right Stick", 318, sname='rs'),
                                             Button("Start", 315, sname='start'),
                                             Button("D Up", 544, sname='dup'),
                                             Button("D Right", 547, sname='dright'),
                                             Button("D Down", 545, sname='ddown'),
                                             Button("D Left", 546, sname='dleft'),
                                             Button("L2", 312, sname='l2'),
                                             Button("R2", 313, sname='r2'),
                                             Button("L1", 310, sname='l1'),
                                             Button("R1", 311, sname='r1'),
                                             Button("Triangle", 307, sname='triangle'),
                                             Button("Circle", 305, sname='circle'),
                                             Button("Cross", 304, sname='cross'),
                                             Button("Square", 308, sname='square'),
                                             Button("Home (PS)", 316, sname='home'),
                                             TriggerAxis("Left Trigger", 0, 255, 2, sname='lt'),
                                             TriggerAxis("Right Trigger", 0, 255, 5, sname='rt'),
                                             CentredAxis("Left Vertical", 0, 255, 1, invert=True, sname='ly'),
                                             CentredAxis("Right Vertical", 0, 255, 4, invert=True, sname='ry'),
                                             CentredAxis("Left Horizontal", 0, 255, 0, sname='lx'),
                                             CentredAxis("Right Horizontal", 0, 255, 3, sname='rx'),
                                             CentredAxis("Motion 0", -128, 127, 'motion0', sname='roll', invert=True),
                                             # CentredAxis("Motion 1", -512, 511, 'motion1', sname='m1'),
                                             CentredAxis("Motion 2", -128, 127, 'motion2', sname='pitch', invert=True),
                                         ],
                                         node_mappings={'Sony PLAYSTATION(R)3 Controller Motion Sensors': 'motion'},
                                         dead_zone=dead_zone,
                                         hot_zone=hot_zone)
        self.axes['roll'].hot_zone = 0.2
        self.axes['pitch'].hot_zone = 0.2

    def __repr__(self):
        return 'Sony DualShock3 (Playstation 3) controller'
