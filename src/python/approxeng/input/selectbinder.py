from select import select
from threading import Thread

from approxeng.input.controllers import find_single_controller, find_any_controller


class ControllerResource:
    """
    General resource which binds a controller on entry and unbinds it on exit. Either a device name (or list of names)
    or a path to a device node, typically in /dev/input, can be specified. If neither are supplied, the binding uses
    the name property of the controller object.
    """

    def __init__(self, controller_class=None, devices=None, controller=None, print_events=False, **kwargs):
        """
        Create a new controller resource. The type of the resource is the controller class, so when used in a with block
        the bound resource will be a controller from which axis and button values can be read. Note - if all of 
        controller_class, devices and controller are None this will attempt to bind to the first controller it can find
        which we support. Use this if you're feeling lazy, or need to be agnostic about what kind of controller your
        code uses. Obviously you'll need to use the standard names for buttons and axes, and make sure you're not
        relying on a particular controller's physical features, but doing this does give you the option to make use of
        any controller you have at the time, whether you developed for that device or not.
        
        :param controller_class: 
            If specified, this class is used to locate the first matching controller of this kind anywhere on the evdev
            bus. If this is not None then devices and controller are ignored, and IOError will be raised if we can't
            find an appropriate controller.
        :param devices: 
            If controller_classes is None, this can be non-None and should contain at least one instance of InputDevice
            to which we should bind to extract evdev events
        :param controller: 
            If controller_classes is None, this can be an instance of Controller to which events can be pushed
        :param print_events:
            Defaults to False, if set to True then all events picked up by the binder will be printed to stdout. Use
            this when you're trying to figure out what events correspond to what axes and buttons!
        :raises IOError:
            If a controller class is specified but we can't find a connected instance of the class, or nothing has been
            specified and we can't find any controller at all.
        :raises ValueError:
            If the controller class is not specified, and we have no devices or controller is None
        """
        if controller_class is not None:
            self.devices, self.controller, physical_address = find_single_controller(controller_class, **kwargs)
        else:
            if devices is None or controller is None or len(devices) == 0:
                self.devices, self.controller, physical_address = find_any_controller(**kwargs)
            else:
                self.devices = devices
                self.controller = controller
        self.unbind = None
        self.print_events = print_events

    def __enter__(self):
        """
        Called on entering the resource block, returns the controller passed into the constructor.
        """
        self.unbind = bind_controller(self.devices, self.controller, print_events=self.print_events)
        return self.controller

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called on resource exit, unbinds the controller, removing the listening thread.
        """
        self.unbind()


def bind_controller(devices, controller, print_events=False):
    """
    Bind a controller to a set of evdev InputDevice instances
    
    :param devices: 
        A list of InputDevice instance which should be polled for events
    :param controller: 
        A Controller instance to which events can be pushed
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
            self.devices = {dev.fd: dev for dev in devices}

        def run(self):
            while self.running:
                r, w, x = select(self.devices, [], [], 0.5)
                for fd in r:
                    for event in self.devices[fd].read():
                        if print_events:
                            print(event)
                        controller.handle_evdev_event(event)

        def stop(self):
            self.running = False

    polling_thread = SelectThread()

    for device in devices:
        device.grab()

    def unbind():
        polling_thread.stop()
        for dev in devices:
            dev.ungrab()

    polling_thread.start()

    return unbind
