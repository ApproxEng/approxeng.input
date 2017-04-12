from approxeng.input import Controller, Button, CentredAxis, TriggerAxis, BinaryAxis

RC_VENDOR_ID = 3695
RC_PRODUCT_ID = 296


class RockCandy(Controller):
    """
    Driver for the Rock Candy PS3 controller, courtesy of Keith Ellis (keithellis74 on github)
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        """
        Create a new Rock Candy driver

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        super(RockCandy, self).__init__(vendor_id=RC_VENDOR_ID,
                                        product_id=RC_PRODUCT_ID,
                                        controls=[
                                            Button("6 Dot", 306, sname='circle'),
                                            Button("5 Dot", 305, sname='cross'),
                                            Button("4 Dot", 304, sname='square'),
                                            Button("3 Dot", 307, sname='triangle'),
                                            Button("Home", 316, sname='home'),
                                            Button("Select", 312, sname='select'),
                                            Button("Start", 313, sname='start'),
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
                                            BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
                                            BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
                                        ],
                                        dead_zone=dead_zone,
                                        hot_zone=hot_zone)

    def __repr__(self):
        return 'Rock Candy PS3 controller'
