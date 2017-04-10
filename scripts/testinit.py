"""
Simple joystick test, waits to bind to a PS4 controller then shows button presses and hold times for the circle button
"""

from time import sleep

from approxeng.input.dualshock4 import DualShock4
from approxeng.input.selectbinder import ControllerResource

while 1:
    try:
        with ControllerResource(controller_class=DualShock4) as joystick:
            print "Found joystick {}".format(joystick)
            while 1:
                sleep(1)
                presses = joystick.buttons.get_and_clear_button_press_history()
                if len(presses.buttons) > 0:
                    print presses
                held_time = joystick.buttons.is_held_name('circle')
                if held_time is not None:
                    print "Circle held for {} seconds".format(held_time)
                print joystick
    except IOError:
        print "No joystick yet."
        sleep(0.3)
