from approxeng.input import CentredAxis, TriggerAxis, Button, Controller, BinaryAxis

XB1S_VENDOR_ID = 1118
XB1S_WIRED_PRODUCT_ID = 746
XB1S_WIRELESS_PRODUCT_ID = 736


class WiredXBoxOneSPad(Controller):
    """
    Wired XBox One controller, tested with the newer controllers that use bluetooth and are supplied with the XBox One S
    but may work with older versions. Note that the codes and axis mappings for the wired controller are not the same
    as for the wireless!
    """

    def __init__(self, dead_zone=0.1, hot_zone=0.05):
        """
        Create a new xbox one s controller instance

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        """
        super(WiredXBoxOneSPad, self).__init__(vendor_id=XB1S_VENDOR_ID,
                                               product_id=XB1S_WIRED_PRODUCT_ID,
                                               controls=[
                                                   Button("X", 307, sname='square'),
                                                   Button("Y", 308, sname='triangle'),
                                                   Button("B", 305, sname='circle'),
                                                   Button("A", 304, sname='cross'),
                                                   Button("Right Stick", 318, sname='rs'),
                                                   Button("Left Stick", 317, sname='ls'),
                                                   Button("View", 314, sname='select'),
                                                   Button("Menu", 315, sname='start'),
                                                   Button("XBox", 316, sname='home'),
                                                   Button("LB", 310, sname='l1'),
                                                   Button("RB", 311, sname='r1'),
                                                   CentredAxis("Left Horizontal", -32768, 32768, 0, sname='lx'),
                                                   CentredAxis("Left Vertical", -32768, 32768, 1, invert=True,
                                                               sname='ly'),
                                                   CentredAxis("Right Horizontal", -32768, 32768, 3, sname='rx'),
                                                   CentredAxis("Right Vertical", -32768, 32768, 4, invert=True,
                                                               sname='ry'),
                                                   TriggerAxis("Left Trigger", 0, 1023, 2, sname='lt'),
                                                   TriggerAxis("Right Trigger", 0, 1023, 5, sname='rt'),
                                                   BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
                                                   BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
                                               ],
                                               dead_zone=dead_zone,
                                               hot_zone=hot_zone)

    def __repr__(self):
        return 'Wired Microsoft XBox One S controller'


class WirelessXBoxOneSPad(Controller):
    """
    Wireless over bluetooth - for some reason the control ranges on this are different to when wired and all the buttons
    are different.
    
    To make the wireless pair work with linux you need to set a kernel module option on the bluetooth module. This can
    be done by creating a file in /etc/modprobe.d with the line 'options bluetooth disable_ertm=Y' and rebooting.    
    """

    def __init__(self, dead_zone=0.1, hot_zone=0.05):
        """
        Create a new xbox one s controller instance

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        """
        super(WirelessXBoxOneSPad, self).__init__(vendor_id=XB1S_VENDOR_ID,
                                                  product_id=XB1S_WIRELESS_PRODUCT_ID,
                                                  controls=[
                                                      Button("X", 306, sname='square'),
                                                      Button("Y", 307, sname='triangle'),
                                                      Button("B", 305, sname='circle'),
                                                      Button("A", 304, sname='cross'),
                                                      Button("Right Stick", 313, sname='rs'),
                                                      Button("Left Stick", 312, sname='ls'),
                                                      Button("View", 310, sname='select'),
                                                      Button("Menu", 311, sname='start'),
                                                      Button("XBox", 139, sname='home'),
                                                      Button("LB", 308, sname='l1'),
                                                      Button("RB", 309, sname='r1'),
                                                      CentredAxis("Left Horizontal", 0, 65335, 0, sname='lx'),
                                                      CentredAxis("Left Vertical", 0, 65335, 1, invert=True,
                                                                  sname='ly'),
                                                      CentredAxis("Right Horizontal", 0, 65335, 3, sname='rx'),
                                                      CentredAxis("Right Vertical", 0, 65335, 4, invert=True,
                                                                  sname='ry'),
                                                      TriggerAxis("Left Trigger", 0, 1023, 2, sname='lt'),
                                                      TriggerAxis("Right Trigger", 0, 1023, 5, sname='rt'),
                                                      BinaryAxis("D-pad Horizontal", 16, b1name='dleft',
                                                                 b2name='dright'),
                                                      BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
                                                  ],
                                                  dead_zone=dead_zone,
                                                  hot_zone=hot_zone)

    def __repr__(self):
        return 'Wireless Microsoft XBox One S controller'
