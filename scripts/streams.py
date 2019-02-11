from time import sleep

from approxeng.input.controllers import find_matching_controllers, ControllerRequirement
from approxeng.input.selectbinder import bind_controllers

discovery = None

# Look for an attached controller, requiring that it has 'lx' and 'ly' controls, looping until we find one.
while discovery is None:
    try:
        discovery = find_matching_controllers(ControllerRequirement(require_snames=['lx', 'ly']))[0]
    except IOError:
        print('No suitable controller found yet')
        sleep(0.5)

# Bind the controller to the underlying event stream, returning a function used to tidy up
unbind_function = bind_controllers(discovery, print_events=False)

try:
    # Get a stream of values for the left stick x and y axes. If we were using robot code from gpio.zero we could
    # set the controller.stream[...] as a source, as sources are just iterators which produce sequences of values
    for lx, ly in discovery.controller.stream['lx', 'ly']:
        print('Left stick: x={}, y={}'.format(lx, ly))
        sleep(0.1)
except StopIteration:
    # Raised when the stream ends
    pass

# Tidy up any resources (threads, file handles) used by the binder
unbind_function()
