import logging
from typing import Tuple, Type, Dict, List, Optional

import yaml

from approxeng.input import Button, Controller, CentredAxis, TriggerAxis, BinaryAxis

__all__ = ['create_controller_class_from_yaml']

LOGGER = logging.getLogger(name=__name__)

SEPARATOR = ':'

CLASS_CREATION_COUNT = 0


def create_controller_class_from_yaml(filename: str, register=False) -> Tuple[str, Type]:
    """
    Load a config from a YAML file, and use it to dynamically create a new subclass of
    :class:`~approxeng.input.Controller`. This new class will be immediately available for
    use elsewhere in the library, in particular it will be picked up when searching for
    matching controllers to use.

    :param filename:
        filename of a YAML file to load
    :param register:
        if True, registers the newly created class within this module's namespace. The
        resultant class name, which can be referenced and used as any regular class, will be
        `approxeng.input.dynamic.NAME` where NAME is the name specified in the YAML input.
        Defaults to False.
    :return:
        A pair of (name, class)
    """
    return create_controller_class_from_dict(_load_yaml(filename), register=register)


def create_controller_class_from_dict(config: Dict, register=False) -> Tuple[str, Type]:
    """
    Load a config from a YAML file, and use it to dynamically create a new subclass of
    :class:`~approxeng.input.Controller`. This new class will be immediately available for
    use elsewhere in the library, in particular it will be picked up when searching for
    matching controllers to use.

    :param config:
        a dict containing configuration, typically loaded from a YAML file
    :param register:
        if True, registers the newly created class within this module's namespace. The
        resultant class name, which can be referenced and used as any regular class, will be
        `approxeng.input.dynamic.NAME` where NAME is the name specified in the YAML input.
        Defaults to False.
    :return:
        A pair of (name, class)
    """

    # Constructor function to use for the newly generated class
    def constructor(self, dead_zone=0.1, hot_zone=0.1):
        Controller.__init__(self,
                            controls=_parse_buttons(config) +
                                     _parse_centred_axes(config) +
                                     _parse_binary_axes(config) +
                                     _parse_trigger_axes(config),
                            dead_zone=dead_zone,
                            hot_zone=hot_zone)

    global CLASS_CREATION_COUNT
    name = _parse_name(config) or f'DynamicController{CLASS_CREATION_COUNT}'
    CLASS_CREATION_COUNT = CLASS_CREATION_COUNT + 1
    LOGGER.info(f'creating new class with name "{name}"')

    # Create a new class definition
    new_class_def = type(name, (Controller,), {
        '__init__': constructor,
    })
    # Set the class level registration ID method
    ids = _parse_registration_ids(config)
    setattr(new_class_def, 'registration_ids', staticmethod(lambda: ids))

    if register:
        # Insert into the global (really module level) dictionary
        LOGGER.info(f'registering new class as {__name__}.{new_class_def.__qualname__}')
        globals()[name] = new_class_def

    return name, new_class_def


