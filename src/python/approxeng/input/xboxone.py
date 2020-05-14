from approxeng.input import CentredAxis, TriggerAxis, Button, Controller, BinaryAxis

__all__ = ['WiredXBoxOnePadJack', 'WiredXBoxOneSPad', 'WirelessXBoxOneSPad']

class WiredXBoxOnePadJack(Controller):
    """
    Wired XBox One controller, version 733 i.e. with headphone jack. It is exactly the same as the Xbox one S though the product ID is different.
    """

    def __init__(self, dead_zone=0.1, hot_zone=0.05):
        """
        Create a new xbox one controller instance Product: 733

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        """
        super(WiredXBoxOnePadJack, self).__init__(
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
                CentredAxis("Left Vertical", -32768, 32768, 1, invert=True, sname='ly'),
                CentredAxis("Right Horizontal", -32768, 32768, 3, sname='rx'),
                CentredAxis("Right Vertical", -32768, 32768, 4, invert=True, sname='ry'),
                TriggerAxis("Left Trigger", 0, 1023, 2, sname='lt', button_sname='l2', button_trigger_value=0.2),
                TriggerAxis("Right Trigger", 0, 1023, 5, sname='rt', button_sname='r2', button_trigger_value=0.2),
                BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
                BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
            ],
            dead_zone=dead_zone,
            hot_zone=hot_zone)

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x45e, 0x2dd)]

    def __repr__(self):
        return 'Wired Microsoft XBox One Jack controller'


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
        super(WiredXBoxOneSPad, self).__init__(
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
                CentredAxis("Left Vertical", 32768, -32768, 1, sname='ly'),
                CentredAxis("Right Horizontal", -32768, 32768, 3, sname='rx'),
                CentredAxis("Right Vertical", 32768, -32768, 4, sname='ry'),
                TriggerAxis("Left Trigger", 0, 1023, 2, sname='lt', button_sname='l2', button_trigger_value=0.2),
                TriggerAxis("Right Trigger", 0, 1023, 5, sname='rt', button_sname='r2', button_trigger_value=0.2),
                BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
                BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
            ],
            dead_zone=dead_zone,
            hot_zone=hot_zone)

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x45e, 0x2ea)]

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
        super(WirelessXBoxOneSPad, self).__init__(
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
                CentredAxis("Left Vertical", 65335, 0, 1, sname='ly'),
                CentredAxis("Right Horizontal", 0, 65335, 3, sname='rx'),
                CentredAxis("Right Vertical", 65335, 0, 4, sname='ry'),
                TriggerAxis("Left Trigger", 0, 1023, 2, sname='lt', button_sname='l2', button_trigger_value=0.1),
                TriggerAxis("Right Trigger", 0, 1023, 5, sname='rt', button_sname='r2', button_trigger_value=0.1),
                BinaryAxis("D-pad Horizontal", 16, b1name='dleft', b2name='dright'),
                BinaryAxis("D-pad Vertical", 17, b1name='dup', b2name='ddown')
            ],
            dead_zone=dead_zone,
            hot_zone=hot_zone)

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x45e, 0x2fd),
                (0x45e, 0x2e0)]

    def __repr__(self):
        return 'Wireless Microsoft XBox One S controller'
