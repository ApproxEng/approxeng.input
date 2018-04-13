import logging
from time import time

import logzero

logger = logzero.setup_logger(name='approxeng.input', level=logging.NOTSET)


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


class Controller(object):
    """
    Superclass for controller implementations

    :ivar int vendor_id:
        Vendor ID used to identify the controller type.
    :ivar int product_id:
        Product ID used to identify the controller type.
    :ivar approxeng.input.Axes axes:
        All analogue axes. You can get the individual axis objects from this, but you shouldn't ever need to do this,
        use methods on Controller instead!
    :ivar approxeng.input.Buttons buttons:
        All buttons are managed by this object. This can be used to access Button objects representing buttons on the
        controller, but you will almost never need to do this - use the methods on Controller instead!
    :ivar: boolean connected:
        True if the controller is connected to a source of events, False otherwise. This can be used as a break
        condition to check for controller disconnection.
    """

    def __init__(self, vendor_id, product_id, controls, node_mappings=None, dead_zone=None,
                 hot_zone=None):
        """
        Populate the controller name, button set and axis set.

        :param int vendor_id:
            The USB vendor ID for the controller
        :param int product_id:
            The USB product ID for the controller
        :param controls:
            A sequence of Button, CentredAxis, TriggerAxis and BinaryAxis instances
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
        self.vendor_id = vendor_id
        self.product_id = product_id
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
        self.stream = Controller.ControllerStream(self)

    @property
    def connected(self):
        """
        Returns True if the controller object is associated correctly with a physical device, False otherwise. Use this
        to detect a loss of controller pairing.
        """
        if self.device_unique_name:
            return True
        return False

    @property
    def battery_level(self):
        """
        Returns the battery level, as a float from 0.0 to 1.0, or None if not available
        """
        return None

    class ControllerStream(object):

        def __init__(self, controller):
            self.controller = controller

        def __getitem__(self, item):
            def generator():
                while self.controller.connected:
                    yield self.controller.__getitem__(item)

            return generator()

    def __getitem__(self, item):
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

    def __getattr__(self, item):
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

    def __contains__(self, item):
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

    def check_presses(self):
        """
        Return the set of Buttons which have been pressed since this call was last made, clearing it as we do. This is
        a shortcut do doing 'buttons.get_and_clear_button_press_history'

        :return:
            A ButtonPresses instance which contains buttons which were pressed since this call was last made.
        """
        return self.buttons.check_presses()

    @property
    def has_presses(self):
        return self.buttons.presses.has_presses

    @property
    def presses(self):
        """
        The ButtonPresses containing buttons pressed between the two most recent calls to check_presses
        """
        return self.buttons.presses

    @property
    def controls(self):
        """
        :return:
            A struct containing all the names of controls on this controller
        """
        return {'axes': self.axes.names,
                'buttons': self.buttons.names}

    def register_button_handler(self, button_handler, button_sname):
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

    def __str__(self):
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

    def axis_updated(self, event, prefix=None):
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
            axis.set_raw_value(float(event.value))
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
    def names(self):
        """
        The snames of all axis objects
        """
        return sorted([name for name in self.axes_by_sname.keys() if name is not ''])

    @property
    def active_axes(self):
        """
        Return a sequence of all Axis objects which are not in their resting positions
        """
        return [axis for axis in self.axes if axis.value != 0]

    def __getitem__(self, sname):
        """
        Get an axis by sname, if present

        :param sname:
            The standard name to search
        :return:
            An axis object, or None if no such button exists
        """
        return self.axes_by_sname.get(sname)

    def __getattr__(self, item):
        """
        Called when an unresolved attribute is requested, retrieves the Axis object for the given sname

        :param item:
            the standard name of the axis to query
        :return:
            the corrected value of the axis, or raise AttributeError if no such axis is present
        """
        if item in self.axes_by_sname:
            return self.get(item)
        raise AttributeError

    def __contains__(self, item):
        """
        Check whether a given axis, referenced by sname, exists

        :param item:
            The sname of the axis to search
        :return:
            True if the axis exists, false otherwise
        """
        return item in self.axes_by_sname


class TriggerAxis(object):
    """
    A single analogue axis where the expected output range is 0.0 to 1.0. Typically this is used for triggers, where the
    resting position is 0.0 and any interaction causes higher values. Whether a particular controller exposes triggers
    as axes or as buttons depends on the hardware - the PS3 front triggers appear as buttons, the XBox One triggers as
    axes.
    """

    def __init__(self, name, min_raw_value, max_raw_value, axis_event_code, dead_zone=0.0, hot_zone=0.0, sname=None,
                 button_sname=None, button_trigger_value=0.5):
        """
        Create a new TriggerAxis - this will be done internally within the controller classes i.e.
        :class:`approxeng.input.xboxone.XBoxOneSPad`

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

    def _input_to_raw_value(self, value):
        """
        Convert the value read from evdev to a 0.0 to 1.0 range.

        :internal:

        :param value:
            a value ranging from the defined minimum to the defined maximum value.
        :return:
            0.0 at minumum, 1.0 at maximum, linearly interpolating between those two points.
        """
        return (value - self.min_raw_value) / self.max_raw_value

    @property
    def raw_value(self):
        """
        Get an uncorrected value for this trigger

        :return: a float value, 0.0 when not pressed, to 1.0 when fully pressed
        """
        return self.__value

    @property
    def value(self):
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

    def set_raw_value(self, raw_value):
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


