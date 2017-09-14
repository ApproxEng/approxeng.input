from approxeng.input import CentredAxis, Controller, Button, TriggerAxis, BinaryAxis

PH_VENDOR_ID = 9571
PH_PRODUCT_ID = 1318


class PiHut(Controller):
    """
    Driver for the PiHut PS3-alike controller
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        """
        Discover and initialise a PiHut controller connected to this computer.

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        super(PiHut, self).__init__(vendor_id=PH_VENDOR_ID,
                                    product_id=PH_PRODUCT_ID,
                                    controls=[
                                        Button("Select", 314, sname='select'),
                                        Button("Left Stick", 317, sname='ls'),
                                        Button("Right Stick", 318, sname='rs'),
                                        Button("Start", 315, sname='start'),
                                        Button("L1", 310, sname='l1'),
                                        Button("L2", 312, sname='l2'),
                                        Button("R1", 311, sname='r1'),
                                        Button("R2", 313, sname='r2'),
                                        Button("Triangle", 308, sname='triangle'),
                                        Button("Circle", 305, sname='circle'),
                                        Button("Cross", 304, sname='cross'),
                                        Button("Square", 307, sname='square'),
                                        Button("Analog", 316, sname='home'),
                                        CentredAxis("Left Vertical", 0, 255, 1, invert=True, sname='ly'),
                                        CentredAxis("Right Vertical", 0, 255, 5, invert=True, sname='ry'),
                                        CentredAxis("Left Horizontal", 0, 255, 0, sname='lx'),
                                        CentredAxis("Right Horizontal", 0, 255, 2, sname='rx'),
                                        TriggerAxis("Left Trigger", 0, 255, 9, sname='lt'),
                                        TriggerAxis("Right Trigger", 0, 255, 10, sname='rt'),
                                        BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
                                        BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
                                    ],
                                    dead_zone=dead_zone,
                                    hot_zone=hot_zone)

    def __repr__(self):
        return 'PiHut PS3-alike controller'
