from approxeng.input import CentredAxis, Controller, Button, TriggerAxis

__all__ = ['DualShock3']


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
        super(DualShock3, self).__init__(controls=[
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
            CentredAxis("Left Vertical", 255, 0, 1, sname='ly'),
            CentredAxis("Right Vertical", 255, 0, 4, sname='ry'),
            CentredAxis("Left Horizontal", 0, 255, 0, sname='lx'),
            CentredAxis("Right Horizontal", 0, 255, 3, sname='rx'),
            CentredAxis("Motion 0", 127, -128, 'motion0', sname='roll'),
            CentredAxis("Motion 2", 127, -128, 'motion2', sname='pitch'),
        ],
            node_mappings={'Sony PLAYSTATION(R)3 Controller Motion Sensors': 'motion'},
            dead_zone=dead_zone,
            hot_zone=hot_zone)
        self.axes['roll'].hot_zone = 0.2
        self.axes['pitch'].hot_zone = 0.2

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x54c, 0x268)]

    def __repr__(self):
        return 'Sony DualShock3 (Playstation 3) controller'

    def set_led(self, led_number, led_value):
        """
        Set front-panel controller LEDs. The DS3 controller has four, labelled, LEDs on the front panel that can
        be either on or off.

        :param led_number:
            Integer between 1 and 4
        :param led_value:
            Value, set to 0 to turn the LED off, 1 to turn it on
        """
        if 1 > led_number > 4:
            return
        self.write_led_value(led_name='sony{}'.format(led_number), value=led_value)
