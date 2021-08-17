from evdev import InputDevice
from threading import Thread
from select import select
import logging
from approxeng.input import Button, CentredAxis, TriggerAxis, BinaryAxis, Controller

LOGGER = logging.getLogger(name='approxeng.input.profiling')

EV_KEY = 1
EV_REL = 2
EV_ABS = 3

BUTTON_NAMES = ['circle', 'cross', 'square', 'triangle', 'home', 'select', 'start', 'l1', 'r1', 'l2', 'r2',
                'ls', 'rs', 'dup', 'ddown', 'dleft', 'dright']
AXIS_NAMES = ['lx', 'ly', 'rx', 'ry', 'lt', 'rt', 'dx', 'dy']


class Profiler:
    """
    Holds the observed state of a set of controller axes and buttons. The profiler thread updates this, maintaining
    the highest and lowest observed values for an axis, and the last button to be pressed. We use this to guess the
    most likely intentional movement or button press from the user when profiling a controller.
    """

    def __init__(self, device: InputDevice):
        self.last_button_pressed = None
        self.axes = {}
        self.device = device

    def reset(self):
        self.last_button_pressed = None
        self.axes.clear()

    def update_axis(self, code, value):
        if code not in self.axes:
            self.axes[code] = value, value, value
        min_value, max_value, _ = self.axes[code]
        self.axes[code] = min(min_value, value), max(max_value, value), value

    def update_button(self, code):
        self.last_button_pressed = code

    @property
    def axis_changes(self):
        return sorted([(code, self.axes[code][0], self.axes[code][1], self.axes[code][2]) for code in self.axes],
                      key=lambda item: -abs(item[1] - item[2]))

    @property
    def binary_axis_changes(self):
        return [(code, low, high, value) for code, low, high, value in self.axis_changes if low == -1 and high == 1]


class ProfilerThread(Thread):
    """
    Thread that reads events from an InputDevice and uses them to update a profile object
    """

    def __init__(self, profiler: Profiler):
        Thread.__init__(self, name='evdev profiler thread')
        self.daemon = True
        self.running = True
        self.profiler = profiler

    def run(self):
        while self.running:
            try:
                r, w, x = select([self.profiler.device], [], [], 0.5)
                for fd in r:
                    for event in fd.read():
                        if event.type == EV_ABS or event.type == EV_REL:
                            self.profiler.update_axis(event.code, event.value)
                        elif event.type == EV_KEY:
                            self.profiler.update_button(event.code)
            except Exception as e:
                self.stop(e)

    def stop(self, exception=None):
        if exception:
            LOGGER.error('Error when reading from device!', exc_info=exception)
        self.running = False


class AxisProfile:
    """
    Details of a single axis
    """

    def __init__(self, code=None, min_value=0, max_value=0, invert=False, disable=False):
        # evdev code
        self.code = code
        # minimum reported value
        self.min_value = min_value
        # maximum reported value
        self.max_value = max_value
        # normally we assume positive = up / right, this inverts that
        self.invert = invert
        # allow for explicitly disabled axes
        self.disable = disable

    @property
    def real_max(self):
        return self.max_value if not self.invert else self.min_value

    @property
    def real_min(self):
        return self.min_value if not self.invert else self.max_value

    def __bool__(self):
        return self.code is not None and not self.disable

    def build_repr(self, control=None, axis=None, current_value=None):
        """
        String representation of this axis profile

        :param current_value: optionally adds the current value of the axis to the display
        """
        control_string = f'[{control}] ' if control else ''
        axis_string = f'{axis} : ' if axis else ''
        if self.disable:
            return f'{control_string}{axis_string}DISABLED'
        if self.code is None:
            return f'{control_string}{axis_string}---'
        if current_value is not None:
            return f'{control_string}{axis_string}{self.code} = {current_value} {"[invert]" if self.invert else ""}'
        else:
            return f'{control_string}{axis_string}{self.code} {"[invert]" if self.invert else ""}'


