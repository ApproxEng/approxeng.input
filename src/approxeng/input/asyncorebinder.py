from asyncore import file_dispatcher, loop
from threading import Thread

try:
    from evdev import InputDevice, list_devices
except ImportError:
    # Ignore this error, it happens when building the documentation on OSX (as evdev won't build there) but is otherwise
    # not significant. Obviously if it's actually failing to import in real systems that would be a problem!
    print 'Not importing evdev, expected during sphinx generation on OSX'


class ControllerResource:
    """
    General resource which binds a controller on entry and unbinds it on exit. Either a device name (or list of names)
    or a path to a device node, typically in /dev/input, can be specified. If neither are supplied, the binding uses
    the name property of the controller object.
    """

    def __init__(self, controller, device_name=None, device_path=None):
        """
        Create a new resource

        :param controller:
            A :class:`approxeng.input.Controller` to bind on entry and unbind on exit.
        :param device_name:
            The name of the device to bind in the device tree, i.e. 'Sony PLAYSTATION(R)3 Controller'
        :param device_path:
            The explicit path of the device to bind in the device tree, i.e. '/dev/input/event22'
        """
        self.controller = controller
        self.device_name = device_name
        self.device_path = device_path

    def __enter__(self):
        """
        Called on entering the resource block, returns the controller passed into the constructor.
        """
        self.unbind = bind_controller(self.controller, device_name=self.device_name, device_path=self.device_path)
        return self.controller

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called on resource exit, unbinds the controller, removing the listening thread.
        """
        self.unbind()


def bind_controller(event_receiver, device_name=None, device_path=None):
    """
    Connect to the first controller available within /dev/inputX, identifying it by the name supplied, or by device
    path. If both path and device name are specified, either will be matched and the first match returned.

    This also creates a new thread to run the asyncore loop, and uses a file dispatcher monitoring the corresponding
    device to handle input events. All events are passed to the handle_event function in the parent, this is then
    responsible for interpreting the events and updating any internal state, calling button handlers etc.

    :param event_receiver:
        A class which can receive raw evdev events and interpret them. Typically this will be a controller class
        such as :class:`approxeng.input.dualshock3.DualShock3`. The receiver must implement a 'handle_evdev_event(e)'
        method.
    :param device_name:
        The name of the device to search for in the udev tree, i.e. 'Microsoft X-Box One S pad'. If this is specified
        the first instance of this controller found will be bound and any subsequent ones ignored. This can be a list,
        in which case the first match of any item in the list will be used.
    :param device_path:
        The absolute path of the device to bind, i.e. /dev/input/event20. If this is specified the exact path will be
        matched, you need to ensure the correct controller class is being used.
    :return:
        If a controller was found and connected, this returns a function which will stop and un-bind the event
        polling thread.
    :raises IOError:
        If we didn't already have a controller but couldn't find a new one, this normally means
        there's no controller paired with the Pi
    """
    if device_name is None and device_path is None:
        device_name = event_receiver.name
    if device_name is not None and isinstance(device_name, basestring):
        device_name = [device_name]
    for device in [InputDevice(fn) for fn in list_devices()]:
        if (device_name is not None and device.name in device_name) or (
                        device_path is not None and device.fn == device_path):

            print "Binding to {} at {}".format(device.name, device.fn)

            class InputDeviceDispatcher(file_dispatcher):
                def __init__(self):
                    self.device = device
                    file_dispatcher.__init__(self, device)

                def recv(self, ign=None):
                    return self.device.read()

                def handle_read(self):
                    for event in self.recv():
                        event_receiver.handle_evdev_event(event)

                def handle_error(self):
                    pass

            class AsyncLoop(Thread):
                def __init__(self, channel):
                    Thread.__init__(self, name='InputDispatchThread[{}]'.format(device_name))
                    self._set_daemon()
                    self.channel = channel

                def run(self):
                    loop()

                def stop(self):
                    self.channel.close()

            loop_thread = AsyncLoop(InputDeviceDispatcher())
            loop_thread.start()
            return loop_thread.stop
    raise IOError('Unable to find a device with name {}.'.format(device_name))
