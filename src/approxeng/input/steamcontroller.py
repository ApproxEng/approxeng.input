from approxeng.input import Controller

CONTROLLER_NAME = 'Valve Software Steam Controller'
"""Name used to find the controller when searching evdev devices
"""


class SteamController(Controller):
    """
    Driver for the Steam Controller, Valve's odd hybrid controller thing. Still in progress.
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        super(SteamController, self).__init__(vendor_id=10462,
                                              product_id=4418,
                                              name=CONTROLLER_NAME,
                                              axes=[],
                                              buttons=[],
                                              dead_zone=dead_zone,
                                              hot_zone=hot_zone,
                                              print_events=True)
