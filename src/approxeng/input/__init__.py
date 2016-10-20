from time import time


class Axis:
    """
    A single analogue axis on a controller
    """

    def __init__(self, name, invert=False, dead_zone=0.0, hot_zone=0.0):
        """
        Create a new Axis - this will be done internally within the controller classes i.e.
        :class:`approxeng.input.sixaxis.SixAxis`

        :param name:
            A friendly name for the axis
        :param invert:
            True to invert data, used when the raw data is in the opposite sense to normal
        :param dead_zone:
            Size of the dead zone in the centre of the axis, within which all values will be mapped to 0.0
        :param hot_zone:
            Size of the hot zones at the ends of the axis, where values will be mapped to -1.0 or 1.0
        """
        self.name = name
        self.centre = 0.5
        self.max = 0.9
        self.min = 0.1
        self.value = 0.5
        self.invert = invert
        self.dead_zone = dead_zone
        self.hot_zone = hot_zone

    def raw_value(self):
        """
        Get an uncorrected value for this axis

        :return: a float value, negative to the left or down, and ranging from -1.0 to 1.0
        """
        return self.value

    def corrected_value(self):
        """
        Get a centre-compensated, scaled, value for the axis, taking any dead-zone into account. The value will
        scale from 0.0 at the edge of the dead-zone to 1.0 (positive) or -1.0 (negative) at the extreme position of
        the controller or the edge of the hot zone, if defined as other than 1.0. The axis will auto-calibrate for
        maximum value, initially it will behave as if the highest possible value from the hardware is 0.9 in each
        direction, and will expand this as higher values are observed. This is scaled by this function and should
        always return 1.0 or -1.0 at the extreme ends of the axis.

        :return: a float value, negative to the left or down and ranging from -1.0 to 1.0
        """

        high_range = self.max - self.centre
        high_start = self.centre + self.dead_zone * high_range
        high_end = self.max - self.hot_zone * high_range

        low_range = self.centre - self.min
        low_start = self.centre - self.dead_zone * low_range
        low_end = self.min + self.hot_zone * low_range

        if self.value > high_start:
            if self.value > high_end:
                result = 1.0
            else:
                result = (self.value - high_start) / (high_end - high_start)
        elif self.value < low_start:
            if self.value < low_end:
                result = -1.0
            else:
                result = (self.value - low_start) / (low_start - low_end)
        else:
            result = 0

        if not self.invert:
            return result
        else:
            return -result

    def reset(self):
        """
        Reset calibration (max, min and centre values) for this axis specifically. Not generally needed, you can just
        call the reset method on the SixAxis instance.

        :internal:
        """
        self.centre = 0.5
        self.max = 0.9
        self.min = 0.1

    def set_raw_value(self, new_value):
        """
        Set a new value, called from within the SixAxis class when parsing the event queue.

        :param new_value: the raw value from the joystick hardware
        :internal:
        """
        self.value = new_value
        if new_value > self.max:
            self.max = new_value
        elif new_value < self.min:
            self.min = new_value


class Button:
    """
    A single button on a controller
    """

    def __init__(self, name, key_code=None):
        """
        Create a new Button - this will be done by the controller implementation classes, you shouldn't create your own
        unless you're writing such a class.

        :param name:
            A friendly name for the button
        :param key_code:
            The key code for the button, typically an integer used within the button press and release events. Defaults
            to None if not used.
        """
        self.name = name
        self.key_code = key_code

    def __repr__(self):
        return "Button(name={}, code={})".format(self.name, self.key_code)


class Buttons:
    """
    A set of buttons on a controller. This class manages event binding and triggering, as well as monitoring button
    states and tracking whether buttons are held down, and how long if so. Controller implementations instantiate and
    configure an instance of this class when they want to provide button information, the controller is responsible for
    translating button events from the underlying operating system frameworks and updating this object appropriately,
    user code (i.e. your code if you're reading this) uses the methods on this object to react to button presses.
    """

    def __init__(self, buttons):
        """
        Instantiate a new button manager

        :param buttons:
            a list of :class:`approxeng.input.Button` instances which will be managed by this class

        """
        self.buttons = {button: Buttons.ButtonState(button) for button in buttons}
        self.buttons_by_code = {button.key_code: state for button, state in self.buttons.items()}

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

    def button_pressed(self, key_code):
        """
        Called from the controller classes to update the state of this button manager when a button is pressed.

        :param key_code:
            The code specified when populating Button instances
        """
        state = self.buttons_by_code.get(key_code)
        if state is not None:
            for handler in state.button_handlers:
                handler(state.button)
            state.is_pressed = True
            state.last_pressed = time()
            state.was_pressed_since_last_check = True

    def button_released(self, key_code):
        """
        Called from the controller classes to update the state of this button manager when a button is released.

        :param key_code:
            The code specified when populating Button instances
        """
        state = self.buttons_by_code.get(key_code)
        if state is not None:
            state.is_pressed = False
            state.last_pressed = None

    def get_and_clear_button_press_history(self):
        """
        Return the set of Buttons which have been pressed since this call was last made, clearing it as we do.

        :return:
            A list of Button instances which were pressed since this call was last made.
        """
        pressed = []
        for button, state in self.buttons.items():
            if state.was_pressed_since_last_check:
                pressed.append(button)
                state.was_pressed_since_last_check = False
        return pressed

    def is_held(self, button):
        """
        Determines whether a button is currently held down

        :param approxeng.input.Button button:
            a Button to check
        :return:
            None if the button is not held down, or the number of seconds as a floating point value since it was
            pressed
        """
        state = self.buttons.get(button)
        if state is not None:
            if state.is_pressed and state.last_pressed is not None:
                return time() - state.last_pressed
        return None

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
