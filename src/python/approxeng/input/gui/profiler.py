import curses
import curses.textpad
import re
import signal
from math import floor

import yaml
from evdev import InputDevice

from approxeng.input.controllers import get_valid_devices
from approxeng.input.profiling import Profiler, ProfilerThread, Profile, BUTTON_NAMES, AXIS_NAMES

DEFAULT_AXIS_KEYS = ('z', 'x', 'c', 'v', 'b', 'n', 'm', ',')
DEFAULT_BUTTON_KEYS = ('1', '2', '3', '4', '5', '6', '7', '8', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a')


def profiler_main():
    devices = list(get_valid_devices())

    if devices:
        print('Available input devices:\n')
    for index, device in enumerate(devices):
        print(f'[{index}] : {device.name} (vendor={device.info.vendor}, product={device.info.product})')
    if devices:
        i = input('\nEnter a device number to continue (0): ')
        try:
            if i == '':
                i = 0
            i = int(i)
            if not len(devices) > i >= 0:
                print('Device number must be one of the ones above, exiting.')
                exit(0)
            run_profiler_gui(devices[i])
        except ValueError:
            print('Input must be a number, exiting.')
            exit(0)
    else:
        print('No valid devices found, ensure your controller is connected?')


def run_profiler_gui(device: InputDevice, button_keys=DEFAULT_BUTTON_KEYS, axis_keys=DEFAULT_AXIS_KEYS):
    curses.wrapper(build_profiler_gui(device=device, button_keys=button_keys, axis_keys=axis_keys))


def build_profiler_gui(device: InputDevice, button_keys=DEFAULT_BUTTON_KEYS, axis_keys=DEFAULT_AXIS_KEYS,
                       filename=None):
    profiler = Profiler(device=device)
    profiler_thread = ProfilerThread(profiler=profiler)
    profiler_thread.start()
    profile = Profile()
    profile.name = device.name
    profile.vendor_id = device.info.vendor
    profile.product_id = device.info.product

    def convert_device_name():
        return re.sub(r'\s+', '_', re.sub(r'[^\w\s]', '', device.name.lower()))

    if filename is None:
        filename = f'{convert_device_name()}_v{device.info.vendor}_p{device.info.product}.yaml'

    def signal_handler(sig, frame):
        with open(filename, 'w') as outfile:
            yaml.dump(profile.dict, outfile)
        profiler_thread.stop()
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    def curses_main(screen):
        try:
            display = DisplayState(screen=screen, profile=profile, profiler=profiler, axis_keys=axis_keys,
                                   button_keys=button_keys)
            curses.cbreak()
            curses.halfdelay(1)
            while True:
                display.start()
                display.println('Approxeng.input controller profiling tool')
                display.println('Select axis or button and activate corresponding control')
                display.println(f'File : {filename}')
                display.println(f'CTRL-C to exit and save YAML definition file')
                # display.println(f'{profiler.axis_changes}')
                display.newline()

                display.print_header('Buttons')
                for index, button in enumerate(BUTTON_NAMES):
                    row, col = divmod(index, 4)
                    display.show_button(display.line + row, col * 20, button)
                display.line += floor((len(BUTTON_NAMES) - 1) / 4) + 1
                display.newline()

                display.print_header('Axes')
                for index, axis in enumerate(AXIS_NAMES):
                    row, col = divmod(index, 2)
                    display.show_axis(display.line + row, col * 40, axis)
                display.line += floor((len(AXIS_NAMES) - 1) / 2) + 1
                display.newline()

                if display.control_is_button:
                    display.println('Button selected - press control to assign or BACKSPACE to clear')
                elif display.control_is_axis:
                    if display.control[0] == 'd':
                        display.println('Binary axis, press both corresponding buttons to assign')
                    else:
                        display.println('Analogue axis, move control to full extent to assign')
                    display.println('SPACE to toggle inversion, BACKSPACE to toggle enable / disable')

                try:
                    key = screen.getkey()
                    if key in button_keys and button_keys.index(key) < len(BUTTON_NAMES):
                        profiler.reset()
                        display.control = BUTTON_NAMES[button_keys.index(key)]
                    elif key in axis_keys and axis_keys.index(key) < len(AXIS_NAMES):
                        profiler.reset()
                        display.control = AXIS_NAMES[axis_keys.index(key)]
                    elif key == ' ' and display.control_is_axis:
                        profile.toggle_axis_invert(name=display.control)
                    elif key == 'KEY_BACKSPACE':
                        profiler.reset()
                        if display.control_is_button:
                            profile.set_button(name=display.control, code=None)
                        elif display.control_is_axis:
                            profile.toggle_axis_enable(name=display.control)
                    elif key == 'KEY_LEFT':
                        profiler.reset()
                        display.select_previous_control()
                    elif key == 'KEY_RIGHT':
                        profiler.reset()
                        display.select_next_control()
                except curses.error:
                    # Expect this when the key check times out
                    pass

        except KeyboardInterrupt:
            profiler_thread.stop()
            pass

    return curses_main


class DisplayState:

    def __init__(self, screen, profile, profiler, axis_keys, button_keys):
        self.screen = screen
        self.profile = profile
        self.profiler = profiler
        self.axis_keys = axis_keys
        self.button_keys = button_keys
        self.line = 0
        self.all_controls = [*BUTTON_NAMES, *AXIS_NAMES]
        self.control = self.all_controls[0]
        # Disable echo to terminal
        curses.noecho()
        # Hide the cursor
        curses.curs_set(0)
        # Contrast colour for UI
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        # Highlight
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        # Enable colour
        curses.start_color()
        # Clear the screen
        screen.clear()
        # Enable key events for special keys i.e. arrows, backspace
        screen.keypad(True)

    def start(self):
        self.screen.clear()
        self.line = 0

    def println(self, string, contrast=False):
        try:
            if contrast:
                self.screen.addstr(self.line, 0, string, curses.color_pair(1))
            else:
                self.screen.addstr(self.line, 0, string)
        except curses.error:
            pass
        self.line += 1

    def newline(self):
        self.line += 1

    def print_header(self, string):
        s = '——' + string
        s += '—' * (80 - len(s))
        self.println(s, True)

    @property
    def control_is_button(self):
        return self.control in BUTTON_NAMES

    @property
    def control_is_axis(self):
        return self.control in AXIS_NAMES

    def select_next_control(self):
        control_index = self.all_controls.index(self.control)
        self.control = self.all_controls[(control_index + 1) % len(self.all_controls)]

    def select_previous_control(self):
        control_index = self.all_controls.index(self.control)
        self.control = self.all_controls[(control_index - 1) % len(self.all_controls)]

    def select_next_row(self):

        pass

    def select_previous_row(self):
        pass

    def show_axis(self, row, col, axis):
        control = self.axis_keys[AXIS_NAMES.index(axis)]
        try:
            if self.control == axis:
                # Pick up either all changes, or binary changes only if the axis starts with 'd'
                changes = self.profiler.axis_changes if axis[0] != 'd' else self.profiler.binary_axis_changes
                if changes:
                    # Currently editing this axis, show live information if available
                    code, min_value, max_value, current_value = changes[0]
                    self.profile.set_axis_range(axis, code, min_value, max_value)
                    rep = self.profile.axes[axis].build_repr(axis=axis, control=control, current_value=current_value)
                else:
                    rep = self.profile.axes[axis].build_repr(axis=axis, control=control)
                self.screen.addstr(row, col, rep, curses.color_pair(2))
            else:
                self.screen.addstr(row, col, self.profile.axes[axis].build_repr(axis=axis, control=control))
        except curses.error:
            pass

    def show_button(self, row, col, button):
        control = self.button_keys[BUTTON_NAMES.index(button)]
        try:
            if self.control == button:
                if self.profiler.last_button_pressed:
                    self.profile.set_button(button, self.profiler.last_button_pressed)
                rep = f'[{control}] {button} : {self.profile.buttons[button] or "---"}'
                self.screen.addstr(row, col, rep, curses.color_pair(2))
            else:
                rep = f'[{control}] {button} : {self.profile.buttons[button] or "---"}'
                self.screen.addstr(row, col, rep)
        except curses.error:
            pass
