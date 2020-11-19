import logging
from abc import ABC, abstractmethod
from math import sqrt
from time import time
from typing import Optional, Union, Tuple

from evdev import InputEvent

from approxeng.input.sys import sys_nodes

#: Logger - explicitly set the level for this to see log messages
logger = logging.getLogger(name='approxeng.input')


def map_into_range(low, high, raw_value):
    """
    Map an input function into an output value, clamping such that the magnitude of the output is at most 1.0

    :param low:
        The value in the input range corresponding to zero.
    :param high:
        The value in the input range corresponding to 1.0 or -1.0, depending on whether this is higher or lower than the
        low value respectively.
    :param raw_value:
        An input value
    :return:
        Mapped output value
    """
    value = float(raw_value)
    if low < high:
        if value < low:
            return 0
        elif value > high:
            return 1.0
    elif low > high:
        if value > low:
            return 0
        elif value < high:
            return -1.0
    return (value - low) / abs(high - low)


def map_single_axis(low, high, dead_zone, hot_zone, value):
    """
    Apply dead and hot zones before mapping a value to a range. The dead and hot zones are both expressed as the
    proportion of the axis range which should be regarded as 0.0 or 1.0 (or -1.0 depending on cardinality) respectively,
    so for example setting dead zone to 0.2 means the first 20% of the range of the axis will be treated as if it's the
    low value, and setting the hot zone to 0.4 means the last 40% of the range will be treated as if it's the high
    value. Note that as with map_into_range, low is not necessarily numerically lower than high, it instead expresses
    a low value signal as opposed to a high value one (which could include a high negative value). Note that bad things
    happen if dead_zone + hot_zone == 1.0, so don't do that. This is used by the map_dual_axis call, but can also be
    used by itself to handle single axes like triggers where the overall range varies from 0.0 to 1.0 rather than -1.0
    to 1.0 as a regular joystick axis would.

    :param low:
        The value corresponding to no signal
    :param high:
        The value corresponding to a full signal
    :param dead_zone:
        The proportion of the range of motion away from the no-signal end which should be treated as equivalent to no
        signal and return 0.0
    :param hot_zone:
        The proportion of the range of motion away from the high signal end which should be treated as equivalent to a
        full strength input.
    :param value:
        The raw value to map
    :return:
        The scaled and clipped value, taking into account dead and hot zone boundaries, ranging from 0.0 to either 1.0
        or -1.0 depending on whether low or high are numerically larger (low < high means max value is 1.0, high < low
        means it's -1.0).
    """
    input_range = high - low
    corrected_low = low + input_range * dead_zone
    corrected_high = high - input_range * hot_zone
    return map_into_range(corrected_low, corrected_high, value)


def map_dual_axis(low, high, centre, dead_zone, hot_zone, value):
    """
    Map an axis with a central dead zone and hot zones at each end to a range from -1.0 to 1.0. This in effect uses two
    calls to map_single_axis, choosing whether to use centre and low, or centre and high as the low and high values in
    that call based on which side of the centre value the input value falls. This is the call that handles mapping of
    values on regular joysticks where there's a centre point to which the physical control returns when no input is
    being made.

    :param low:
        The raw value corresponding to the strongest negative input (stick far left / down).
    :param high:
        The raw value corresponding to the strongest positive input (stick far right / up).
    :param centre:
        The raw value corresponding to the resting position of the axis when no user interaction is happening.
    :param dead_zone:
        The proportion of each (positive and negative) part of the motion away from the centre which should result in
        an output of 0.0
    :param hot_zone:
        The proportion of each (positive and negative) part of the motion away from each extreme end of the range which
        should result in 1.0 or -1.0 being returned (depending on whether we're on the high or low side of the centre
        point)
    :param value:
        The raw value to map
    :return:
        The filtered and clamped value, from -1.0 at low to 1.0 at high, with a centre as specified mapping to 0.0
    """
    if value <= centre:
        return map_single_axis(centre, low, dead_zone, hot_zone, value)
    else:
        return map_single_axis(centre, high, dead_zone, hot_zone, value)


