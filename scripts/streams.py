from approxeng.input.controllers import find_any_controller
from approxeng.input.selectbinder import bind_controller
from time import sleep

devices, controller = None, None

# Look for an attached controller, looping until we find one.
while controller is None:
    try:
        devices, controller, physical_address = find_any_controller()
    except IOError:
        print('No controller found yet')
        sleep(0.5)

# Bind the controller to the underlying event stream, returning a function used to tidy up
unbind_function = bind_controller(devices=devices, controller=controller, print_events=False)

try:
    # Get a stream of values for the left stick x and y axes. If we were using robot code from gpio.zero we could
    # set the controller.stream[...] as a source, as sources are just iterators which produce sequences of values
    for lx, ly in controller.stream['lx','ly']:
        print('Left stick: x={}, y={}'.format(lx, ly))
        sleep(0.1)
except StopIteration:
    # Raised when the stream ends
    pass

# Tidy up any resources (threads, file handles) used by the binder
unbind_function()