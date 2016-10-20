from approxeng.input import Axis, Button, Buttons
from approxeng.input.asyncorebinder import bind_controller

try:
    from evdev import ecodes
except ImportError:
    # Ignore this error, it happens when building the documentation on OSX (as evdev won't build there) but is otherwise
    # not significant. Obviously if it's actually failing to import in real systems that would be a problem!
    print 'Not importing evdev, expected during sphinx generation on OSX'

CONTROLLER_NAME = "Sony PLAYSTATION(R)3 Controller"

BUTTON_SELECT = Button("Select", 288)  #: The Select button
BUTTON_LEFT_STICK = Button("Left Stick", 289)  #: Left stick click button
BUTTON_RIGHT_STICK = Button("Right Stick", 290)  #: Right stick click button
BUTTON_START = Button("Start", 291)  #: Start button
BUTTON_D_UP = Button("D Up", 292)  #: D-pad up
BUTTON_D_RIGHT = Button("D Right", 293)  #: D-pad right
BUTTON_D_DOWN = Button("D Down", 294)  #: D-pad down
BUTTON_D_LEFT = Button("D Left", 295)  #: D-pad left
BUTTON_L2 = Button("L2", 296)  #: L2 lower shoulder trigger
BUTTON_R2 = Button("R2", 297)  #: R2 lower shoulder trigger
BUTTON_L1 = Button("L1", 298)  #: L1 upper shoulder trigger
BUTTON_R1 = Button("R1", 299)  #: R1 upper shoulder trigger
BUTTON_TRIANGLE = Button("Triangle", 300)  #: Triangle
BUTTON_CIRCLE = Button("Circle", 301)  #: Circle
BUTTON_CROSS = Button("Cross", 302)  #: Cross
BUTTON_SQUARE = Button("Square", 303)  #: Square
BUTTON_PS = Button("Home (PS)", 704)  #: PS button


class SixAxisResource:
    """
    Resource class which will automatically connect and disconnect to and from a joystick, creating a new SixAxis
    object and passing it to the 'with' clause. Also binds a handler to the START button which resets the axis
    calibration, and to the SELECT button which centres the analogue sticks on the current position.
    """

    def __init__(self, bind_defaults=False, dead_zone=0.05, hot_zone=0.0):
        """
        Resource class, produces an :class:`approxeng.input.SixAxis` for use in a 'with' binding.

        :param float dead_zone:
            See SixAxis class documentation
        :param float hot_zone:
            See SixAxis class documentation
        :param bind_defaults:
            Defaults to False, if True will automatically bind two actions to the START and SELECT buttons to
            reset the axis calibration and to set the axis centres respectively.
        """
        self.bind_defaults = bind_defaults
        self.dead_zone = dead_zone
        self.hot_zone = hot_zone

    def __enter__(self):
        self.joystick = SixAxis(dead_zone=self.dead_zone, hot_zone=self.hot_zone)
        self.unbind = bind_controller(self.joystick, CONTROLLER_NAME)
        if self.bind_defaults:
            self.joystick.buttons.register_button_handler(self.joystick.reset_axis_calibration, BUTTON_START)
            self.joystick.buttons.register_button_handler(self.joystick.set_axis_centres, BUTTON_SELECT)
        return self.joystick

    def __exit__(self, exc_type, exc_value, traceback):
        self.unbind()


