try:
    from evdev import InputDevice, list_devices, ecodes
except ImportError as e:
    pass

import pprint


def find_device(controller, device_name=None, device_path=None, fail=False):
    """
    Attempt to locate an InputDevice in evdev based on the provided information. If neither device_name nor device_path
    are provided this will use the vendor and product IDs defined by the controller class. If both are provided then the
    first match to either will be returned.

    The first matching device will be returned.

    :param approxeng.input.Controller controller:
        A controller subclass. This is only used if neither device_name nor device_path are specified, in which case the
        controller's vendor and product ID are used to match the device.
    :param device_name:
        A string, or list of strings, which specifies the device name as defined by the evdev library. If provided, the
        first match to this device name will be returned as the InputDevice
    :param device_path:
        An absolute path to a node in the dev filesystem, i.e. '/dev/input/event20' or similar. If provided, the first
        match to this device path will be returned as the InputDevice
    :param fail:
        If set to True, a failure to find a device will raise an IOError rather than returning None.
    :return:
        An :class:`evdev.InputDevice` if one is found which matches the provided information, or None if one can't be
        found. If fail is set to True then an exception is thrown instead if no device can be found.
    :raises IOError:
        If no match could be found in evdev and the fail parameter was True
    """
    if device_name is None and device_path is None:
        device_name = controller.names
    if device_name is not None and isinstance(device_name, basestring):
        device_name = [device_name]
    for device in [InputDevice(fn) for fn in list_devices()]:
        if (device_name is not None and device.name in device_name) \
                or (device_path is not None and device.fn == device_path) \
                or (device_path is None and device_name is None and
                            controller.vendor_id == device.info.vendor and
                            controller.product_id == device.info.product):
            return device
    if fail:
        raise IOError('Unable to find a device with name {} or path {}'.format(device_name, device_path))
    else:
        return None


def print_devices():
    """
    Simple test function which prints out all devices found by evdev
    """
    for device in [InputDevice(fn) for fn in list_devices()]:
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint({'fn': device.fn, 'name': device.name, 'phys': device.phys, 'vendor': device.info.vendor,
                   'product': device.info.product, 'version': device.info.version, 'bus': device.info.bustype})
