import logging
from time import sleep

from approxeng.input.dualshock4 import DualShock4
from approxeng.input.selectbinder import ControllerResource, ControllerRequirement, ControllerNotFoundError

logging.basicConfig(level=logging.DEBUG)

while True:
    hue = 0.0
    try:
        # Force waiting for a DS4 controller, as that's the only one with the call
        # to set the light bar in this way.
        with ControllerResource(ControllerRequirement(require_class=DualShock4)) as ds4:
            while ds4.connected:
                # Set the hue of the light bar, saturation and value default to 1.0
                ds4.set_leds(hue=hue)
                # Pause for a bit, advance hue, and go around again
                sleep(0.02)
                hue = hue + 0.01
                if hue > 1.0:
                    hue = 0.0
                    # Vibrate the controller for 200ms every time we loop round the hue wheel
                    ds4.rumble(milliseconds=200)
    except ControllerNotFoundError:
        # No DS4 controller found, wait for a bit and try again
        print('Waiting for a DS4 controller connection')
        sleep(1)
