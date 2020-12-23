from approxeng.input import CentredAxis, Controller, Button, TriggerAxis, BinaryAxis

MY_VENDOR_ID = 6473
MY_PRODUCT_ID = 1026

__all__ = ['B07']


class B07(Controller):
    """
    Driver for Beboncool B07 controller
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.0):
        """
        Axis and button definitions for Beboncool B07 driver

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        super(B07, self).__init__(
		controls=[
		        Button("Select", 314, sname='select'),
		        Button("Left Stick", 317, sname='ls'),
		        Button("Right Stick", 318, sname='rs'),
		        Button("Start", 315, sname='start'),
		        Button("L1", 310, sname='l1'),
		        Button("L2", 312, sname='l2'),
		        Button("R1", 311, sname='r1'),
		        Button("R2", 313, sname='r2'),
		        Button("Y", 308, sname='triangle'),
		        Button("B", 305, sname='circle'),
		        Button("A", 304, sname='cross'),
		        Button("X", 307, sname='square'),   
		        Button("N/A", 999, sname='home'),                                     
                        CentredAxis("Left Horizontal", 0, 255, 0, sname='lx'),
		        CentredAxis("Left Vertical", 255, 0, 1, sname='ly'),
                        
                        CentredAxis("Right Horizontal", 0, 255, 2, sname='rx'),
		        CentredAxis("Right Vertical", 255, 0, 3, sname='ry'),	                                                        
                        
                        TriggerAxis("Left Trigger", 0, 255, 10, sname='lt'),
                        TriggerAxis("Right Trigger", 0, 255, 9, sname='rt'),	        
                        
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
        return [(MY_VENDOR_ID, MY_PRODUCT_ID)]

    def __repr__(self):
        return 'Beboncool B07'
