from asyncore import file_dispatcher, loop
from threading import Thread

try:
    from evdev import InputDevice, list_devices
except ImportError:
    # Ignore this error, it happens when building the documentation on OSX (as evdev won't build there) but is otherwise
    # not significant. Obviously if it's actually failing to import in real systems that would be a problem!
    print 'Not importing evdev, expected during sphinx generation on OSX'


def bind_controller(event_receiver, device_name):
    """
    Connect to the first controller available within /dev/inputX, identifying it by the name supplied.

    This also creates a new thread to run the asyncore loop, and uses a file dispatcher monitoring the corresponding
    device to handle input events. All events are passed to the handle_event function in the parent, this is then
    responsible for interpreting the events and updating any internal state, calling button handlers etc.

    :param event_receiver:
        A class which can receive raw evdev events and interpret them. Typically this will be a controller class
        such as :class:`approxeng.input.sixaxis.SixAxis`. The receiver must implement a 'handle_evdev_event(e)'
        method.
    :param device_name:
        The name of the device to search for in the udev tree.
    :return:
        If a controller was found and connected, this returns a function which will stop and un-bind the event
        polling thread.
    :raises IOError:
        If we didn't already have a controller but couldn't find a new one, this normally means
        there's no controller paired with the Pi
    """
    for device in [InputDevice(fn) for fn in list_devices()]:
        if device.name == device_name:

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
