# from approxeng.input import CentredAxis, TriggerAxis, Button, Controller, BinaryAxis
from approxeng.input import Controller

SWITCH_VENDOR_ID = 1406
SWITCH_R_PRODUCT_ID = 8199


class SwitchJoyCon_R(Controller):
    """
    Nintendo Switch Joycon controller, curently only the Right controller.
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
                                           controls=[],
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
