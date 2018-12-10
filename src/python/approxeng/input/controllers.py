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
from approxeng.input.switch import SwitchJoyConLeft, SWITCH_VENDOR_ID, SWITCH_L_PRODUCT_ID, SwitchJoyConRight, \
    SWITCH_R_PRODUCT_ID

import logzero
import logging
from functools import total_ordering

logger = logzero.setup_logger(name='approxeng.input.controllers', level=logging.NOTSET)

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
               {'constructor': SF30Pro, 'vendor_id': SF30Pro_VENDOR_ID, 'product_id': SF30Pro_PRODUCT_ID},
               {'constructor': SwitchJoyConLeft, 'vendor_id': SWITCH_VENDOR_ID, 'product_id': SWITCH_L_PRODUCT_ID},
               {'constructor': SwitchJoyConRight, 'vendor_id': SWITCH_VENDOR_ID, 'product_id': SWITCH_R_PRODUCT_ID}]


@total_ordering
class ControllerDiscovery:
    """
    Represents a single discovered controller attached to the host. Ordered, with controllers with more axes and buttons
    being given a higher ordering, then falling back to the assigned name.
    """

    def __init__(self, controller, devices, name):
        self.controller = controller
        if not isinstance(devices, list):
            self.devices = [devices]
        else:
            self.devices = devices
        self.name = name

    def __repr__(self):
        return '{}({})'.format(self.controller.__class__.__name__, ','.join(device.fn for device in self.devices))

    def __eq__(self, other):
        return self.controller.__class__.__name__ == other.controller.__class__.__name__ and self.name == other.name

    def __lt__(self, other):
        self_axes = len(self.controller.axes.names)
        other_axes = len(other.controller.axes.names)
        self_buttons = len(self.controller.buttons.names)
        other_buttons = len(other.controller.buttons.names)
        if self_axes != other_axes:
            return self_axes < other_axes
        elif self_buttons != other_buttons:
            return self_buttons < other_buttons
        return self.name < other.name


class ControllerRequirement:
    """
    Represents a requirement for a single controller, allowing restriction on type. We might add more filtering options
    later, such as requiring a minimum number of axes, or the presence of a particular control. If you want that now,
    you can subclass this and pass it into the find_matching_controllers and similar functions.
    """

    def __init__(self, require_class=None):
        self.require_class = require_class

    def accept(self, discovery: ControllerDiscovery):
        """
        Returns True if the supplied ControllerDiscovery matches this requirement, False otherwise
        """
        if self.require_class is None:
            return True
        elif isinstance(discovery.controller, self.require_class):
            return True
        return False


class ControllerNotFoundError(IOError):
    """
    Raised during controller discovery if the specified set of controller requirements cannot be satisfied
    """
    pass


def unique_name(device: InputDevice) -> str:
    """
    Construct a unique name for the device based on, in order if available, the uniq ID, the phys ID and
    finally a concatenation of vendor, product, version and filename.

    :param device:
        An InputDevice instance to query
    :return:
        A string containing as unique as possible a name for the physical entity represented by the device
    """
    if device.uniq:
        return device.uniq
    elif device.phys:
        return device.phys.split('/')[0]
    return '{}-{}-{}-{}'.format(device.info.vendor, device.info.product, device.info.version, device.fn)


