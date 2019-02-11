import curses
from time import sleep

from approxeng.input.controllers import ControllerRequirement, ControllerNotFoundError
from approxeng.input.selectbinder import ControllerResource


def main(screen):
    curses.curs_set(False)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.start_color()

    def red(s):
        screen.addstr(s, curses.color_pair(1))

    def green(s):
        screen.addstr(s, curses.color_pair(2))

    def yellow(s):
        screen.addstr(s, curses.color_pair(3))

    while True:
        try:
            # Bind to controllers. By specifying the requirements parameter and passing in a list of two requirements
            # objects we indicate that we must have at least two connected controllers, but that we don't care what they
            # are. We could have specified more parameters to the ControllerRequirements objects, in which case they
            # would act as filters. So, you could, for example, require the first controller to be a PS3 and the second
            # a PS4, or, more usefully, the two halves of the joycon!
            with ControllerResource(ControllerRequirement(), ControllerRequirement()) as (joystick_a, joystick_b):

                # When using this form, all controllers are connected, or they're all disconnected, so only need
                # to check one of them. The logic is that if you needed two controllers, and you now only have
                # one, this should be an error and you shouldn't just continue.
                while joystick_a.connected:
                    screen.clear()

                    def print_axes(joystick, row, title):

                        screen.addstr(row, 0, '{} axes:'.format(title))
                        for axis_name in joystick.axes.names:
                            screen.addstr(' {}='.format(axis_name))
                            axis_value = joystick[axis_name]
                            text = '{:.2f}'.format(axis_value)
                            if axis_value > 0:
                                green(text)
                            elif axis_value < 0:
                                red(text)
                            else:
                                yellow(text)

                    # Print the live axes of both connected controllers
                    print_axes(joystick_a, 1, 'A')
                    print_axes(joystick_b, 2, 'B')

                    # We're not bothering with buttons here, if you did you'd need to check for button presses for
                    # each joystick individually.

                    screen.refresh()
                    sleep(0.05)

        except ControllerNotFoundError:
            screen.clear()
            screen.addstr(0, 0, 'Waiting for 2 matching controllers')
            screen.refresh()
            sleep(1.0)


curses.wrapper(main)
