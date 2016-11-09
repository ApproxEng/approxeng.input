"""
Simple joystick test, waits to bind to a PS3 controller and prints out its axes
"""

from approxeng.input.asyncorebinder import ControllerResource
from approxeng.input.dualshock3 import DualShock3, CONTROLLER_NAMES
from time import sleep

while 1:
    try:
        with ControllerResource(controller=DualShock3(), device_name=CONTROLLER_NAMES) as joystick:
            print "Found joystick {}".format(joystick)
            while 1:
                sleep(0.3)
                presses = joystick.buttons.get_and_clear_button_press_history()
                if len(presses) > 0:
                    print presses
                held_time = joystick.buttons.is_held(joystick.BUTTON_CIRCLE)
                if held_time is not None:
                    print "Circle held for {} seconds".format(held_time)
                print joystick
    except IOError:
        print "No joystick yet."
        sleep(0.3)
