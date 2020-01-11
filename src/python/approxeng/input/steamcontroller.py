from approxeng.input import CentredAxis, TriggerAxis, Button, Controller, BinaryAxis

__all__ = ['SteamController']


class SteamController(Controller):
    """
    Wireless steam controller. Note that you must be running the xbox driver for the steam controller first, otherwise
    this won't pick up any appropriate devices. Once this is running though it works just fine.
    """

    def __init__(self, dead_zone=0.1, hot_zone=0.05):
        """
        Create a new steam controller

        :param float dead_zone:
            Used to set the dead zone for each :class:`~approxeng.input.CentredAxis` and
            :class:`~approxeng.input.TriggerAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`~approxeng.input.CentredAxis` and
            :class:`~approxeng.input.TriggerAxis` in the controller.
        """
        super(SteamController, self).__init__(
            controls=[
                Button("X", 307, sname='square'),
                Button("Y", 308, sname='triangle'),
                Button("B", 305, sname='circle'),
                Button("A", 304, sname='cross'),
                Button("Right Stick", 318, sname='rs'),
                Button("Left Stick", 317, sname='ls'),
                Button("Left", 314, sname='select'),
                Button("Right", 315, sname='start'),
                Button("Steam", 316, sname='home'),
                Button("LB", 310, sname='l1'),
                Button("RB", 311, sname='r1'),
                CentredAxis("Left Horizontal", -32768, 32768, 0, sname='lx'),
                CentredAxis("Left Vertical", 32768, -32768, 1, sname='ly'),
                CentredAxis("Right Horizontal", -32768, 32768, 3, sname='rx'),
                CentredAxis("Right Vertical", 32768, -32768, 4, sname='ry'),
                TriggerAxis("Left Trigger", 0, 255, 2, sname='lt'),
                TriggerAxis("Right Trigger", 0, 255, 5, sname='rt'),
                BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
                BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
            ],
            dead_zone=dead_zone,
            hot_zone=hot_zone)

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x45e, 0x28e)]

    def __repr__(self):
        return 'Valve Steam controller in XBox mode'
