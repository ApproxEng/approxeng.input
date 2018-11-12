# from approxeng.input import CentredAxis, TriggerAxis, Button, Controller, BinaryAxis
from approxeng.input import Controller, Button, CentredAxis

SWITCH_VENDOR_ID = 1406
SWITCH_R_PRODUCT_ID = 8199


class SwitchJoyCon_R(Controller):
    """
    Nintendo Switch Joycon controller, curently only the Right controller
	being used in horizontal mode, i.e. a single controller and not paired
	with the lefthand controller.
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        """
        Create a new Nintendo Switch Joycon controller instance

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        """
        super(SwitchJoyCon_R, self).__init__(vendor_id=SWITCH_VENDOR_ID,
                                           product_id=SWITCH_R_PRODUCT_ID,
                                           controls=[
                                               Button("X", 305, sname="circle"),
                                               Button("Y", 307, sname="triangle"),
                                               Button("B", 306, sname="square"),
                                               Button("A", 304, sname="cross"),
                                               Button("Left Stick", 315, sname="ls"),
                                               Button("Home", 316, sname="home"),
                                               Button("Plus", 313, sname="start"),
                                               Button("SL", 308, sname="l1"),
                                               Button("SR", 309, sname="r1"),
                                               CentredAxis("Left Horizontal", -1, 1, 16, sname="lx"),
                                               CentredAxis("Left Vertical", 1, -1, 17, sname="ly")
                                           ],
                                           dead_zone=dead_zone,
                                           hot_zone=hot_zone)

    def __repr__(self):
        return 'Nintendo Switch JoyCon controller'


