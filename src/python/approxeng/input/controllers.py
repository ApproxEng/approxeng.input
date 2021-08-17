try:
    import importlib.resources as resources
except ModuleNotFoundError:
    # Use the backport if on python < 3.7
    import importlib_resources as resources
import logging
import os
import pprint
from functools import total_ordering
from pathlib import Path
from typing import List

import yaml

from approxeng.input.dualshock3 import DualShock3
from approxeng.input.dualshock4 import DualShock4
from approxeng.input.pihut import PiHut
from approxeng.input.profiling import Profile
from approxeng.input.sf30pro import SF30Pro
from approxeng.input.spacemousepro import SpaceMousePro
from approxeng.input.steamcontroller import SteamController
from approxeng.input.switch import SwitchJoyConRight, SwitchJoyConLeft
from approxeng.input.wiimote import WiiMote

# This is used to specify classes to load, as we no longer (as of 2.6.0) do a subclass scan
# Some of these will be replaced in due course with the new profiles, others require more
# controls or are special cases in some way and will remain as custom classes
CUSTOM_CLASSES = [DualShock3, DualShock4, PiHut, SF30Pro, SwitchJoyConLeft, SwitchJoyConRight, WiiMote, SpaceMousePro,
                  SteamController]

try:
    from evdev import InputDevice, list_devices, ecodes, util
except ImportError:
    InputDevice = None
    list_devices = None
    print('Attempt to import evdev failed - if you are not running Sphinx this is a critical error.')

logger = logging.getLogger(name='approxeng.input.controllers')


@total_ordering
class ControllerDiscovery:
    """
    Represents a single discovered controller attached to the host. Ordered, with controllers with more axes and buttons
    being given a higher ordering, and controllers with force feedback higher than those without, then falling back to
    the assigned name.
    """

    def __init__(self, controller_class, controller_constructor_args, devices, name):
        if not isinstance(devices, list):
            self.devices = [devices]
        else:
            self.devices = devices
        self.name = name
        self.ff_device = None
        for device in self.devices:
            if ecodes.EV_FF in device.capabilities():
                self.ff_device = device
                break
        self.controller = controller_class(ff_device=self.ff_device, **controller_constructor_args)

    @property
    def has_ff(self):
        """
        True if there's a force feedback compatible device in this discovery's device list, False otherwise
        """
        return self.ff_device is not None

    def __repr__(self):
        return '{}(devices=[{}], ff={})'.format(self.controller.__class__.__name__,
                                            ','.join(device.fn for device in self.devices), self.has_ff)

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
        if self.has_ff != other.has_ff:
            return (1 if self.has_ff else 0) < (1 if other.has_ff else 0)
        return self.name < other.name


class ControllerRequirement:
    """
    Represents a requirement for a single controller, allowing restriction on type. We might add more filtering options
    later, such as requiring a minimum number of axes, or the presence of a particular control. If you want that now,
    you can subclass this and pass it into the find_matching_controllers and similar functions.
    """

    def __init__(self, require_class=None, require_snames=None, require_ff=False):
        """
        Create a new requirement

        :param require_class:
            If specified, this should be a subclass of :class:`approxeng.input.Controller`, only controllers which match
            this class will be accepted. Defaults to None, accepting any available controller class.
        :param require_snames:
            If specified, this should be a list of strings containing snames of controls (buttons or axes) that must be
            present in the controller. Use this when you know what controls you need but don't mind which controller
            actually implements them.
        :param require_ff:
            If true, requires controllers with at least one force-feedback compatible device node
        """
        self.require_class = require_class
        self.snames = require_snames
        self.require_ff = require_ff

    def accept(self, discovery: ControllerDiscovery):
        """
        Returns True if the supplied ControllerDiscovery matches this requirement, False otherwise
        """
        if self.require_class is not None and not isinstance(discovery.controller, self.require_class):
            return False
        if self.snames is not None:
            all_controls = discovery.controller.buttons.names + discovery.controller.axes.names
            for sname in self.snames:
                if sname not in all_controls:
                    return False
        if self.require_ff and discovery.has_ff is False:
            return False
        return True


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
    return '{}-{}-{}-{}'.format(device.info.vendor, device.info.product, device.info.version, device.path)


def find_matching_controllers(*requirements, **kwargs) -> List[ControllerDiscovery]:
    """
    Find a sequence of controllers which match the supplied requirements, or raise an error if no such controllers
    exist.

    :param requirements:
        Zero or more ControllerRequirement instances defining the requirements for controllers. If no item is passed it
        will be treated as a single requirement with no filters applied and will therefore match the first controller
        found.
    :return:
        A sequence of the same length as the supplied requirements array containing ControllerDiscovery instances which
        match the requirements supplied.
    :raises:
        ControllerNotFoundError if no appropriately matching controllers can be located
    """
    requirements = list(requirements)
    if requirements is None or len(requirements) == 0:
        requirements = [ControllerRequirement()]

    def pop_controller(r: ControllerRequirement, discoveries: List[ControllerDiscovery]) -> ControllerDiscovery:
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