class Controller(ABC):
    """
    Superclass for controller implementations

    :ivar approxeng.input.Axes axes:
        All analogue axes. You can get the individual axis objects from this, but you shouldn't ever need to do this,
        use methods on Controller instead!
    :ivar approxeng.input.Buttons buttons:
        All buttons are managed by this object. This can be used to access Button objects representing buttons on the
        controller, but you will almost never need to do this - use the methods on Controller instead!
    """

    def __init__(self, controls, node_mappings=None, dead_zone=None,
                 hot_zone=None):
        """
        Populate the controller name, button set and axis set.

        :param controls:
            A list of :class:`~approxeng.input.Button`, :class:`~approxeng.input.CentredAxis`,
            :class:`~approxeng.input.TriggerAxis` and :class:`~approxeng.input.BinaryAxis` instances
        :param node_mappings:
            A dict from device name to a prefix which will be applied to all events from nodes with a
            matching name before dispatching the corresponding events. This is used to handle controller
            types which create multiple nodes in /dev/input by keying on the device names reported to evdev
            for each node. Nodes are grouped by physical or unique ID first so should, in an ideal world at least,
            all correspond to the same physical controller. This is necessary to support some controllers on modern
            kernels, particularly 4.15. If not specified, or none, then no per-node renaming is applied. Device
            names which do not appear in this map are not assigned a prefix, so it's legitimate to only assign
            prefixes for 'new' functionality which has magically appeared in a later kernel. Similarly, this is
            ignored if there is only one device node bound to the controller instance, so the best practice is to
            leave the older mappings named simply by their code, and only use this to handle secondary device nodes
            such as motion sensors.
        :param dead_zone:
            If specified, this is applied to all axes
        :param hot_zone:
            If specified, this is applied to all axes
        """
        self.axes = Axes([control for control in controls if
                          isinstance(control, CentredAxis) or
                          isinstance(control, BinaryAxis) or
                          isinstance(control, TriggerAxis)])
        self.buttons = Buttons([control for control in controls if
                                isinstance(control, Button) or
                                isinstance(control, BinaryAxis) or
                                isinstance(control, TriggerAxis)])
        if dead_zone is not None:
            for axis in self.axes.axes:
                axis.dead_zone = dead_zone
        if hot_zone is not None:
            for axis in self.axes.axes:
                axis.hot_zone = hot_zone
        self.node_mappings = node_mappings
        self.device_unique_name = None
        self.exception = None

        class ControllerStream(object):
            """
            Class to produce streams for values from the parent controller on demand.
            """

            def __init__(self, controller):
                self.controller = controller

            def __getitem__(self, item):
                """
                :param item:
                    Name of an item or items to fetch, referring to them by sname, so either axes or
                    buttons.
                :return:
                    A generator which will emit the value of that item or items every time it's called, in effect
                    creating an infinite stream of values for the given item or items.
                """

                def generator():
                    while self.controller.connected:
                        yield self.controller.__getitem__(item)

                return generator()

        self.stream = ControllerStream(self)

    @property
    def sys_nodes(self) -> {}:
        """
        Returns a dict of discovered sys nodes representing power and LED status for this controller. If the controller
        isn't bound to a physical device, or there aren't LED or power nodes available this returns an empty dict.
        """
        if self.device_unique_name is not None:
            return sys_nodes(self.device_unique_name)
        return {}

    def read_led_value(self, led_name) -> Optional[int]:
        """
        Read an existing LED value. This may or may not work depending on the underlying implementation. Requires
        a bound controller with the specified name present in its LED sys classes. Returns None if this does not
        apply.

        :param led_name:
            Name of LED to query
        :return:
            Integer value of LED, or None if either unbound or no such LED name
        """
        if self.device_unique_name is not None:
            return sys.read_led_value(self.device_unique_name, led_name)
        return None

    def write_led_value(self, led_name: str, value: int):
        """
        Write a value to a named LED. Does nothing if either we're not bound to a device, or there's no
        such LED name.

        :param led_name:
            LED name within this device - use self.sys_nodes['leds'] keys to discover LED names.
        :param value:
            Value to write, should be an integer.
        """
        if self.device_unique_name is not None:
            sys.write_led_value(self.device_unique_name, led_name, value)

    @property
    def battery_level(self) -> Optional[float]:
        """
        Read the battery capacity, if available, as a percentage. If not available, return None
        """
        if self.device_unique_name is not None:
            return sys.read_power_level(self.device_unique_name)
        return None

    @staticmethod
    @abstractmethod
    def registration_ids() -> [Tuple[int, int]]:
        pass

    @property
    def connected(self) -> bool:
        """
        :return:
            True if the controller object is associated correctly with a physical device, False otherwise. Use this
            to detect a loss of controller pairing.
        """
        if self.device_unique_name:
            return True
        return False

    def __getitem__(self, item: Union[str, Tuple[str, ...]]) -> [Optional[float]]:
        """
        Simple index access to axis corrected values and button held times

        :param item:
            the sname of an axis or button, or a tuple thereof
        :return:
            for an axis, the corrected value, or, for a button, the held time or None if not held. Raises AttributeError
            if the given name doesn't correspond to an axis or a button. If a tuple is supplied as an argument, result
            will be a tuple of values.
        """

        if isinstance(item, tuple):
            return [self.__getattr__(single_item) for single_item in item]
        return self.__getattr__(item)

    def __getattr__(self, item: str) -> Optional[float]:
        """
        Property access to axis values and button hold times

        :param item:
            sname of an axis or button
        :return:
            The axis corrected value, or button hold time (None if not held), or AttributeError if sname not found
        """
        if item in self.axes:
            return self.axes[item].value
        elif item in self.buttons:
            return self.buttons.held(item)
        raise AttributeError

    def __contains__(self, item: str) -> bool:
        """
        A Controller contains a named attribute if it has either an axis or a button with the attribute as its sname

        :param item:
            The sname of the button or axis
        :return:
            True if there's a button or axis with that name, false otherwise
        """
        if item in self.axes:
            return True
        if item in self.buttons:
            return True
        return False

    def check_presses(self) -> 'ButtonPresses':
        """
        Return the set of Buttons which have been pressed since this call was last made, clearing it as we do. This is
        a shortcut to doing 'buttons.get_and_clear_button_press_history'

        :return:
            A ButtonPresses instance which contains buttons which were pressed since this call was last made.
        """
        return self.buttons.check_presses()

    @property
    def has_presses(self) -> bool:
        """
        :return: True if there were button presses since the last check.
        """
        return self.buttons.presses.has_presses

    @property
    def has_releases(self) -> bool:
        """
        :return: True if any buttons were released since the last check.
        """
        return self.buttons.releases.has_presses
    
    @property
    def presses(self) -> 'ButtonPresses':
        """
        The :class:`~approxeng.input.ButtonPresses` containing buttons pressed between the two most recent calls to
        :meth:`~approxeng.input.Controller.check_presses`
        """
        return self.buttons.presses

    @property
    def releases(self) -> 'ButtonPresses':
        """
        The :class:`~approxeng.input.ButtonPresses` containing buttons released between the two most recent calls to
        :meth:`~approxeng.input.Controller.check_presses`
        """
        return self.buttons.releases

    @property
    def controls(self) -> {}:
        """
        :return:
            A dict containing all the names of controls on this controller, this takes the form of a dict with two
            keys, `axes` and `buttons`, the values for each of which are lists of strings containing the names of each
            type of control.
        """
        return {'axes': self.axes.names,
                'buttons': self.buttons.names}

    def register_button_handler(self, button_handler, button_sname: str):
        """
        Register a handler function which will be called when a button is pressed

        :param button_handler:
            A function which will be called when any of the specified buttons are pressed. The
            function is called with the Button that was pressed as the sole argument.
        :param button_sname:
            The sname of the button which should trigger the handler function
        :return:
            A no-arg function which can be used to remove this registration
        """
        return self.buttons.register_button_handler(button_handler, self.buttons[button_sname])

    def __str__(self) -> str:
        return "{}, axes={}, buttons={}".format(self.__class__.__name__, self.axes, self.buttons)


