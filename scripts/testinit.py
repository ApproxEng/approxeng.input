"""
Simple joystick test, waits to bind to one and prints out its axes
"""

from approxeng.input.sixaxis import SixAxisResource, BUTTON_CIRCLE

while 1:
    try:
        with SixAxisResource(bind_defaults=False) as joystick:
            while 1:
                presses = joystick.buttons.get_and_clear_button_press_history()
                if len(presses) > 0:
                    print presses
                held_time = joystick.buttons.is_held(BUTTON_CIRCLE)
                if held_time is not None:
                    print "Circle held for {} seconds".format(held_time)

    except IOError:
        print "No joystick yet."
