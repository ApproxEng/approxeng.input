import pprint

try:
    from evdev import InputDevice, list_devices, ecodes, util
except ImportError:
    InputDevice = None
    list_devices = None
    print('Attempt to import evdev failed - if you are not running Sphinx this is a critical error.')

from approxeng.input.dualshock3 import DS3_PRODUCT_ID, DS3_VENDOR_ID, DualShock3
from approxeng.input.dualshock4 import DS4_PRODUCT_ID, DS4_VENDOR_ID, DS4V2_PRODUCT_ID, DualShock4
from approxeng.input.pihut import PH_PRODUCT_ID, PH_VENDOR_ID, PiHut
from approxeng.input.steamcontroller import SC_PRODUCT_ID, SC_VENDOR_ID, SteamController
from approxeng.input.xboxone import XB1S_VENDOR_ID, XB1S_WIRED_PRODUCT_ID, XB1S_WIRELESS_PRODUCT_ID, WiredXBoxOneSPad, \
    WirelessXBoxOneSPad, XB1S_WIRELESS_PRODUCT_ID_2
from approxeng.input.rockcandy import RockCandy, RC_PRODUCT_ID, RC_VENDOR_ID
from approxeng.input.wii import WiiRemotePro, WII_REMOTE_PRO_VENDOR, WII_REMOTE_PRO_PRODUCT
from approxeng.input.wiimote import WiiMote, WIIMOTE_PRODUCT_ID, WIIMOTE_VENDOR_ID
from approxeng.input.sf30pro import SF30Pro, SF30Pro_PRODUCT_ID, SF30Pro_VENDOR_ID

import logzero
import logging

logger = logzero.setup_logger(name='approxeng.input.controllers', level=logging.NOTSET)

# Steam controller works but only when using the xbox userland driver. PS3 and PS4 are fine though, as is the XB1 if on
# a wired connection or after setting the appropriate kernel module options. Rock Candy controller reported as working.
# Support for wiimote contributed by Keith Ellis

CONTROLLERS = [{'constructor': DualShock3, 'vendor_id': DS3_VENDOR_ID, 'product_id': DS3_PRODUCT_ID},
               {'constructor': DualShock4, 'vendor_id': DS4_VENDOR_ID, 'product_id': DS4_PRODUCT_ID},
               {'constructor': DualShock4, 'vendor_id': DS4_VENDOR_ID, 'product_id': DS4V2_PRODUCT_ID},
               {'constructor': PiHut, 'vendor_id': PH_VENDOR_ID, 'product_id': PH_PRODUCT_ID},
               {'constructor': WiredXBoxOneSPad, 'vendor_id': XB1S_VENDOR_ID, 'product_id': XB1S_WIRED_PRODUCT_ID},
               {'constructor': WirelessXBoxOneSPad, 'vendor_id': XB1S_VENDOR_ID,
                'product_id': XB1S_WIRELESS_PRODUCT_ID},
               {'constructor': WirelessXBoxOneSPad, 'vendor_id': XB1S_VENDOR_ID,
                'product_id': XB1S_WIRELESS_PRODUCT_ID_2},
               {'constructor': SteamController, 'vendor_id': SC_VENDOR_ID,
                'product_id': SC_PRODUCT_ID},
               {'constructor': RockCandy, 'vendor_id': RC_VENDOR_ID, 'product_id': RC_PRODUCT_ID},
               {'constructor': WiiRemotePro, 'vendor_id': WII_REMOTE_PRO_VENDOR, 'product_id': WII_REMOTE_PRO_PRODUCT},
               {'constructor': WiiMote, 'vendor_id': WIIMOTE_VENDOR_ID, 'product_id': WIIMOTE_PRODUCT_ID},
               {'constructor': SF30Pro, 'vendor_id': SF30Pro_VENDOR_ID, 'product_id': SF30Pro_PRODUCT_ID}]


def find_any_controller(**kwargs):
    """
    Finds the first controller of any kind and returns the result from find_single_controller. Handy for cases where
    you know (because, say, you've just built a robot) that there's only ever going to be one controller and you're okay
    with that controller being whatever you connect. Because the most modern bits of the API use names which are
    standardised across the supported controllers you should be able to write code that works with any of the fully
    supported devices, so for example you could test with a PS3 controller and reasonably expect it to work with a PS4
    one if that's all you have at the time. For events like PiWars where you might need to borrow a controller from
    another team this could be a good way to go...

    :raises IOError:
        If no suitable controller can be found
    :return:
         A tuple of (devices, controller, physical_location) containing the InputDevice instances used by this
        controller, the instance of the controller class itself and the first part of the input device phys property
    """
    for controller_class in [c['constructor'] for c in CONTROLLERS]:
        logger.debug('Attempting to find controller using driver class {}'.format(controller_class))
        try:
            return find_single_controller(controller_class, **kwargs)
        except IOError:
            pass
    raise IOError('Unable to find any controllers!')


