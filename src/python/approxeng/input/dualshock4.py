from colorsys import hsv_to_rgb

from approxeng.input import Controller, Button, CentredAxis, TriggerAxis, BinaryAxis

__all__ = ['DualShock4']


# Battery status at /sys/class/power_supply/sony_controller_battery_xx:xx:xx:xx:xx:xx/capacity, where xx:xx... is the
# bluetooth MAC of the controller.


class DualShock4(Controller):
    """
    Driver for the Sony PlayStation 4 controller, the DualShock4
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        """
        Create a new DualShock4 driver

        :param float dead_zone:
            Used to set the dead zone for each :class:`~approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`~approxeng.input.CentredAxis` in the controller.
        """
        super(DualShock4, self).__init__(controls=[
            Button("Circle", 305, sname='circle'),
            Button("Cross", 304, sname='cross'),
            Button("Square", 308, sname='square'),
            Button("Triangle", 307, sname='triangle'),
            Button("Home (PS)", 316, sname='home'),
            Button("Share", 314, sname='select'),
            Button("Options", 315, sname='start'),
            Button("Trackpad", 'touch272', sname='ps4_pad'),
            Button("L1", 310, sname='l1'),
            Button("R1", 311, sname='r1'),
            Button("L2", 312, sname='l2'),
            Button("R2", 313, sname='r2'),
            Button("Left Stick", 317, sname='ls'),
            Button("Right Stick", 318, sname='rs'),
            CentredAxis("Left Horizontal", 0, 255, 0, sname='lx'),
            CentredAxis("Left Vertical", 255, 0, 1, sname='ly'),
            CentredAxis("Right Horizontal", 0, 255, 3, sname='rx'),
            CentredAxis("Right Vertical", 255, 0, 4, sname='ry'),
            TriggerAxis("Left Trigger", 0, 255, 2, sname='lt'),
            TriggerAxis("Right Trigger", 0, 255, 5, sname='rt'),
            BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
            BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown'),
            CentredAxis("Yaw rate", 2097152, -2097152, 'motion4', sname='yaw_rate'),
            CentredAxis("Roll", 8500, -8500, 'motion0', sname='roll'),
            CentredAxis("Pitch", 8500, -8500, 'motion2', sname='pitch'),
            CentredAxis("Touch X", 0, 1920, 'touch53', sname='tx'),
            CentredAxis("Touch Y", 942, 0, 'touch54', sname='ty')

        ],
            node_mappings={
                'Sony Interactive Entertainment Wireless Controller Touchpad': 'touch',
                'Sony Interactive Entertainment Wireless Controller Motion Sensors': 'motion',
                'Wireless Controller Touchpad': 'touch',
                'Wireless Controller Motion Sensors': 'motion'},
            dead_zone=dead_zone,
            hot_zone=hot_zone)
        self.axes['roll'].hot_zone = 0.2
        self.axes['pitch'].hot_zone = 0.2

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x54c, 0x9cc),
                (0x54c, 0x5c4)]

    def __repr__(self) -> str:
        return 'Sony DualShock4 (Playstation 4) controller'

    def set_leds(self, hue: float = 0.0, saturation: float = 1.0, value: float = 1.0):
        """
        The DualShock4 has an LED bar on the front of the controller. This function allows you to set the value of this
        bar. Note that the controller must be connected for this to work, if it's not the call will just be ignored.

        :param hue:
            The hue of the colour, defaults to 0, specified as a floating point value between 0.0 and 1.0.
        :param saturation:
            Saturation of the colour, defaults to 1.0, specified as a floating point value between 0.0 and 1.0.
        :param value:
            Value of the colour (i.e. how bright the light is overall), defaults to 1.0, specified as a floating point
            value between 0.0 and 1.0
        """
        r, g, b = hsv_to_rgb(hue, saturation, value)
        self.write_led_value('red', r * 255.0)
        self.write_led_value('green', g * 255.0)
        self.write_led_value('blue', b * 255.0)
