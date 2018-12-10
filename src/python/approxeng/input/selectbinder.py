from functools import reduce
from select import select
from threading import Thread

import approxeng.input.sys as sys
from approxeng.input.controllers import *

EV_KEY = 1
EV_ABS = 3


class ControllerResource:
    """
    General resource which binds a controller on entry and unbinds it on exit. Either a device name (or list of names)
    or a path to a device node, typically in /dev/input, can be specified. If neither are supplied, the binding uses
    the name property of the controller object.
    """

    def __init__(self, requirements=None, print_events=False, **kwargs):
        """
        Create a new resource to bind and access one or more controllers. If no additional arguments are supplied this
        will find the first controller of any kind enabled by the library. Otherwise the requirements must be provided
        as a list of ControllerRequirement

        :param requirements:
            A list of ControllerRequirement instances used, in order, to find and bind controllers. If not specified
            this will be equivalent to supplying a single unfiltered requirement and will match the first specified
            controller.
        :param print_events:
            Defaults to False, if set to True then all events picked up by the binder will be printed to stdout. Use
            this when you're trying to figure out what events correspond to what axes and buttons!
        :raises ControllerNotFoundError:
            If a controller class is specified but we can't find a connected instance of the class, or nothing has been
            specified and we can't find any controller at all.
        """

        self.discoveries = find_matching_controllers(requirements, **kwargs)
        self.unbind = None
        self.print_events = print_events

    def __enter__(self):
        """
        Called on entering the resource block, returns the controller passed into the constructor.
        """
        self.unbind = bind_controllers(self.discoveries, print_events=self.print_events)
        if len(self.discoveries) == 1:
            return self.discoveries[0].controller
        else:
            return tuple(discovery.controller for discovery in self.discoveries)

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called on resource exit, unbinds the controller, removing the listening thread.
        """
        self.unbind()


def bind_controllers(discoveries: [ControllerDiscovery], print_events=False):
    """
    Bind a controller or controllers to a set of evdev InputDevice instances, starting a thread to keep those
    controllers in sync with the state of the hardware.
    
    :param discoveries:
        A list of ControllerDiscovery instances specifying the controllers and their associated input devices
    :param print_events:
        Defaults to False, if set to True then all events picked up by this binder will be printed to stdout
    :return: 
        A function which can be used to stop the event reading thread and unbind from the device
    """

    class SelectThread(Thread):
        def __init__(self):
            Thread.__init__(self, name='evdev select thread')
            self.daemon = True
            self.running = True

            self.device_to_controller_discovery = {}
            for discovery in discoveries:
                for d in discovery.devices:
                    self.device_to_controller_discovery[d.fn] = discovery
            self.all_devices = reduce(lambda x, y: x + y, [discovery.devices for discovery in discoveries])

        def run(self):

            for discovery in discoveries:
                discovery.controller.device_unique_name = discovery.name

            while self.running:
                try:
                    r, w, x = select(self.all_devices, [], [], 0.5)
                    for fd in r:
                        active_device = fd
                        controller_discovery = self.device_to_controller_discovery[active_device.fn]
                        controller = controller_discovery.controller
                        controller_devices = controller_discovery.devices
                        prefix = None
                        if controller.node_mappings is not None and len(controller_devices) > 1:
                            try:
                                prefix = controller.node_mappings[active_device.name]
                            except KeyError:
                                pass
                        for event in active_device.read():
                            if print_events:
                                print(event)
                            if event.type == EV_ABS:
                                controller.axes.axis_updated(event, prefix=prefix)
                            elif event.type == EV_KEY:
                                # Button event
                                if event.value == 1:
                                    # Button down
                                    controller.buttons.button_pressed(event.code, prefix=prefix)
                                elif event.value == 0:
                                    # Button up
                                    controller.buttons.button_released(event.code, prefix=prefix)
                except Exception as e:
                    self.stop(e)

        def stop(self, exception=None):

            for discovery in discoveries:
                discovery.controller.device_unique_name = None
                discovery.controller.exception = exception

            self.running = False

    polling_thread = SelectThread()

    # Force an update of the LED and battery system cache
    sys.scan_cache(force_update=True)

    for device in polling_thread.all_devices:
        device.grab()

    def unbind():
        polling_thread.stop()
        for dev in polling_thread.all_devices:
            try:
                dev.ungrab()
            except IOError:
                pass

    polling_thread.start()

    return unbind