def _load_yaml(filename: str) -> Dict:
    """
    Load a dict from a YAML file

    :param filename:
        filename
    :return:
        dict parsed from YAML
    """
    with open(filename, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        LOGGER.info(f'loaded yaml config from {filename}')
        return config


def _parse_buttons(d: Dict) -> List:
    """
    Extract button definitions from the config. The corresponding YAML form is:

    .. code-block:: yaml

        buttons:
          - X:307:square
          - Y:309:triangle
          - B:305:circle

    Button definitions are of the form NAME:CODE:SNAME

    :param d:
        config dict built from the YAML source
    :return:
        list of :class:`~approxeng.input.Button`
    """
    if 'buttons' in d:
        buttons = list([Button(*button_string.split(SEPARATOR)) for button_string in d['buttons']])
        LOGGER.info(f'buttons      : {[button.name for button in buttons]}')
        return buttons
    LOGGER.info('buttons      : NONE')
    return []


def _parse_centred_axes(d: Dict) -> List:
    """
    Extract centred axis definitions from the config. The corresponding YAML form is:

    .. code-block:: yaml

        centred_axes:
          - Left Horizontal:-32768:32768:0:lx
          - Left Vertical:32768:-32768:1:ly
          - Right Horizontal:-32768:32768:3:rx
          - Right Vertical:32768:-32768:4:ry

    Axis definitions are of the form NAME:LOW_VALUE:HIGH_VALUE:CODE:SNAME - note that the low value
    is the value corresponding to a -1.0 output, and not necessarily the lowest event value! In the
    case of inverted axes we now express these by simply reversing the low and high values, rather than
    with an explicit invert flag.

    :param d:
        config dict built from the YAML source
    :return:
        list of :class:`~approxeng.input.CentredAxis`
    """

    def _parse_centred_axis(axis_string: str) -> CentredAxis:
        name, min, max, code, sname = axis_string.split(SEPARATOR)
        return CentredAxis(name=name, min_raw_value=min, max_raw_value=max,
                           axis_event_code=code, sname=sname)

    if 'centred_axes' in d:
        axes = list([_parse_centred_axis(axis_string) for axis_string in d['centred_axes']])
        LOGGER.info(f'centred axes : {[axis.name for axis in axes]}')
        return axes
    LOGGER.info('centred axes : NONE')
    return []


def _parse_trigger_axes(d: Dict) -> List:
    """
    Extract trigger axis definitions from the config. The corresponding YAML form is:

    .. code-block:: yaml

        trigger_axes:
            - Left Trigger:0:1023:2:lt:l2:0.2
            - Right Trigger:0:1023:5:rt:r2:0.2

    Each axis definition contains either five or seven elements. For the five element form,
    the string is NAME:MIN_VALUE:MAX_VALUE:CODE:SNAME. For the seven element form there's
    an additional pair BUTTON_SNAME:THRESHOLD used to generate a button press with the specified
    name when the trigger passes through the threshold value. Some controllers don't emit
    a button press event from their analogue triggers, so we use this form to generate that
    event based on the analogue value.

    :param d:
        config dict built from the YAML source
    :return:
        list of :class:`~approxeng.input.TriggerAxis`
    """

    def _parse_trigger_axis(axis_string: str) -> TriggerAxis:
        split = axis_string.split(SEPARATOR)
        if len(split) == 5:
            name, min_raw, max_raw, code, sname = split
            return TriggerAxis(name=name, min_raw_value=min_raw, max_raw_value=max_raw, axis_event_code=code,
                               sname=sname)
        elif len(split) == 7:
            # Trigger axes optionally have a button sname and trigger value for cases where
            # the controller has an analogue trigger but doesn't also generate button press
            # events itself.
            name, min_raw, max_raw, code, sname, button_sname, button_trigger_value = split
            return TriggerAxis(name=name, min_raw_value=min_raw, max_raw_value=max_raw, axis_event_code=code,
                               sname=sname,
                               button_sname=button_sname, button_trigger_value=button_trigger_value)

    if 'trigger_axes' in d:
        axes = list([_parse_trigger_axis(axis_string) for axis_string in d['trigger_axes']])
        LOGGER.info(f'trigger axes : {[axis.name for axis in axes]}')
        return axes
    LOGGER.info('trigger axes : NONE')
    return []


def _parse_binary_axes(d: Dict) -> List:
    """
    Extract binary axis definitions from the config. The corresponding YAML form is:

    .. code-block:: yaml

        binary_axes:
            - D-pad Horizontal:16:dleft:dright
            - D-pad Vertical:17:dup:ddown

    Each axis definition contains NAME:CODE:BUTTON_SNAME_LOW:BUTTON_SNAME_HIGH

    :param d:
        config dict built from the YAML source
    :return:
        list of :class:`~approxeng.input.BinaryAxis`
    """
    if 'binary_axes' in d:
        axes = list([BinaryAxis(*axis_string.split(SEPARATOR)) for axis_string in d['binary_axes']])
        LOGGER.info(f'binary axes  : {[axis.name for axis in axes]}')
        return axes
    LOGGER.info('binary axes  : NONE')
    return []


def _parse_registration_ids(d: Dict) -> List[Tuple[int, int]]:
    """
    Extract registration IDs from the config. The corresponding YAML form is:

    .. code-block:: yaml

        ids:
          - vendor: 0x45e
            product: 0x2ea

    :param d:
        config dict built from the YAML source
    :return:
        list of tuples of (vendor, product) IDs
    """
    if 'ids' in d:
        ids = list([(int(spec['vendor']), int(spec['product'])) for spec in d['ids']])
        LOGGER.info(f'(V,P) IDs    : {ids}')
        return ids
    LOGGER.info('IDs          : NONE')
    return []


def _parse_name(d: Dict) -> Optional[str]:
    """
    Pull out class name from config. Corresponding YAML is:

    .. code-block:: yaml

        name: XBoxOne

    :param d:
        config dict built from the YAML source
    :return:
        string name, or None if no name is specified (this is usually, but not
        invariably, an error in the configuration)
    """
    if 'name' in d:
        return d['name']
    LOGGER.error('no name specified!')
    return None
