# from approxeng.input import CentredAxis, TriggerAxis, Button, Controller, BinaryAxis
from approxeng.input import Controller, Button, CentredAxis

SWITCH_VENDOR_ID = 1406
SWITCH_L_PRODUCT_ID = 8198


class SwitchJoyCon_L(Controller):
    """
    Nintendo Switch Joycon controller, curently only the Left Controller
	being used in horizontal mote, i.e. a single controller and not paired
	with the righthand controller.
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        """
        Create a new Nintendo Switch Joycon controller instance
		Left hand contorller only

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        """
        super(SwitchJoyCon_L, self).__init__(vendor_id=SWITCH_VENDOR_ID,
                                           product_id=SWITCH_L_PRODUCT_ID,
                                           controls=[
                                               Button("Right", 305, sname="circle"),
                                               Button("Up", 307, sname="triangle"),
                                               Button("Left", 306, sname="square"),
                                               Button("Down", 304, sname="cross"),
                                               Button("Left Stick", 314, sname="ls"),
                                               Button("Home", 317, sname="home"),
                                               Button("Minus", 312, sname="start"),
                                               Button("SL", 308, sname="l1"),
                                               Button("SR", 309, sname="r1"),
                                               CentredAxis("Left Horizontal", -1, 1, 16, sname="lx"),
                                               CentredAxis("Left Vertical", 1, -1, 17, sname="ly")

                                           ],
                                           dead_zone=dead_zone,
                                           hot_zone=hot_zone)

    def __repr__(self):
        return 'Nintendo Switch JoyCon controller'


"""    @property
    def battery_level(self):
        return float(read_power_level(self.device_unique_name)) / 100.0

    def __repr__(self):
        return 'Wireless Microsoft XBox One S controller'
"""