class Profile:
    """
    Profile of a (simplified) controller, with a single input device and a standard set of controls, all of which are
    optional. Can be retrieved and stored from and to a dict, and can dynamically create a Controller subclass from
    this information when needed.
    """

    def __init__(self, d=None):
        # Note - some of these axes and button names are mutually exclusive, in particular some controllers
        # don't have button events for analogue triggers, and d-pads are either buttons or binary axes
        self._reset()
        self.vendor_id = 0
        self.product_id = 0
        self.name = 'unknown controller'
        if d:
            self.dict = d

    def _reset(self):
        self.buttons = {button: None for button in BUTTON_NAMES}
        self.axes = {axis: AxisProfile() for axis in AXIS_NAMES}

    def set_button(self, name, code):
        if name in self.buttons:
            self.buttons[name] = code
        else:
            LOGGER.warning(f'Unknown button sname={name}, not using')

    def set_axis_range(self, name, code, min_value, max_value):
        if name in self.axes:
            axis = self.axes[name]
            axis.min_value = min_value
            axis.max_value = max_value
            axis.code = code

    def toggle_axis_enable(self, name):
        if name in self.axes:
            self.axes[name].disable = not self.axes[name].disable

    def toggle_axis_invert(self, name):
        if name in self.axes and self.axes[name]:
            self.axes[name].invert = not self.axes[name].invert

    @property
    def dict(self):
        return {'vendor': self.vendor_id,
                'product': self.product_id,
                'name': self.name,
                'buttons': {button: self.buttons[button] for button in self.buttons if self.buttons[button]},
                'axes': {axis: {'code': self.axes[axis].code,
                                'min_value': self.axes[axis].min_value,
                                'max_value': self.axes[axis].max_value,
                                'invert': self.axes[axis].invert} for axis in self.axes if self.axes[axis]}}

    @dict.setter
    def dict(self, d):
        self._reset()
        for name, code in d['buttons'].items():
            self.buttons[name] = code
        for name, axis in d['axes'].items():
            self.axes[name] = AxisProfile(code=axis['code'],
                                          min_value=axis['min_value'],
                                          max_value=axis['max_value'],
                                          invert=axis['invert'])
        self.vendor_id = d['vendor']
        self.product_id = d['product']
        self.name = d['name']

    @property
    def controls(self):
        """
        Infers a list of control objects from the current set of known axes etc. This can be used to construct
        a controller class
        """
        # Get all buttons first, only picking up ones for which we've got known codes
        buttons = [Button(name=name, key_code=self.buttons[name], sname=name) for name in self.buttons if
                   self.buttons[name]]

        # Pick up trigger axes if we have them
        def trigger_axis(axis_name, button_name):
            if self.axes[axis_name]:
                axis = self.axes[axis_name]
                if self.buttons[button_name]:
                    # We have a trigger button defined, no need to include it in the trigger definition
                    return TriggerAxis(name=axis_name, min_raw_value=axis.real_min, max_raw_value=axis.real_max,
                                       axis_event_code=axis.code, sname=axis_name)
                else:
                    # Have an analogue trigger but no trigger button, set the trigger axis to create a
                    # virtual button triggered at 20% activation, this is what we use for e.g. xbox controllers
                    return TriggerAxis(name=axis_name, min_raw_value=axis.real_min, max_raw_value=axis.real_max,
                                       axis_event_code=axis.code, sname=axis_name, button_sname=button_name,
                                       button_trigger_value=0.2)

        triggers = [trigger_axis(a, b) for a, b in [('lt', 'l2'), ('rt', 'r2')]]

        # Binary axes - these are generally just the D-pad on some controllers (some have actual buttons, some
        # have a slightly strange axis which only reports -1 and 1 when buttons are pressed
        def binary_axis(axis_name, b1name, b2name):
            if self.axes[axis_name] and self.buttons[b1name] is None and self.buttons[b2name] is None:
                axis = self.axes[axis_name]
                return BinaryAxis(name=axis_name, axis_event_code=axis.code,
                                  b1name=b1name if not axis.invert else b2name,
                                  b2name=b2name if not axis.invert else b1name)

        dpad = [binary_axis(a, b, c) for a, b, c in [('dx', 'dleft', 'dright'), ('dy', 'dup', 'ddown')]]

        # Regular centred axes
        def centred_axis(axis_name):
            if self.axes[axis_name]:
                axis = self.axes[axis_name]
                return CentredAxis(name=axis_name, min_raw_value=axis.real_min, max_raw_value=axis.real_max,
                                   axis_event_code=axis.code, sname=axis_name)

        sticks = [centred_axis(name) for name in ['lx', 'ly', 'rx', 'ry']]

        return list([control for control in [*buttons, *triggers, *dpad, *sticks] if control is not None])

    def build_controller_class(self):
        """
        Builds a new controller subclass which should be able to drive a controller with this profile. These
        controller classes are simple, they only map to a single device and they don't support any special features
        of the controller such as onboard LEDs, motion sensors etc. This is, however, enough for almost all
        controller types, leaving custom code only required for things like the dualshock controllers with their
        fancy touchpad surfaces and similar
        """
        profile = self

        class ProfiledController(Controller):

            def __init__(self, dead_zone=0.05, hot_zone=0.05, **kwargs):
                super(ProfiledController, self).__init__(controls=profile.controls,
                                                         dead_zone=dead_zone,
                                                         hot_zone=hot_zone,
                                                         **kwargs)

            @staticmethod
            def registration_ids():
                return [(profile.vendor_id, profile.product_id)]

            def __repr__(self) -> str:
                return profile.name

        return ProfiledController