def find_matching_controllers(requirements: [ControllerRequirement] = None, **kwargs) -> [ControllerDiscovery]:
    """
    Find a sequence of controllers which match the supplied requirements, or raise an error if no such controllers
    exist.

    :param requirements:
        A sequence of ControllerRequirement instances defining the requirements for controllers. If a single item is
        passed in it will be treated as a single element list. If no item is passed it will be treated as a single
        requirement with no filters applied and will therefore match the first controller found, this is also the case
        if an empty list is supplied.
    :return:
        A sequence of the same length as the supplied requirements array containing ControllerDiscovery instances which
        match the requirements supplied.
    :raises:
        ControllerNotFoundError if no appropriately matching controllers can be located
    """

    if requirements is None:
        requirements = [ControllerRequirement()]
    elif not isinstance(requirements, list):
        requirements = [requirements]
    if len(requirements) == 0:
        requirements = [ControllerRequirement()]

    def pop_controller(r: ControllerRequirement, discoveries: [ControllerDiscovery]) -> ControllerDiscovery:
        """
        Find a single controller matching the supplied requirement from a list of ControllerDiscovery instances

        :param r:
            The ControllerRequirement to match
        :param discoveries:
            The [ControllerDiscovery] to search
        :return:
            A matching ControllerDiscovery. Modifies the supplied list of discoveries, removing the found item.
        :raises:
            ControllerNotFoundError if no matching controller can be found
        """
        for index, d in enumerate(discoveries):
            if r.accept(d):
                return discoveries.pop(index)
        raise ControllerNotFoundError()

    all_controllers = find_all_controllers(**kwargs)

    try:
        return list(pop_controller(r, all_controllers) for r in requirements)
    except ControllerNotFoundError as exception:
        logger.info('Unable to satisfy controller requirements' +
                    ', required {}, found {}'.format(requirements, find_all_controllers(**kwargs)))
        raise exception


def find_all_controllers(**kwargs) -> [ControllerDiscovery]:
    """
    :return:
        A list of ControllerDiscovery instances corresponding to controllers attached to this host, ordered by the
        ordering on ControllerDiscovery. Any controllers found will be constructed with kwargs passed to their
        constructor function
    """

    id_to_constructor = {'{}-{}'.format(c['vendor_id'], c['product_id']): c['constructor'] for c in CONTROLLERS}

    def controller_constructor(d: InputDevice):
        id = '{}-{}'.format(d.info.vendor, d.info.product)
        if id in id_to_constructor:
            return id_to_constructor[id]
        return None

    all_devices = list(InputDevice(path) for path in list_devices())

    devices_by_name = {name: list(e for e in all_devices if unique_name(e) == name) for name in
                       set(unique_name(e) for e in all_devices if
                           controller_constructor(e) is not None)}

    controllers = sorted(
        ControllerDiscovery(controller=controller_constructor(devices[0])(**kwargs), devices=devices, name=name) for
        name, devices in devices_by_name.items())

    return controllers


def print_devices():
    """
    Simple test function which prints out all devices found by evdev
    """

    def device_verbose_info(device: InputDevice) -> {}:
        """
        Gather and format as much info as possible about the supplied InputDevice. Used mostly for debugging at this point.

        :param device:
            An InputDevice to examine
        :return:
            A dict containing as much information as possible about the input device.
        """

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
        if has_abs_axes(device):
            axes = {
                axis_name(axis_code): {'code': axis_code, 'min': axis_info.min, 'max': axis_info.max,
                                       'fuzz': axis_info.fuzz,
                                       'flat': axis_info.flat, 'res': axis_info.resolution} for
                axis_code, axis_info in device.capabilities().get(3)}

        rel_axes = None
        if has_rel_axes(device):
            print(device.capabilities().get(2))
            rel_axes = {
                rel_axis_name(axis_code): {'code': axis_code} for
                axis_code in device.capabilities().get(2)}

        buttons = None
        if has_buttons(device):
            buttons = {code: names for (names, code) in
                       dict(util.resolve_ecodes_dict({1: device.capabilities().get(1)})).get(('EV_KEY', 1))}

        return {'fn': device.fn, 'name': device.name, 'phys': device.phys, 'uniq': device.uniq,
                'vendor': device.info.vendor, 'product': device.info.product, 'version': device.info.version,
                'bus': device.info.bustype, 'axes': axes, 'rel_axes': rel_axes, 'buttons': buttons,
                'unique_name': unique_name(device)}

    def has_abs_axes(device):
        return device.capabilities().get(3) is not None

    def has_rel_axes(device):
        return device.capabilities().get(2) is not None

    def has_buttons(device):
        return device.capabilities().get(1) is not None

    _check_import()
    for d in [InputDevice(fn) for fn in list_devices()]:
        if has_abs_axes(d) or has_rel_axes(d):
            pp = pprint.PrettyPrinter(indent=2, width=100)
            pp.pprint(device_verbose_info(d))


def print_controllers():
    """
    Pretty-print all controllers found
    """
    _check_import()
    pp = pprint.PrettyPrinter(indent=2)
    for discovery in find_all_controllers():
        pp.pprint(discovery.controller)


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
