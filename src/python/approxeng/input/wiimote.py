from approxeng.input import Controller, Button, CentredAxis, TriggerAxis, BinaryAxis

WiiMote_VENDOR_ID = 1406
WiiMote_PRODUCT_ID = 774


class WiiMote(Controller):
    """
    Driver for the Nintendo WiiMote controller, the WiiMote
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.05):
        """
        Create a new WiiMote driver

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        '''
        super(WiiMote, self).__init__(vendor_id=WiiMote_VENDOR_ID,
                                         product_id=WiiMote_PRODUCT_ID,
                                         controls=[
                                         Button("Nunchuck Z", 309, sname="Nunchuk Z"),
                                         Button("Nunchuck C", 306, sname="Nunchik C"),
                                         Button("Wiimote A", 304, sname="Wimote A"),
                                         Button("Wiimote B", 305, sname="Wimmote B"),
                                         Button("Wiimote DUp", 103, sname="Dup"),
                                         Button("Wiimote DDown", 108, sname="DDown"),
                                         Button("Wiimote DLeft", 105, sname="DLeft"),
                                         Button("Wiimote DRight", 106, sname="DRight"),
                                         Button("Wiimote -", 412, sname="-"),
                                         Button("Wiimote +", 407, sname="+"),
                                         Button("Wiimote home", 316, sname="home"),
                                         Button("Wiimote 1", 257, sname="1"),
                                         Button("Wiimote 2", 258, sname="2"),
                                         CentredAxis("Nunchuk 1",0, 255, 3),
                                         CentredAxis("Nunchuk 2",0, 255, 4),
                                         CentredAxis("Nunchuk 3",0, 255, 5),
                                         CentredAxis("Nunchuk Stick X",0, 255, 16),
                                         CentredAxis("Nunchuk 5",0, 255, 17)
                                         					
                                       ],
        '''

        super(WiiMote, self).__init__(vendor_id=WiiMote_VENDOR_ID,
                                         product_id=WiiMote_PRODUCT_ID,
                                         controls=[
                                         Button("Nunchuck Z", 309, sname="Nunchuk Z"),
                                         Button("Nunchuck C", 306, sname="Nunchik C"),
                                         Button("Wiimote A", 304, sname="Wimote A"),
                                         Button("Wiimote B", 305, sname="Wimmote B"),
                                         Button("Wiimote DUp", 103, sname="Dup"),
                                         Button("Wiimote DDown", 108, sname="DDown"),
                                         Button("Wiimote DLeft", 105, sname="DLeft"),
                                         Button("Wiimote DRight", 106, sname="DRight"),
                                         Button("Wiimote -", 412, sname="-"),
                                         Button("Wiimote +", 407, sname="+"),
                                         Button("Wiimote home", 316, sname="home"),
                                         Button("Wiimote 1", 257, sname="1"),
                                         Button("Wiimote 2", 258, sname="2"),
                                         CentredAxis("Wiimote Roll",-100, 100, 3, sname="roll"),
                                         CentredAxis("Wiimote Pitch",-90, 125, 4, sname="pitch"),
                                         CentredAxis("Wiimote ???",-90, 125, 5, sname="???"),
                                         CentredAxis("Nunchuck Y",-100, 100, 17, sname="Nunchuk Y"),
                                         CentredAxis("Nunchuck X",-100, 100, 16, sname="Nunchuk X"),
                                         CentredAxis("Classic lx",-32, 32, 18, sname="classic lx"),
                                         CentredAxis("Classic ly",-32, 32, 19, sname="classic ly"),
                                         CentredAxis("Classic rx",-32, 32, 20, sname="classic rx"),
                                         CentredAxis("Classic ry",-32, 32, 21, sname="classic ly"),
                                         Button("Classic x", 307, sname="classic x"),
                                         Button("Classic y", 308, sname="classic y"),
                                         Button("Classic zr", 313, sname="classic zr"),
                                         Button("Classic zl", 312, sname="classic zl"),
                                   ],

                                         dead_zone=dead_zone,
                                         hot_zone=hot_zone)

    def __repr__(self):
        return 'Nintendo WiiMote controller'
