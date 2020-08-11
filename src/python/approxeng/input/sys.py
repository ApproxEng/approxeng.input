import logging
from os import listdir
from typing import Optional

logger = logging.getLogger(name='approxeng.input.sys')

__CACHED_SCAN__ = None


def scan_cache(force_update=False):
    """
    Get the results of a previous scan for LEDs in /sys/class/leds. This will perform a scan if one hasn't been done, or
    if the force_update parameter is set to true, cache the result, and return it.

    :param force_update:
        Set to True to force a re-scan even if there's already cached information
    :return:
        A dict from hardware ID to dicts of LED name to LED write path
    """

    global __CACHED_SCAN__
    if force_update or __CACHED_SCAN__ is None:
        __CACHED_SCAN__ = scan_system()
    return __CACHED_SCAN__


def read_led_value(hw_id, led_name) -> int:
    if hw_id in __CACHED_SCAN__['leds']:
        if led_name in __CACHED_SCAN__['leds'][hw_id]:
            with open(__CACHED_SCAN__['leds'][hw_id][led_name], 'r') as f:
                return int(f.read() or None)
        else:
            logger.debug("No led called {} in {}".format(led_name, hw_id))
    else:
        logger.debug("No hardware ID {} in scan".format(hw_id))


def write_led_value(hw_id, led_name, value):
    if hw_id in __CACHED_SCAN__['leds']:
        if led_name in __CACHED_SCAN__['leds'][hw_id]:
            with open(__CACHED_SCAN__['leds'][hw_id][led_name], 'w') as f:
                f.write(str(int(value)))
        else:
            logger.debug("No led called {} in {}".format(led_name, hw_id))
    else:
        logger.debug("No hardware ID {} in scan".format(hw_id))


def read_power_level(hw_id) -> Optional[float]:
    """
    Power level as a percentage, or None if the device doesn't have a corresponding /sys/power_supply node

    :param hw_id:
        Unique hardware ID
    :return:
        Float 0.0-100.0 percentage of battery capacity, or None if no battery found.
    """
    if hw_id in __CACHED_SCAN__['power']:
        with open(__CACHED_SCAN__['power'][hw_id], 'r') as f:
            return float(f.read() or 0) / 100.0
    else:
        return None


def sys_nodes(hw_id):
    """
    Returns a dict containing known power and LED sys nodes for a given hw_id, used by the 'sys_nodes' property on
    :class:`~approxeng.input.Controller` instances.

    :param hw_id:
        Sensible hardware ID from uevent file path
    :return:
        Dict containing either nothing, or one or both of 'leds' and 'power' keys. Power is a single file path, LEDs
        a dict from LED name to file path.
    """
    info = {}
    if hw_id in __CACHED_SCAN__['power']:
        info['power'] = __CACHED_SCAN__['power'][hw_id]
    if hw_id in __CACHED_SCAN__['leds']:
        info['leds'] = {name: __CACHED_SCAN__['leds'][hw_id][name] for name in __CACHED_SCAN__['leds'][hw_id]}
    return info


def scan_system():
    """
    Scans /sys/class/leds looking for entries, then examining their .../device/uevent file to obtain unique hardware
    IDs corresponding to the associated hardware. This then allows us to associate InputDevice based controllers with
    sets of zero or more LEDs. The result is a dict from hardware address to a dict of name to filename, where the name
    is the name of the LED and the filename is the brightness control to which writing a value changes the LED state.

    At the same time, scans /sys/class/power_supply looking for battery entries and analysing them in the same way.

    Hardware IDs are, in order of preference, the HID_UNIQ address (corresponding to the physical MAC of an attached
    bluetooth or similar HID device), or the PHYS corresponding to other devices. This is the same logic as used in the
    evdev based scanning to group together input nodes for composite controllers (i.e. ones with motion sensors as well
    as physical axes). It is intended to produce the same results, so the LEDs for e.g. a PS4 controller will be keyed
    on the same physical address as that returned by :func:`approxeng.input.controllers.unique_name` for all the
    InputDevice instances associated with a given controller.

    :return:
        A dict containing available LEDs, keyed on physical device ID
    """

    def find_device_hardware_id(uevent_file_path):
        try:
            hid_uniq = None
            phys = None
            for line in open(uevent_file_path, 'r').read().split('\n'):
                parts = line.split('=')
                if len(parts) == 2:
                    name, value = parts
                    value = value.replace('"', '')
                    if name == 'HID_UNIQ' and value:
                        hid_uniq = value
                    elif name == 'PHYS' and value:
                        phys = value.split('/')[0]
            if hid_uniq:
                return hid_uniq
            elif phys:
                return phys
        except FileNotFoundError:
            pass
        return None

    leds = {}
    for sub in ['/sys/class/leds/' + sub_dir for sub_dir in listdir('/sys/class/leds')]:
        led_name = sub.split(':')[-1]
        write_path = sub + '/brightness'
        device_id = find_device_hardware_id(sub + '/device/uevent')
        if device_id:
            if device_id not in leds:
                leds[device_id] = {}
            leds[device_id][led_name] = write_path

    power = {}
    for sub in ['/sys/class/power_supply/' + sub_dir for sub_dir in listdir('/sys/class/power_supply')]:
        # From https://www.kernel.org/doc/Documentation/power/power_supply_class.txt - this is the
        # capacity as a percentage, so will always be an integer in the range 0-100
        read_path = sub + '/capacity'
        device_id = find_device_hardware_id(sub + '/device/uevent')
        if device_id:
            power[device_id] = read_path

    return {'leds': leds,
            'power': power}
