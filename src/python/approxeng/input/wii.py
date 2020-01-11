from approxeng.input import Controller, CentredAxis, Button

__all__ = ['WiiRemotePro']


class WiiRemotePro(Controller):
    """
    Wireless wi-u-pro controller. This theoretically supports battery and LED control, but for some reason doesn't
    report its hardware ID back to evdev so we can't associate it with nodes in /sys/class/xxx.
    """

    def __init__(self, dead_zone=0.1, hot_zone=0.05):
        """
        Create a new steam controller

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        """
        super(WiiRemotePro, self).__init__(
            controls=[
                Button("X", 307, sname='triangle'),
                Button("Y", 308, sname='square'),
                Button("A", 305, sname='circle'),
                Button("B", 304, sname='cross'),
                Button("Right Stick", 318, sname='rs'),
                Button("Left Stick", 317, sname='ls'),
                Button("Select", 314, sname='select'),
                Button("Start", 315, sname='start'),
                Button("Home", 316, sname='home'),
                Button("L", 310, sname='l1'),
                Button("R", 311, sname='r1'),
                Button("LZ", 312, sname='l2'),
                Button("RZ", 313, sname='r2'),
                Button("D Up", 544, sname='dup'),
                Button("D Right", 547, sname='dright'),
                Button("D Down", 545, sname='ddown'),
                Button("D Left", 546, sname='dleft'),
                CentredAxis("Left Horizontal", -1000, 1000, 0, sname='lx'),
                CentredAxis("Left Vertical", 1000, -1000, 1, sname='ly'),
                CentredAxis("Right Horizontal", -1000, 1000, 3, sname='rx'),
                CentredAxis("Right Vertical", 1000, -1000, 4, sname='ry'),
            ],
            dead_zone=dead_zone,
            hot_zone=hot_zone)

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x57e, 0x330)]

    def __repr__(self):
        return 'Nintendo Wii Remote Pro Controller'