class BinaryAxis(object):
    """
    A fake 'analogue' axis which actually corresponds to a pair of buttons. Once associated with a Buttons instance
    it routes events through to the Buttons instance to create button presses corresponding to axis movements.
    """

    def __init__(self, name, axis_event_code, invert=False, b1name=None, b2name=None):
        """
        Create a new binary axis, used to route axis events through to a pair of buttons, which are created as
        part of this constructor

        :param name:
            Name for the axis, use this to describe the axis, it's not used for anything else
        :param axis_event_code:
            The evdev event code for changes to this axis
        :param invert:
            True to invert data, used when the raw data is in the opposite sense to normal
        :param b1name:
            The sname of the button corresponding to negative values of the axis.
        :param b2name:
            The sname of the button corresponding to positive values of the axis
        """
        self.name = name
        self.axis_event_code = axis_event_code
        self.b1 = Button('{}_left_button'.format(name), key_code='{}_left'.format(axis_event_code), sname=b1name)
        self.b2 = Button('{}_right_button'.format(name), key_code='{}_right'.format(axis_event_code), sname=b2name)
        self.invert = invert
        self.buttons = None
        self.last_value = 0
        self.sname = ''
        self.__value = 0

    def set_raw_value(self, raw_value):
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
        if self.invert:
            return -self.__value
        else:
            return self.__value

    def __str__(self):
        return "BinaryAxis name={}, sname={}, corrected_value={}".format(self.name, self.sname, self.value)


class CentredAxis(object):
    """
    A single analogue axis on a controller where the expected output range is -1.0 to 1.0 and the resting position of
    the control is at 0.0, at least in principle.
    """

    def __init__(self, name, min_raw_value, max_raw_value, axis_event_code, invert=False, dead_zone=0.0, hot_zone=0.0,
                 sname=None):
        """
        Create a new CentredAxis - this will be done internally within the controller classes i.e.
        :class:`approxeng.input.sixaxis.SixAxis`

        :param name:
            A friendly name for the axis
        :param min_raw_value:
            The value read from the event system when the axis is at its minimum value
        :param max_raw_value:
            The value read from the event system when the axis is at its maximum value
        :param axis_event_code:
            The evdev code for this axis, used to dispatch events to the axis from the event system
        :param invert:
            True to invert data, used when the raw data is in the opposite sense to normal
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
        self.invert = invert
        self.dead_zone = dead_zone
        self.hot_zone = hot_zone
        self.min_raw_value = float(min_raw_value)
        self.max_raw_value = float(max_raw_value)
        self.axis_event_code = axis_event_code
        self.sname = sname

    def _input_to_raw_value(self, value):
        """
        Convert the value read from evdev to a -1.0 to 1.0 range.

        :internal:

        :param value:
            a value ranging from the defined minimum to the defined maximum value.
        :return:
            -1.0 at minumum, 1.0 at maximum, linearly interpolating between those two points.
        """
        return (value - self.min_raw_value) * (2 / (self.max_raw_value - self.min_raw_value)) - 1.0

    @property
    def raw_value(self):
        """
        Get an uncorrected value for this axis

        :return: a float value, negative to the left or down, and ranging from -1.0 to 1.0
        """
        return self.__value

    @property
    def value(self):
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

    def set_raw_value(self, raw_value):
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

    def __str__(self):
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

        :param sname: the name to check
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
            logger.debug('Unknown button code {} ({})'.format(key_code, prefix))

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

    @property
    def names(self):
        """
        The snames of all button objects
        """
        return sorted([name for name in self.buttons_by_sname.keys() if name is not ''])

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

    def check_presses(self):
        """
        Return the set of Buttons which have been pressed since this call was last made, clearing it as we do.

        :return:
            A ButtonPresses instance which contains buttons which were pressed since this call was last made.
        """
        pressed = []
        for button, state in self.buttons.items():
            if state.was_pressed_since_last_check:
                pressed.append(button)
                state.was_pressed_since_last_check = False
        self.__presses = ButtonPresses(pressed)
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
            if state.is_pressed and state.last_pressed is not None:
                return time() - state.last_pressed
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
