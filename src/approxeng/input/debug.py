try:
    from evdev import ecodes
except ImportError:
    # Ignore this error, it happens when building the documentation on OSX (as evdev won't build there) but is otherwise
    # not significant. Obviously if it's actually failing to import in real systems that would be a problem!
    print 'Not importing evdev, expected during sphinx generation on OSX'


class DebugController(object):
    """
    Dummy controller implementation which just prints all received events
    """

    def __init__(self, print_axes=True, print_buttons=True):
        self.name = "Debug controller"
        self.print_axes = print_axes
        self.print_buttons = print_buttons
        self.axes = {}

    def handle_evdev_event(self, event):
        """
        Process an event from evdev, using it to update the axis or button information in the controller.

        :param event:
            The evdev event to handle
        """
        if event.type == ecodes.EV_ABS:
            self.axes[event.code] = event.value
            if self.print_axes:
                print "Axis {} value {}".format(event.code, event.value)
        elif event.type == ecodes.EV_KEY:
            if self.print_buttons:
                # Button event
                if event.value == 1:
                    # Button down
                    print "Button {} down".format(event.code)
                elif event.value == 0:
                    # Button up
                    print "Button {} up".format(event.code)
        elif event.type > 0:
            print "Unknown event - {}".format(event)

    def __str__(self):
        return "Joystick event printer"
