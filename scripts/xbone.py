from time import time, sleep

from approxeng.input.asyncorebinder import ControllerResource
from approxeng.input.xboxone import XBoxOneSPad

last_print = time()
print_joystick = False

while 1:
    try:
        with ControllerResource(controller=XBoxOneSPad(),
                                device_name='Xbox Wireless Controller') as joystick:
            print "Found joystick {}".format(joystick)
            while 1:
                now = time()
                if now - last_print > 0.2 and print_joystick:
                    last_print = now
                    print joystick
    except IOError:
        print "No joystick yet."
        sleep(0.5)
