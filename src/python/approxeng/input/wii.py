from approxeng.input import Controller, CentredAxis, Button
from approxeng.input.sys import read_power_level, write_led_value

WII_REMOTE_PRO_VENDOR = 1406
WII_REMOTE_PRO_PRODUCT = 816


class WiiRemotePro(Controller):
    """
    Wireless steam controller. Note that you must be running the xbox driver for the steam controller first, otherwise
    this won't pick up any appropriate devices. Once this is running though it works just fine.
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
        super(WiiRemotePro, self).__init__(vendor_id=WII_REMOTE_PRO_VENDOR,
                                           product_id=WII_REMOTE_PRO_PRODUCT,
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
                                               CentredAxis("Left Vertical", -1000, 1000, 1, invert=True,
                                                           sname='ly'),
                                               CentredAxis("Right Horizontal", -1000, 1000, 3, sname='rx'),
                                               CentredAxis("Right Vertical", -1000, 1000, 4, invert=True,
                                                           sname='ry'),
                                           ],
                                           dead_zone=dead_zone,
                                           hot_zone=hot_zone)

    def __repr__(self):
        return 'Nintendo Wii Remote Pro Controller'

    def set_led(self, led_number, led_value):
        """
        Set controller LEDs. The controller has four, labelled, LEDs between the hand grips that can be either
        on or off. The labels are actually slightly raised dimples.

        :param led_number:
            Integer between 1 and 4
        :param led_value:
            Value, set to 0 to turn the LED off, 1 to turn it on
        """
        if 1 > led_number > 4:
            return
        write_led_value(hw_id=self.device_unique_name, led_name='p{}'.format(led_number), value=led_value)

    @property
    def battery_level(self):
        return float(read_power_level(self.device_unique_name)) / 100.0