class SixAxis:
    """
    Class to handle the PS3 SixAxis controller

    This class will process events from the evdev event queue and calculate positions for each of the analogue axes on
    the SixAxis controller (motion sensing is not currently supported). It will also extract
    button press events and call any handler functions bound to those buttons.

    Once the connect() call is made, a thread is created which will actively monitor the device for events, passing them
    to the SixAxis class for processing. There is no need to poll the event queue manually.

    Consuming code can get the current position of any of the sticks from this class through the `axes` instance
    property. This contains a list of :class:`approxeng.input.Axis` objects, one for each distinct axis
    on the controller. The list of axes is, in order: left x, left y, right x, right y.
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.0):
        """
        Discover and initialise a PS3 SixAxis controller connected to this computer.

        :param float dead_zone:
            Creates a dead zone centred on the centre position of the axis (which may or may not be zero depending on
            calibration). The axis values range from 0 to 1.0, but will be locked to 0.0 when the measured value less
            centre offset is lower in magnitude than this supplied value. Defaults to 0.05, which makes the PS3 analogue
            sticks easy to centre but still responsive to motion. The deadzone is applies to each axis independently, so
            e.g. moving the stick far right won't affect the deadzone for that sticks Y axis.
        :param float hot_zone:
            Creates a zone of maximum value, any readings from the sensor which are within this value of the max or min
            values will be mapped to 1.0 and -1.0 respectively. This can be useful because, while the PS3 controllers
            sticks have independent axes, they are constrained to move within a circle, so it's impossible to have e.g.
            1.0,1.0 for both x and y axes. Setting this value to non-zero in effect partially squares the circle,
            allowing for controls which require full range control. Setting this value to 1/sqrt(2) will create a square
            zone of variability within the circular range of motion of the controller, with any stick motions outside
            this square mapping to the maximum value for the respective axis. The value is actually scaled by the max
            and min magnitude for upper and lower ranges respectively, so e.g. setting 0.5 will create a hot-zone at
            above half the maximum value and below half the minimum value, and not at +0.5 and -0.5 (unless max and
            min are 1.0 and -1.0 respectively). As with the dead zone, these are applied separately to each axis, so in
            the case where the hot zone is set to 1/sqrt(2), a circular motion of the stick will map to x and y values
            which trace the outline of a square of unit size, allowing for all values to be emitted from the stick.
        :return: an initialised link to an attached PS3 SixAxis controller.
        """

        self._stop_function = None
        self.axes = [Axis('left_x', dead_zone=dead_zone, hot_zone=hot_zone),
                     Axis('left_y', dead_zone=dead_zone, hot_zone=hot_zone, invert=True),
                     Axis('right_x', dead_zone=dead_zone, hot_zone=hot_zone),
                     Axis('right_y', dead_zone=dead_zone, hot_zone=hot_zone, invert=True)]
        self.buttons = Buttons(
            [BUTTON_SELECT, BUTTON_LEFT_STICK, BUTTON_RIGHT_STICK, BUTTON_START, BUTTON_D_UP, BUTTON_D_RIGHT,
             BUTTON_D_DOWN, BUTTON_D_LEFT, BUTTON_L2, BUTTON_R2, BUTTON_L1, BUTTON_R1, BUTTON_TRIANGLE, BUTTON_CROSS,
             BUTTON_SQUARE, BUTTON_CIRCLE, BUTTON_PS])

    def __str__(self):
        """
        Simple string representation of the state of the axes
        """
        return 'x1={}, y1={}, x2={}, y2={}'.format(
            self.axes[0].corrected_value(), self.axes[1].corrected_value(),
            self.axes[2].corrected_value(), self.axes[3].corrected_value())

    def set_axis_centres(self, *args):
        """
        Sets the centre points for each axis to the current value for that axis. This centre value is used when
        computing the value for the axis and is subtracted before applying any scaling.
        """
        for axis in self.axes:
            axis.centre = axis.value

    def reset_axis_calibration(self, *args):
        """
        Resets any previously defined axis calibration to 0.0 for all axes
        """
        for axis in self.axes:
            axis.reset()

    def handle_evdev_event(self, event):
        """
        Handle a single evdev event, this updates the internal state of the Axis objects as well as calling any
        registered button handlers.

        :internal:

        :param event:
            The evdev event object to parse
        """
        if event.type == ecodes.EV_ABS:
            # Absolute axis value
            value = float(event.value) / 255.0
            if value < 0:
                value = 0
            elif value > 1.0:
                value = 1.0
            if event.code == 0:
                # Left stick, X axis
                self.axes[0].set_raw_value(value)
            elif event.code == 1:
                # Left stick, Y axis
                self.axes[1].set_raw_value(value)
            elif event.code == 2:
                # Right stick, X axis
                self.axes[2].set_raw_value(value)
            elif event.code == 5:
                # Right stick, Y axis (yes, 5...)
                self.axes[3].set_raw_value(value)
        elif event.type == ecodes.EV_KEY:
            # Button event
            if event.value == 1:
                # Button down
                self.buttons.button_pressed(event.code)
            elif event.value == 0:
                # Button up
                self.buttons.button_released(event.code)
