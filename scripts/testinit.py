"""
Simple joystick test, waits to bind to a PS3 controller and prints out its axes
"""

from time import sleep

from approxeng.input.asyncorebinder import ControllerResource
from approxeng.input.dualshock4 import DualShock4, CONTROLLER_NAME

while 1:
    try:
        with ControllerResource(controller=DualShock4(), device_name=CONTROLLER_NAME) as joystick:
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
