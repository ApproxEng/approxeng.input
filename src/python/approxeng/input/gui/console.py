import curses
import logging
import pprint
from time import sleep

import approxeng.input.sys as sys
from approxeng.input.controllers import print_devices, find_all_controllers
from approxeng.input.selectbinder import ControllerResource


def sys_scan():
    logging.basicConfig(level=logging.DEBUG)
    pp = pprint.PrettyPrinter(indent=2, width=100)
    pp.pprint(sys.scan_system())


def list_devices():
    logging.basicConfig(level=logging.DEBUG)
    print_devices()


def list_discoveries():
    logging.basicConfig(level=logging.DEBUG)
    for discovery in find_all_controllers():
        logging.info('found a thing')
        print(discovery)
        logging.info('done finding a thing')


def show_controls():
    def main(screen):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.start_color()
        last_presses = None

        def red(s):
            screen.addstr(s, curses.color_pair(1))

        def green(s):
            screen.addstr(s, curses.color_pair(2))

        def yellow(s):
            screen.addstr(s, curses.color_pair(3))

        def magenta(s):
            screen.addstr(s, curses.color_pair(4))

        # Loop forever
        while True:
            try:
                with ControllerResource() as joystick:
                    while joystick.connected:
                        # Check for presses since the last time we checked
                        joystick.check_presses()

                        screen.clear()

                        if joystick.has_presses:
                            last_presses = joystick.presses

                        # Print most recent presses set
                        screen.addstr(0, 0, 'last presses:')
                        if last_presses is not None:
                            for button_name in last_presses:
                                green(' {}'.format(button_name))

                        # Print axis values
                        screen.addstr(1, 0, 'axes:')
                        for axis_name in joystick.axes.names:
                            screen.addstr(' {}='.format(axis_name))
                            axis_value = joystick[axis_name]
                            if not isinstance(axis_value, tuple):
                                text = '{:.2f}'.format(axis_value)
                                if axis_value > 0:
                                    green(text)
                                elif axis_value < 0:
                                    red(text)
                                else:
                                    yellow(text)
                            else:
                                x, y = axis_value
                                text = f'({x:.2f},{y:.2f})'
                                magenta(text)

                        # Print button hold times
                        screen.addstr(2, 0, 'hold times:')
                        for button_name in joystick.buttons.names:
                            hold_time = joystick[button_name]
                            if hold_time is not None:
                                screen.addstr(' {}='.format(button_name))
                                green('{:.1f}'.format(hold_time))

                        # Print some details of the controller
                        screen.addstr(3, 0, 'controller class: {}'.format(type(joystick).__name__))
                        screen.addstr(4, 0, 'controller name: {}'.format(joystick.__repr__()))
                        battery_level = joystick.battery_level
                        if battery_level:
                            screen.addstr(5, 0, 'battery_level: {:.2f}'.format(joystick.battery_level))
                        screen.addstr(6, 0, pprint.pformat(joystick.controls, indent=2))

                        screen.refresh()
                        sleep(0.05)
            except IOError:
                screen.clear()
                screen.addstr(0, 0, 'Waiting for controller')
                screen.refresh()
                sleep(1.0)
            except KeyboardInterrupt:
                exit(0)

    curses.wrapper(main)