class Axes(object):
    """
    A set of TriggerAxis or CentredAxis instances to which events should be routed based on event code. Contains methods
    to reset calibration on all axes, or to centre all axes for which this is meaningful.
    """

    def __init__(self, axes):
        """
        Create a new Axes instance, this will be done within the controller classes, you never have to explicitly
        instantiate this yourself.

        :param axes:
            a sequence of :class:`approxeng.input.TriggerAxis` or :class:`approxeng.input.CentredAxis` or
            :class:`approxeng.input.BinaryAxis` containing all the axes the controller supports.
        """
        self.axes = axes
        self.axes_by_code = {axis.axis_event_code: axis for axis in axes}
        self.axes_by_sname = {axis.sname: axis for axis in axes}

        # Look to see whether we've got pairs of lx,ly and / or rx,ry and create corresponding circular axes
        def add_circular_axis(rootname):
            xname = rootname + 'x'
            yname = rootname + 'y'
            if xname in self.axes_by_sname and yname in self.axes_by_sname:
                self.axes_by_sname[rootname] = CircularCentredAxis(x=self.axes_by_sname[xname],
                                                                   y=self.axes_by_sname[yname])

        add_circular_axis('l')
        add_circular_axis('r')

    def axis_updated(self, event: InputEvent, prefix=None):
        """
        Called to process an absolute axis event from evdev, this is called internally by the controller implementations

        :internal:

        :param event:
            The evdev event to process
        :param prefix:
            If present, a named prefix that should be applied to the event code when searching for the axis
        """
        if prefix is not None:
            axis = self.axes_by_code.get(prefix + str(event.code))
        else:
            axis = self.axes_by_code.get(event.code)
        if axis is not None:
            axis.receive_device_value(event.value)
        else:
            logger.debug('Unknown axis code {} ({}), value {}'.format(event.code, prefix, event.value))

    def set_axis_centres(self, *args):
        """
        Sets the centre points for each axis to the current value for that axis. This centre value is used when
        computing the value for the axis and is subtracted before applying any scaling. This will only be applied
        to CentredAxis instances
        """
        for axis in self.axes_by_code.values():
            if isinstance(axis, CentredAxis):
                axis.centre = axis.value

    def reset_axis_calibration(self, *args):
        """
        Resets any previously defined axis calibration to 0.0 for all axes
        """
        for axis in self.axes:
            axis.reset()

    def __str__(self):
        return list("{}={}".format(axis.name, axis.value) for axis in self.axes_by_code.values()).__str__()

    @property
    def names(self) -> [str]:
        """
        The snames of all axis objects
        """
        return sorted([name for name in self.axes_by_sname.keys() if name != ''])

    @property
    def active_axes(self) -> ['Axis']:
        """
        Return a sequence of all Axis objects which are not in their resting positions
        """
        return [axis for axis in self.axes if axis.value != 0]

    def __getitem__(self, sname: str) -> Optional['Axis']:
        """
        Get an axis by sname, if present

        :param sname:
            The standard name to search
        :return:
            An axis object, or None if no such axis exists
        """
        return self.axes_by_sname.get(sname)

    def __getattr__(self, item) -> 'Axis':
        """
        Called when an unresolved attribute is requested, retrieves the Axis object for the given sname

        :param item:
            the standard name of the axis to query
        :return:
            the corrected value of the axis, or raise AttributeError if no such axis is present
        :raise:
            AttributeError if there's no axis with this name
        """
        if item in self.axes_by_sname:
            return self.get(item)
        raise AttributeError

    def __contains__(self, item: str) -> bool:
        """
        Check whether a given axis, referenced by sname, exists

        :param item:
            The sname of the axis to search
        :return:
            True if the axis exists, false otherwise
        """
        return item in self.axes_by_sname


