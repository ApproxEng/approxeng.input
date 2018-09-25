from time import sleep

# All we need is a single import.
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
        # kind of connection. In this particular case we're binding to whatever controllers we can find rather than
        # specifying a particular one.
        #
        # The print_events can be set to show evdev events as they're received, whether handled or not. Any additional
        # keyword args are passed through to the constructor of the controller class, so if you know exactly what class
        # you're using (because you've supplied a controller_class argument here) you can provide controller-specific
        # configuration in your resource. Setting controller_class to None just means 'find whatever joystick you can'
        with ControllerResource(print_events=False, controller_class=None, hot_zone=0.1, dead_zone=0.1) as controller:

            # We've got a joystick, loop until it goes away. Print some details about the controller to the console.
            print('Found a controller, {}'.format(controller))

            # New in version 1.0.7 is detection for when a controller disconnects. This is handy, because it means we
            # know if your robot has run out of controller range (for example) and can stop it! Rather than looping
            # while True we loop while the 'connected' property on the controller is true.
            while controller.connected:

                # The next line is used to extract all buttons which were pressed since the last time this call was
                # made. This means you don't have to worry about whether you're catching buttons while they're held
                # down - this will catch a case where you check, then the user clicks and releases the button, and then
                # you check again. Even though the click happened while your code was off doing something else, the
                # event handling thread has monitored it and stored that the click happened. You can use methods on the
                # approxeng.input.ButtonPresses instance this returns to query for specific buttons (by their standard
                # name) or as in this case to see whether anything was pressed and print out the list of presses if so.
                button_presses = controller.check_presses()
                if button_presses.has_presses:
                    # Printing the ButtonPresses object prints a list of the snames of buttons which were pressed
                    print(button_presses)

                # The controller.axes property contains all analogue (and potentially digital) axes of your controller.
                # As with the button presses these are updated behind the scenes, with dead and hot zones applied,
                # centre and range calibration and normalisation to either -1 to 1 (for centred axes) or 0 to 1 for
                # triggers. The convenience method active_axes will return all axis objects which aren't at their
                # resting position, but you can use other methods on this to get the corrected value for a specific
                # axis.
                for axis in controller.axes.active_axes:
                    # Printing an axis object (CentredAxis, TriggerAxis or BinaryAxis) will print a summary of the
                    # axis including its current corrected value
                    print(axis)

                # Note - in real cases we probably want to get axis values even when they're not active, in which case
                # we would use the methods on the Controller class to get single or multiple corrected axis values by
                # standard name.

                # Sleep for a tenth of a second - spamming the console with print messages can upset the event reading
                # loop. In real cases your code will be off doing other things and you probably won't want to have
                # explicit delays!
                sleep(0.1)

            # We get here if controller.connected is False, this is set by the binder if it at any point fails to talk
            # to the controller. The result is that if you turn your controller off you should see a disconnection
            # message and the code will go back into looking for controllers.
            print('Controller disconnected!')

    except IOError:
        # This is thrown when attempting to create the controller resource if no controllers are present. In this case
        # we just pause for a second and try again.
        print('Waiting for controller...')
        sleep(1)
