from approxeng.input.selectbinder import bind_controller
from time import sleep
from approxeng.input.controllers import find_controllers

d = find_controllers()[0]

controller = d['controller']
devices = d['devices']

print(controller)

bind_controller(devices, controller)

while True:
    sleep(0.5)
    for axis in controller.axes.active_axes():
        print(axis)