class Axis(ABC):
    """
    Abstract base class for axis types.
    """

    @property
    @abstractmethod
    def value(self) -> float:
        """
        :return:
            A corrected floating point value, either in the range -1 to 1 for centred axes, or 0 to 1 for non-centred,
            adjusted for dead and hot zones.
        """
        pass

    @abstractmethod
    def receive_device_value(self, value: int):
        """
        Receive a value from the underlying operating system code, in our case evdev, and update the internal state of
        this axis object appropriately.

        :param value:
            Integer value received from the evdev event handler.
        """
        pass


class TriggerAxis(Axis):
    """
    A single analogue axis where the expected output range is 0.0 to 1.0. Typically this is used for triggers, where the
    resting position is 0.0 and any interaction causes higher values. Whether a particular controller exposes triggers
    as axes or as buttons depends on the hardware - the PS3 front triggers appear as buttons, the XBox One triggers as
    axes.
    """

    def __init__(self, name: str, min_raw_value: int, max_raw_value: int, axis_event_code: int, dead_zone=0.0,
                 hot_zone=0.0, sname: Optional[str] = None, button_sname: Optional[str] = None,
                 button_trigger_value=0.5):
        """
        Create a new TriggerAxis - this will be done internally within the :class:`~approxeng.input.Controller`
        sub-class.

        :param name:
            A friendly name for the axis
        :param min_raw_value:
            The value read from the event system when the trigger is not pressed
        :param max_raw_value:
            The value read from the event system when the trigger is fully pressed
        :param axis_event_code:
            The evdev code for this axis, used when dispatching events to it from an Axes object
        :param dead_zone:
            The proportion of the trigger range which will be treated as equivalent to no press
        :param hot_zone:
            The proportion of the trigger range which will be treated as equivalent to fully depressing the trigger
        :param sname:
            The standard name for this trigger, if specified
        :param button_sname:
            If provided, this creates a new Button internally which will be triggered by changes to the axis value. This
            is useful for triggers which have axis representations but no corresponding button presses such as the XBox1
            controller front triggers. If this is set to None then no button is created
        :param button_trigger_value:
            Defaulting to 0.5, this value determines the point in the trigger axis' range at which point the button is
            regarded as being pressed or released.
        """
        self.name = name
        self.max = 0.9
        self.min = 0.1
        self.__value = self.min
        self.dead_zone = dead_zone
        self.hot_zone = hot_zone
        self.min_raw_value = min_raw_value
        self.max_raw_value = max_raw_value
        self.axis_event_code = axis_event_code
        self.sname = sname
        self.buttons = None
        self.button_trigger_value = button_trigger_value
        if button_sname is not None:
            self.button = Button(name='{}_trigger_button'.format(name),
                                 key_code='{}_trigger_button'.format(axis_event_code),
                                 sname=button_sname)
        else:
            self.button = None

    def _input_to_raw_value(self, value: int) -> float:
        """
        Convert the value read from evdev to a 0.0 to 1.0 range.

        :internal:

        :param value:
            a value ranging from the defined minimum to the defined maximum value.
        :return:
            0.0 at minimum, 1.0 at maximum, linearly interpolating between those two points.
        """
        return (float(value) - self.min_raw_value) / self.max_raw_value

    @property
    def raw_value(self) -> float:
        """
        Get an uncorrected value for this trigger

        :return: a float value, 0.0 when not pressed, to 1.0 when fully pressed
        """
        return self.__value

    @property
    def value(self) -> float:
        """
        Get a centre-compensated, scaled, value for the axis, taking any dead-zone into account. The value will
        scale from 0.0 at the edge of the dead-zone to 1.0 (positive) at the extreme position of
        the trigger or the edge of the hot zone, if defined as other than 1.0.

        :return:
            a float value, 0.0 when not pressed or within the dead zone, to 1.0 when fully pressed or in the hot zone
        """
        return map_single_axis(self.min, self.max, self.dead_zone, self.hot_zone, self.__value)

    def reset(self):
        """
        Reset calibration (max, min and centre values) for this axis specifically.

        :internal:
        """
        self.max = 0.9
        self.min = 0.1

    def receive_device_value(self, raw_value: int):
        """
        Set a new value, called from within the joystick implementation class when parsing the event queue.

        :param raw_value: the raw value from the joystick hardware

        :internal:
        """
        new_value = self._input_to_raw_value(raw_value)
        if self.button is not None:
            if new_value > (self.button_trigger_value + 0.05) > self.__value:
                self.buttons.button_pressed(self.button.key_code)
            elif new_value < (self.button_trigger_value - 0.05) < self.__value:
                self.buttons.button_released(self.button.key_code)
        self.__value = new_value
        if new_value > self.max:
            self.max = new_value
        elif new_value < self.min:
            self.min = new_value

    def __str__(self):
        return "TriggerAxis name={}, sname={}, corrected_value={}".format(self.name, self.sname, self.value)


