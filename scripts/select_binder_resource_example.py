from time import sleep

from approxeng.input.selectbinder import ControllerResource

while 1:
    try:
        # Attempt to acquire a controller. If there's more than one we'll get one of them, if there aren't
        # any we'll throw an IOError. Assuming we succeed, the controller will be initialised, a new thread will be
        # created in the background to pull events out of evdev and update the state of the controller object, and all
        # the buttons and axes will be available as properties of 'controller'
        #
        # For most controllers, the same driver class can be used whether the controller is connected over bluetooth or
        # over a USB cable. For controllers where this isn't the case there will be different driver classes for each
        # kind of connection.
        #
        # In this particular case we loop forever, but if we weren't the thread would be stopped when leaving the 'with'
        # block, there's no explicit cleanup needed.
        #
        # The print_events can be set to show evdev events as they're received, whether handled or not. Any additional
        # keyword args are passed through to the constructor of the controller class, so if you know exactly what class
        # you're using (because you've supplied a controller_class argument here) you can provide controller-specific
        # configuration in your resource. Setting controller_class to None just means 'find whatever joystick you can'
        with ControllerResource(print_events=False, controller_class=None, hot_zone=0.0, dead_zone=0.1) as controller:
            # We've got a joystick, loop forever
            while 1:
                # The next line is used to extract all buttons which were pressed since the last time this call was
                # made. This means you don't have to worry about whether you're catching buttons while they're held
                # down - this will catch a case where you check, then the user clicks and releases the button, and then
                # you check again. Even though the click happened while your code was off doing something else, the
                # event handling thread has monitored it and stored that the click happened. You can use methods on the
                # approxeng.input.ButtonPresses instance this returns to query for specific buttons (by their standard
                # name) or as in this case to see whether anything was pressed and print out the list of presses if so.
                button_presses = controller.buttons.get_and_clear_button_press_history()
                if button_presses.has_presses():
                    # Printing the ButtonPresses object prints a list of the snames of buttons which were pressed
                    print(button_presses)
                # The controller.axes property contains all analogue (and potentially digital) axes of your controller.
                # As with the button presses these are updated behind the scenes, with dead and hot zones applied,
                # centre and range calibration and normalisation to either -1 to 1 (for centred axes) or 0 to 1 for
                # triggers. The convenience method active_axes will return all axis objects which aren't at their
                # resting position, but you can use other methods on this to get the corrected value for a specific
                # axis.
                for axis in controller.axes.active_axes():
                    # Printing an axis object (CentredAxis, TriggerAxis or BinaryAxis) will print a summary of the
                    # axis including its current corrected value
                    print(axis)
                # Sleep for a tenth of a second - spamming the console with print messages can upset the event reading
                # loop. In real cases your code will be off doing other things and you probably won't want to have
                # explicit delays!
                sleep(0.1)
    except IOError:
        # No controller, so print out a message and wait for another second before trying again
        print('No controller found yet')
        sleep(1)
