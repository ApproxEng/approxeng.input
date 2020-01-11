from approxeng.input import Controller, Button, CentredAxis, TriggerAxis, BinaryAxis

__all__ = ['SF30Pro']


class SF30Pro(Controller):
    """
    Driver for the 8BitDo SF30 Pro, courtesy of Tom Brougthon (tabroughton on github)
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        """
        Create a new SF30 Pro driver

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        super(SF30Pro, self).__init__(
            controls=[
                TriggerAxis("Right Trigger", 0, 255, 9, sname='rt'),
                TriggerAxis("Left Trigger", 0, 255, 10, sname='lt'),
                CentredAxis("Right Vertical", 255, 0, 5, sname='ry'),
                CentredAxis("Left Horizontal", 0, 255, 0, sname='lx'),
                CentredAxis("Left Vertical", 255, 0, 1, sname='ly'),
                CentredAxis("Right Horizontal", 0, 255, 2, sname='rx'),
                BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
                BinaryAxis("D-pad Vertical", 17, b1name='ddown', b2name='dup'),
                Button("B", 304, sname='circle'),
                Button("A", 305, sname='cross'),
                Button("Mode", 306, sname='home'),
                Button("X", 307, sname='triangle'),
                Button("Y", 308, sname='square'),
                Button("L1", 310, sname='l1'),
                Button("R1", 311, sname='r1'),
                Button("L2", 312, sname='l2'),
                Button("R2", 313, sname='r2'),
                Button("Select", 314, sname='select'),
                Button("Start", 315, sname='start'),
                Button("Left Stick", 317, sname='ls'),
                Button("Right Stick", 318, sname='rs')
            ],
            dead_zone=dead_zone,
            hot_zone=hot_zone)

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x2dc8, 0x6100)]

    def __repr__(self):
        return '8Bitdo SF30 Pro'