class BinaryAxis(Axis):
    """
    A fake 'analogue' axis which actually corresponds to a pair of buttons. Once associated with a Buttons instance
    it routes events through to the Buttons instance to create button presses corresponding to axis movements. This is
    necessary as some controllers expose buttons, especially D-pad buttons, as a pair of axes rather than four buttons,
    but we almost certainly want to treat them as buttons the way most controllers do.
    """

    def __init__(self, name, axis_event_code, b1name=None, b2name=None):
        """
        Create a new binary axis, used to route axis events through to a pair of buttons, which are created as
        part of this constructor

        :param name:
            Name for the axis, use this to describe the axis, it's not used for anything else
        :param axis_event_code:
            The evdev event code for changes to this axis
        :param b1name:
            The sname of the button corresponding to negative values of the axis.
        :param b2name:
            The sname of the button corresponding to positive values of the axis
        """
        self.name = name
        self.axis_event_code = axis_event_code
        self.b1 = Button('{}_left_button'.format(name), key_code='{}_left'.format(axis_event_code), sname=b1name)
        self.b2 = Button('{}_right_button'.format(name), key_code='{}_right'.format(axis_event_code), sname=b2name)

        self.buttons = None
        self.last_value = 0
        self.sname = ''
        self.__value = 0

    def receive_device_value(self, raw_value: int):
        self.__value = raw_value
        if self.buttons is not None:
            if self.last_value < 0:
                self.buttons.button_released(self.b1.key_code)
            elif self.last_value > 0:
                self.buttons.button_released(self.b2.key_code)
            self.last_value = raw_value
            if raw_value < 0:
                self.buttons.button_pressed(self.b1.key_code)
            elif raw_value > 0:
                self.buttons.button_pressed(self.b2.key_code)

    @property
    def value(self):
        """
        You probably don't want to actually get the value of this axis, use the generated buttons instead.

        :returns int:
            The raw value from the evdev events driving this axis.
        """
        return self.__value

    def __str__(self):
        return "BinaryAxis name={}, sname={}, corrected_value={}".format(self.name, self.sname, self.value)


