from approxeng.input import Controller

SC_VENDOR_ID = 10462
SC_WIRELESS_PRODUCT_ID = 4418
SC_WIRED_PRODUCT_ID = 4354


class SteamController(Controller):
    """
    Driver for the Steam Controller, Valve's odd hybrid controller thing. Still in progress. Subclasses are used to 
    detect wired and wireless forms of the controller as these appear with different product IDs (the wireless one has
    the product ID of the wireless dongle rather than the controller itself, unlike say the PS4 controller which uses
    the same ID whether communicating over bluetooth or wired connections)
    """

    def __init__(self, product_id, dead_zone=0.05, hot_zone=0.05):
        super(SteamController, self).__init__(vendor_id=SC_VENDOR_ID,
                                              product_id=product_id,
                                              controls=[],
                                              dead_zone=dead_zone,
                                              hot_zone=hot_zone)


class WirelessSteamController(SteamController):
    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        super(WirelessSteamController, self).__init__(product_id=SC_WIRELESS_PRODUCT_ID, dead_zone=dead_zone,
                                                      hot_zone=hot_zone)

    def __repr__(self):
        return 'Wireless Valve Steam controller - not fully supported'


class WiredSteamController(SteamController):
    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        super(WiredSteamController, self).__init__(product_id=SC_WIRED_PRODUCT_ID, dead_zone=dead_zone,
                                                   hot_zone=hot_zone)

    def __repr__(self):
        return 'Wired Valve Steam controller - not fully supported'