def find_single_controller(controller_class, **kwargs):
    """
    Find the first controller with the specified driver class, raising IOError if we can't find an appropriate connected
    device
    :param controller_class:
        A driver class, i.e. :class:`approxeng.input.dualshock4.DualShock4` - note that you need the class and not an
        instance, so use e.g. find_single_controller(DualShock4) and not find_single_controller(DualShock4())!
    :raises IOError:
        If no suitable controller can be found
    :return:
        A tuple of (devices, controller, physical_location) containing the InputDevice instances used by this
        controller, the instance of the controller class itself and the first part of the input device phys property
    """
    _check_import()
    for controller in find_controllers(**kwargs):
        if isinstance(controller['controller'], controller_class):
            return controller['devices'], controller['controller'], controller['physical_device']
    raise IOError('Unable to find an instance of {}'.format(controller_class))


def find_controllers(**kwargs):
    """
    Scan for and return a list of dicts, one for each detected controller, where the dicts contain 'devices' as the
    sequence of one or more evdev InputDevice instances, 'controller' as the controller instance and 'physical_device'
    as the device component of the InputDevice phys address. This is necessary for controllers like the steam controller
    which can potentially bind to multiple InputDevice instances.
    """
    _check_import()
    result = {}
    for controller in [controller_for_device(InputDevice(fn)) for fn in list_devices()]:
        if controller is not None:
            device = controller['device']
            constructor = controller['constructor']
            physical_device_name = unique_name(device)
            if physical_device_name in result:
                result[physical_device_name]['devices'].append(device)
            else:
                result[physical_device_name] = {'devices': [device],
                                                'controller': constructor(**kwargs),
                                                'physical_device': physical_device_name}
    return list(result.values())


def controller_for_device(device):
    """
    If the evdev InputDevice supplied matches one of our known vendor / product ID pairs, return a dict containing
    'device'->the device, and 'constructor'->the controller class. If no match is found, return None
    """
    _check_import()
    for controller in CONTROLLERS:
        if controller['vendor_id'] == device.info.vendor and controller['product_id'] == device.info.product:
            return {'device': device,
                    'constructor': controller['constructor']}
    return None


def print_devices():
    """
    Simple test function which prints out all devices found by evdev
    """
    _check_import()
    for device in [InputDevice(fn) for fn in list_devices()]:
        if has_abs_axes(device) or has_rel_axes(device):
            pp = pprint.PrettyPrinter(indent=2, width=100)
            pp.pprint(device_verbose_info(device))


def device_verbose_info(device):
    def axis_name(axis_code):
        try:
            return ecodes.ABS[axis_code]
        except KeyError:
            return 'EXTENDED_CODE_{}'.format(axis_code)

    def rel_axis_name(axis_code):
        try:
            return ecodes.REL[axis_code]
        except KeyError:
            return 'EXTENDED_CODE_{}'.format(axis_code)

    axes = None
    if device.capabilities().get(3) is not None:
        axes = {
            axis_name(axis_code): {'code': axis_code, 'min': axis_info.min, 'max': axis_info.max,
                                   'fuzz': axis_info.fuzz,
                                   'flat': axis_info.flat, 'res': axis_info.resolution} for
            axis_code, axis_info in device.capabilities().get(3)}

    rel_axes = None
    if device.capabilities().get(2) is not None:
        print(device.capabilities().get(2))
        rel_axes = {
            axis_name(axis_code): {'code': axis_code} for
            axis_code in device.capabilities().get(2)}

    buttons = None
    if device.capabilities().get(1) is not None:
        buttons = {code: names for (names, code) in
                   dict(util.resolve_ecodes_dict({1: device.capabilities().get(1)})).get(('EV_KEY', 1))}

    return {'fn': device.fn, 'name': device.name, 'phys': device.phys, 'uniq': device.uniq,
            'vendor': device.info.vendor, 'product': device.info.product, 'version': device.info.version,
            'bus': device.info.bustype, 'axes': axes, 'rel_axes': rel_axes, 'buttons': buttons,
            'unique_name': unique_name(device)}


def unique_name(device):
    """
    Construct a unique name for the device based on, in order if available, the uniq ID, the phys ID and
    finally a concatenation of vendor, product and version.

    :param device:
        An InputDevice instance to query
    :return:
        A string containing as unique as possible a name for the physical entity represented by the device
    """
    if device.uniq:
        return device.uniq
    elif device.phys:
        return device.phys.split('/')[0]
    return '{}-{}-{}'.format(device.info.vendor, device.info.product, device.info.version)


def has_abs_axes(device):
    return device.capabilities().get(3) is not None


def has_rel_axes(device):
    return device.capabilities().get(2) is not None


def has_buttons(device):
    return device.capabilities().get(1) is not None


def print_controllers():
    """
    Pretty-print all controllers found
    """
    _check_import()
    pp = pprint.PrettyPrinter(indent=2)
    for controller in find_controllers():
        pp.pprint(controller)


def _check_import():
    """
    Checks whether we imported evdev - it's possible we didn't if we were run as part of a documentation build on a
    system such as OSX which is quite capable of building the docs but can't install evdev. Any attempt to actually
    run this code on such a system should fail as early as possible, we can't fail the import without being unable
    to build docs, but all functions in this module will check to see whether we imported properly and fail if we
    didn't

    :raises ImportError:
    """
    if InputDevice is None:
        raise ImportError('evdev was not imported successfully, nothing will work.')