class CircularCentredAxis:
    """
    An aggregation of a pair of :class:`~approxeng.input.CentredAxis` instances.

    When using a pair of centred axes to model a single joystick there are some unexpected and probably undesirable
    issues with dead zones. As each axis is treated independently, the dead zones are also applied independently - this
    means that, for example, with the joystick fully pushed forwards you still have the dead zone behaviour between left
    and right. You may prefer a behaviour where both axes are zero if the stick is within a certain distance of its
    centre position in any direction. This class provides that, and is created from a pair of centred axes, i.e. 'lx'
    and 'ly'. The value is returns is a tuple of (x,y) positions. Use of this class will constrain the overall motion
    of the paired axes into the unit circle - in many controllers this is true because of the physical layout of the
    controller, but it may not always be in hardware terms.
    """

    def __init__(self, x: "CentredAxis", y: "CentredAxis", dead_zone=0.1, hot_zone=0.1):
        """
        Create a new circular centred axis

        :param CentredAxis x:
            Axis to use for x value
        :param CentredAxis y:
            Axis to use for y value
        :param float dead_zone:
            Specifies the distance from the centre prior to which both x and y will return 0.0, defaults to 0.1
        :param float hot_zone:
            Specifies the distance from the 1.0 distance beyond which both x and y will return +-1.0, i.e. if the hot
            zone is set to 0.1 then all positions where the distance is greater than 0.9 will return magnitude 1 total
            distances. Defaults to 0.1
        """
        self.x = x
        self.y = y
        self.dead_zone = dead_zone
        self.hot_zone = hot_zone

    def _calculate_position(self, raw_x: float, raw_y: float):
        """
        Map x and y to a corrected x,y tuple based on the configured dead and hot zones.

        :param raw_x:
            Raw x axis position, -1.0 to 1.0
        :param raw_y:
            Raw y axis position, -1.0 to 1.0
        :return:
            x,y corrected position
        """
        # Avoid trying to take sqrt(0) in pathological case
        if raw_x != 0 or raw_y != 0:
            distance = sqrt(raw_x * raw_x + raw_y * raw_y)
        else:
            return 0.0, 0.0
        if distance >= 1.0 - self.hot_zone:
            # Return normalised value, which corresponds to the unit vector in that direction
            return raw_x / distance, raw_y / distance
        elif distance <= self.dead_zone:
            # Return zero vector
            return 0.0, 0.0
        # Guarantee distance to be between dead_zone and 1.0-hot_zone at this point, scale it and return
        effective_distance = (distance - self.dead_zone) / (1.0 - (self.dead_zone + self.hot_zone))
        scale = effective_distance / distance
        return raw_x * scale, raw_y * scale

    @property
    def value(self) -> (float, float):
        return self._calculate_position(raw_x=self.x.raw_value, raw_y=self.y.raw_value)


class CentredAxis(Axis):
    """
    A single analogue axis on a controller where the expected output range is -1.0 to 1.0 and the resting position of
    the control is at 0.0, at least in principle.
    """

    def __init__(self, name, min_raw_value, max_raw_value, axis_event_code, dead_zone=0.0, hot_zone=0.0,
                 sname=None):
        """
        Create a new CentredAxis - this will be done internally within the :class:`~approxeng.input.Controller`
        sub-class.

        :param name:
            A friendly name for the axis
        :param min_raw_value:
            The value read from the event system when the axis is at its minimum value
        :param max_raw_value:
            The value read from the event system when the axis is at its maximum value
        :param axis_event_code:
            The evdev code for this axis, used to dispatch events to the axis from the event system
        :param dead_zone:
            Size of the dead zone in the centre of the axis, within which all values will be mapped to 0.0
        :param hot_zone:
            Size of the hot zones at the ends of the axis, where values will be mapped to -1.0 or 1.0
        :param sname:
            The standard name for this axis, if specified
        """
        self.name = name
        self.centre = 0.0
        self.max = 0.9
        self.min = -0.9
        self.__value = 0.0
        self.invert = min_raw_value > max_raw_value
        self.dead_zone = dead_zone
        self.hot_zone = hot_zone
        self.min_raw_value = float(min(min_raw_value, max_raw_value))
        self.max_raw_value = float(max(min_raw_value, max_raw_value))
        self.axis_event_code = axis_event_code
        self.sname = sname

    def _input_to_raw_value(self, value: int):
        """
        Convert the value read from evdev to a -1.0 to 1.0 range.

        :internal:

        :param value:
            a value ranging from the defined minimum to the defined maximum value.
        :return:
            -1.0 at minumum, 1.0 at maximum, linearly interpolating between those two points.
        """
        return (float(value) - self.min_raw_value) * (2 / (self.max_raw_value - self.min_raw_value)) - 1.0

    @property
    def raw_value(self) -> float:
        """
        Get an uncorrected value for this axis

        :return: a float value, negative to the left or down, and ranging from -1.0 to 1.0
        """
        return self.__value

    @property
    def value(self) -> float:
        """
        Get a centre-compensated, scaled, value for the axis, taking any dead-zone into account. The value will
        scale from 0.0 at the edge of the dead-zone to 1.0 (positive) or -1.0 (negative) at the extreme position of
        the controller or the edge of the hot zone, if defined as other than 1.0. The axis will auto-calibrate for
        maximum value, initially it will behave as if the highest possible value from the hardware is 0.9 in each
        direction, and will expand this as higher values are observed. This is scaled by this function and should
        always return 1.0 or -1.0 at the extreme ends of the axis.

        :return: a float value, negative to the left or down and ranging from -1.0 to 1.0
        """
        mapped_value = map_dual_axis(self.min, self.max, self.centre, self.dead_zone, self.hot_zone, self.__value)
        if self.invert:
            return -mapped_value
        else:
            return mapped_value

    def reset(self):
        """
        Reset calibration (max, min and centre values) for this axis specifically. Not generally needed, you can just
        call the reset method on the SixAxis instance.

        :internal:
        """
        self.centre = 0.0
        self.max = 0.9
        self.min = -0.9

    def receive_device_value(self, raw_value: int):
        """
        Set a new value, called from within the joystick implementation class when parsing the event queue.

        :param raw_value: the raw value from the joystick hardware

        :internal:
        """

        new_value = self._input_to_raw_value(raw_value)
        self.__value = new_value
        if new_value > self.max:
            self.max = new_value
        elif new_value < self.min:
            self.min = new_value

    def __str__(self) -> str:
        return "CentredAxis name={}, sname={}, corrected_value={}".format(self.name, self.sname, self.value)