def get_controller_classes(scan_home=True, additional_locations=None):
    """
    Get a map of 'vendor-product' string to controller class. This loads known 'complex' controller classes
    first, then loads simple YAML based ones from within the library, and finally loads from ~/.approxeng_input
    treating this as a directory, iterating over files within it and loading definitions from each. This means that
    users can override controller definitions by putting files in this directory.

    :param scan_home:
        if true, uses ~/.approxeng.input/ as a source for YAML templates, default to True
    :param additional_locations:
        if provided, is interpreted as a list of directory paths which will be scanned in order
        for additional YAML definitions. If this is a single string it will be wrapped automatically in a list
    """

    def built_in_classes():
        for controller_class in CUSTOM_CLASSES:
            for vendor_id, product_id in controller_class.registration_ids():
                yield f'{vendor_id}-{product_id}', controller_class

    def built_in_yaml_definitions():
        package = 'approxeng.input.yaml_controllers'
        for item in resources.contents(package):
            if item.endswith('.yaml') and resources.is_resource(package, item):
                yaml_string = resources.read_text('approxeng.input.yaml_controllers', item)
                profile = Profile(d=yaml.load(yaml_string, Loader=yaml.SafeLoader))
                controller_class = profile.build_controller_class()
                for vendor_id, product_id in controller_class.registration_ids():
                    yield f'{vendor_id}-{product_id}', controller_class

    def yaml_definitions_from_path(path: Path):
        if not path.exists():
            logger.info(f'Creating new definition directory {path}')
            os.makedirs(path)
        elif not Path(path).is_dir():
            logger.error(f'YAML definition path {path} exists, but is a file!')
            return
        for entry in path.glob('*.yaml'):
            if entry.is_file():
                with open(entry, 'r') as file:
                    profile = Profile(d=yaml.load(file, Loader=yaml.SafeLoader))
                    controller_class = profile.build_controller_class()
                    for vendor_id, product_id in controller_class.registration_ids():
                        yield f'{vendor_id}-{product_id}', controller_class

    controllers = {key: value for key, value in built_in_classes()}
    controllers.update({key: value for key, value in built_in_yaml_definitions()})
    if scan_home:
        controllers.update({key: value for key, value in yaml_definitions_from_path(Path.home() / '.approxeng.input')})
    if additional_locations is not None and isinstance(additional_locations, str):
        additional_locations = [additional_locations]
    if additional_locations is not None and isinstance(additional_locations, list):
        for location in additional_locations:
            controllers.update(
                {key: value for key, value in yaml_definitions_from_path(Path(location))})

    return controllers


def find_all_controllers(**kwargs) -> List[ControllerDiscovery]:
    """
    :return:
        A list of :class:`~approxeng.input.controllers.ControllerDiscovery` instances corresponding to controllers
        attached to this host, ordered by the ordering on ControllerDiscovery. Any controllers found will be
        constructed with kwargs passed to their constructor function, particularly useful for dead and hot zone
        parameters.
    """
    id_to_constructor = get_controller_classes()

    def controller_constructor(d: InputDevice):
        id = '{}-{}'.format(d.info.vendor, d.info.product)
        if id in id_to_constructor:
            return id_to_constructor[id]
        logger.info(f'No controller defined for device {d}')
        return None

    all_devices = list(InputDevice(path) for path in list_devices())

    devices_by_name = {name: list(e for e in all_devices if unique_name(e) == name) for name in
                       set(unique_name(e) for e in all_devices if
                           controller_constructor(e) is not None)}

    controllers = sorted(
        ControllerDiscovery(controller_class=controller_constructor(devices[0]), controller_constructor_args=kwargs,
                            devices=devices, name=name) for
        name, devices in devices_by_name.items())

    return controllers


def device_verbose_info(device: InputDevice):
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
            rel_axis_name(axis_code): {'code': axis_code} for
            axis_code in device.capabilities().get(2)}

    buttons = None
    if device.capabilities().get(1) is not None:
        buttons = {code: names for (names, code) in
                   dict(util.resolve_ecodes_dict({1: device.capabilities().get(1)})).get(('EV_KEY', 1))}

    return {'fn': device.fn, 'path': device.path, 'name': device.name, 'phys': device.phys, 'uniq': device.uniq,
            'vendor': device.info.vendor, 'product': device.info.product, 'version': device.info.version,
            'bus': device.info.bustype, 'axes': axes, 'rel_axes': rel_axes, 'buttons': buttons,
            'unique_name': unique_name(device)}


def get_valid_devices():
    def has_abs_axes(device):
        return device.capabilities().get(3) is not None

    def has_rel_axes(device):
        return device.capabilities().get(2) is not None

    _check_import()
    for d in [InputDevice(fn) for fn in list_devices()]:
        if has_abs_axes(d) or has_rel_axes(d):
            yield d


def print_devices():
    """
    Simple test function which prints out all devices found by evdev
    """
    for d in get_valid_devices():
        class MyPrettyPrinter(pprint.PrettyPrinter):
            def format(self, object, context, maxlevels, level):
                if isinstance(object, int):
                    return '0x{:X}'.format(object), True, False
                return super().format(object, context, maxlevels, level)

        pp = MyPrettyPrinter(indent=2, width=100)
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
