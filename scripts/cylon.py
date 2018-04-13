from time import sleep

from approxeng.input.dualshock3 import DualShock3
from approxeng.input.wii import WiiRemotePro
from approxeng.input.selectbinder import ControllerResource

while True:
    active_led = 0
    try:
        # Force waiting for a DS3 or wii-pro controller
        with ControllerResource(controller_class=[DualShock3, WiiRemotePro]) as controller:
            while controller.connected:
                active_led = (active_led + 1) % 4
                for led_number in range(4):
                    if led_number == active_led:
                        controller.set_led(led_number + 1, 1)
                    else:
                        controller.set_led(led_number + 1, 0)
                sleep(0.2)
    except IOError:
        # No DS3 or Wii Pro controller found, wait for a bit and try again
        print('Waiting for a DS3 or Wii Pro controller connection')
        sleep(1)