class Button(object):
    """
    A single button on a controller
    """

    def __init__(self, name, key_code=None, sname=None):
        """
        Create a new Button - this will be done by the controller implementation classes, you shouldn't create your own
        unless you're writing such a class.

        :param name:
            A friendly name for the button
        :param key_code:
            The key code for the button, typically an integer used within the button press and release events. Defaults
            to None if not used.
        :param sname:
            The standard name for the button, if available.
        """
        self.name = name
        self.key_code = key_code
        self.sname = sname

    def __repr__(self):
        return "Button(name={}, code={}, sname={})".format(self.name, self.key_code, self.sname)


class ButtonPresses(object):
    """
    Stores the set of buttons pressed within a given time interval
    """

    def __init__(self, buttons):
        self.buttons = buttons
        self.names = list([button.sname for button in buttons])

    def __getitem__(self, item):
        """
        Return true if a button was pressed, referencing by standard name

        :param item: the name to check
        :return: true if contained within the press set, false otherwise
        """
        if isinstance(item, tuple):
            return [(single_item in self.names) for single_item in item]
        return item in self.names

    def __getattr__(self, item):
        """
        Simpler way to query whether a button was pressed by overriding the __getattr__ method

        :param item:
            sname of the button
        :return:
            true if the button was pressed, false if it either wasn't pressed or wasn't included in the controller
        """
        return item in self.names

    def __contains__(self, item):
        """
        Contains check for a button sname

        :param item:
            The sname of the button to check
        :return:
            True if the button is in the set of pressed buttons, false otherwise
        """
        return item in self.names

    def __iter__(self):
        for name in self.names:
            yield name

    @property
    def has_presses(self):
        return len(self.names) > 0

    def __repr__(self):
        return str(self.names)


