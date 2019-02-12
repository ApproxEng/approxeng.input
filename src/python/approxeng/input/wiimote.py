from approxeng.input import Controller, Button, CentredAxis

__all__ = ['WiiMote']


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
        super(WiiMote, self).__init__(
            controls=[
                Button("Nunchuck Z", 309, sname="r1"),
                Button("Nunchuck C", 306, sname="r2"),
                Button("Wiimote A", 304, sname="cross"),
                Button("Wiimote B", 305, sname="circle"),
                Button("Wiimote DUp", 103, sname="dup"),
                Button("Wiimote DDown", 108, sname="ddown"),
                Button("Wiimote DLeft", 105, sname="dleft"),
                Button("Wiimote DRight", 106, sname="dright"),
                Button("Wiimote -", 412, sname="select"),
                Button("Wiimote +", 407, sname="start"),
                Button("Wiimote home", 316, sname="home"),
                Button("Wiimote 1", 257, sname="cross"),
                Button("Wiimote 2", 258, sname="circle"),
                CentredAxis("Wiimote Roll", -100, 100, 3, sname="roll"),
                CentredAxis("Wiimote Pitch", -90, 125, 4, sname="pitch"),
                CentredAxis("Wiimote ???", -90, 125, 5, sname="???"),
                CentredAxis("Nunchuck Y", -100, 100, 17, sname="ry"),
                CentredAxis("Nunchuck X", -100, 100, 16, sname="rx"),
                CentredAxis("Classic lx", -32, 32, 18, sname="lx"),
                CentredAxis("Classic ly", -32, 32, 19, sname="ly"),
                CentredAxis("Classic rx", -32, 32, 20, sname="rx"),
                CentredAxis("Classic ry", -32, 32, 21, sname="ly"),
                Button("Classic x", 307, sname="square"),
                Button("Classic y", 308, sname="triangle"),
                Button("Classic zr", 313, sname="r2"),
                Button("Classic zl", 312, sname="l2"),
            ],
            dead_zone=dead_zone,
            hot_zone=hot_zone)

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x57e, 0x306)]

    def __repr__(self):
        return 'Nintendo WiiMote controller'
