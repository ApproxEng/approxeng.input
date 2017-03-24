from approxeng.input.asyncorebinder import ControllerResource
from approxeng.input.debug import DebugController
from approxeng.input.dualshock4 import DualShock4
from time import time, sleep

last_print = time()

ds4 = DualShock4(dead_zone=0.05)
debug = DebugController(print_axes=True, print_buttons=True)
print_joystick = False

while 1:
    try:
        with ControllerResource(controller=ds4) as joystick:
            print "Found joystick {}".format(joystick)
            while 1:
                now = time()
                if now - last_print > 0.2 and print_joystick:
                    last_print = now
                    print joystick
    except IOError:
        print "No joystick yet."
        sleep(0.5)