class Buttons(object):
    """
    A set of buttons on a controller. This class manages event binding and triggering, as well as monitoring button
    states and tracking whether buttons are held down, and how long if so. Controller implementations instantiate and
    configure an instance of this class when they want to provide button information, the controller is responsible for
    translating button events from the underlying operating system frameworks and updating this object appropriately,
    user code (i.e. your code if you're reading this) uses the methods on this object to react to button presses.
    """

    def __init__(self, buttons_and_axes, ):
        """
        Instantiate a new button manager

        :param buttons_and_axes:
            a list of :class:`approxeng.input.Button` instances which will be managed by this class
        """
        buttons = []
        for thing in buttons_and_axes:
            if isinstance(thing, Button):
                buttons.append(thing)
            elif isinstance(thing, BinaryAxis):
                buttons.append(thing.b1)
                buttons.append(thing.b2)
                thing.buttons = self
            elif isinstance(thing, TriggerAxis):
                if thing.button is not None:
                    buttons.append(thing.button)
                    thing.buttons = self
        self.buttons = {button: Buttons.ButtonState(button) for button in buttons}
        self.buttons_by_code = {button.key_code: state for button, state in self.buttons.items()}
        self.buttons_by_sname = {button.sname: state for button, state in self.buttons.items()}
        self.__presses = None
        self.__releases = None

    class ButtonState:
        """
        Per-button state, including any handlers registered, whether the button was pressed since the last call to
        check, whether it is currently pressed, and the timestamp of the last button press. From this we can handle all
        possible forms of interaction required.
        """

        def __init__(self, button):
            self.button_handlers = []
            self.is_pressed = False
            self.was_pressed_since_last_check = False
            self.was_released_since_last_check = False
            self.last_pressed = None
            self.button = button

    def button_pressed(self, key_code, prefix=None):
        """
        Called from the controller classes to update the state of this button manager when a button is pressed.

        :internal:

        :param key_code:
            The code specified when populating Button instances
        :param prefix:
            Applied to key code if present
        """
        if prefix is not None:
            state = self.buttons_by_code.get(prefix + str(key_code))
        else:
            state = self.buttons_by_code.get(key_code)
        if state is not None:
            for handler in state.button_handlers:
                handler(state.button)
            state.is_pressed = True
            state.last_pressed = time()
            state.was_pressed_since_last_check = True
        else:
            logger.debug('button_pressed : Unknown button code {} ({})'.format(key_code, prefix))

    def button_released(self, key_code, prefix=None):
        """
        Called from the controller classes to update the state of this button manager when a button is released.

        :internal:

        :param key_code:
            The code specified when populating Button instance
        :param prefix:
            Applied to key code if present
        """
        if prefix is not None:
            state = self.buttons_by_code.get(prefix + str(key_code))
        else:
            state = self.buttons_by_code.get(key_code)
        if state is not None:
            state.is_pressed = False
            state.last_pressed = None
            state.was_released_since_last_check = True
        else:
            logger.debug('button_released : Unknown button code {} ({})'.format(key_code, prefix))

    @property
    def names(self):
        """
        The snames of all button objects
        """
        return sorted([name for name in self.buttons_by_sname.keys() if name != ''])

    @property
    def presses(self):
        """
        Get the ButtonPresses containing buttons pressed between the most recent two calls to check_presses. This will
        call the check_presses method if it has never been called before, and is therefore always safe even if your code
        has never called the update function. To make this property actually do something useful, however, you do need
        to call check_presses, preferably once immediately before you then want to handle any button presses that may
        have happened.

        :return:
            a ButtonPresses object containing information about which buttons were pressed
        """
        if self.__presses is None:
            self.check_presses()
        return self.__presses

    @property
    def releases(self):
        """
        Analogous to presses, but returns the set of buttons which were released

        :return:
            a ButtonPresses object containing information about which buttons were released
        """
        if self.__releases is None:
            self.check_presses()
        return self.__releases

    def check_presses(self):
        """
        Return the set of Buttons which have been pressed since this call was last made, clearing it as we do.

        :return:
            A ButtonPresses instance which contains buttons which were pressed since this call was last made.
        """
        pressed = []
        released = []
        for button, state in self.buttons.items():
            if state.was_pressed_since_last_check:
                pressed.append(button)
                state.was_pressed_since_last_check = False
            if state.was_released_since_last_check:
                released.append(button)
                state.was_released_since_last_check = False
        self.__presses = ButtonPresses(pressed)
        self.__releases = ButtonPresses(released)
        return self.__presses

    def held(self, sname):
        """
        Determines whether a button is currently held, identifying it by standard name

        :param sname:
            The standard name of the button
        :return:
            None if the button is not held down, or is not available, otherwise the number of seconds as a floating
            point value since it was pressed
        """
        state = self.buttons_by_sname.get(sname)
        if state is not None:
            last_pressed = state.last_pressed
            if state.is_pressed and last_pressed is not None:
                return time() - last_pressed
        return None

    def __getitem__(self, item):
        """
        Get a button by sname, if present

        :param item:
            The standard name to search
        :return:
            A Button, or None if no such button exists
        """
        return self.buttons_by_sname.get(item).button

    def __getattr__(self, item):
        """
        Property access to Button instances

        :param item:
            the sname of the button
        :return:
            the Button instance, or raise AttributeError if no such button
        """
        if item in self.buttons_by_sname:
            return self.get(item)
        raise AttributeError

    def __contains__(self, item):
        """
        Check whether a given button, referenced by sname, exists

        :param item:
            The sname of the button to search
        :return:
            True if the axis exists, false otherwise
        """
        return item in self.buttons_by_sname

    def register_button_handler(self, button_handler, buttons):
        """
        Register a handler function which will be called when a button is pressed

        :param button_handler:
            A function which will be called when any of the specified buttons are pressed. The
            function is called with the Button that was pressed as the sole argument.
        :param [Button] buttons:
            A list or one or more buttons which should trigger the handler when pressed. Buttons
            are specified as :class:`approxeng.input.Button` instances, in general controller implementations will
            expose these as constants such as SixAxis.BUTTON_CIRCLE. A single Button can be specified if only one button
            binding is required.
        :return:
            A no-arg function which can be used to remove this registration
        """
        if not isinstance(buttons, list):
            buttons = [buttons]
        for button in buttons:
            state = self.buttons.get(button)
            if state is not None:
                state.button_handlers.append(button_handler)

        def remove():
            for button_to_remove in buttons:
                state_to_remove = self.buttons.get(button_to_remove)
                if state_to_remove is not None:
                    state_to_remove.button_handlers.remove(button_handler)

        return remove
