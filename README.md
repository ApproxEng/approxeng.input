# approxeng.input

A Python (2 or 3) library to handle game controllers. At the moment it can work with the following:

1) DualShock3, as used by the Sony Playstation 3
2) DualShock4, as used by the Sony Playstation 4
3) XBox One, the most recent version with bluetooth

See the full documentation [here](http://approxeng.github.io/approxeng.input/)

Get the code using pip:

```
> pip install approxeng.input
```

Note - you may need to install some prerequisites first, and this will only work on Linux based 
operating systems. See the full docs for more details.

All three controllers can be used either over USB or bluetooth, the library handles event management 
and lets you simply query an object model to get button presses, hold times, and axis values. It also
deals with analogue axis concerns such as dead and hot zones, centering, for both triggers (where the
controller has analogue triggers) and stick inputs.

Controls are references by a set of standard names, so you don't need to code against a specific
controller - it should be possible to write code using a PS3 controller then pick up a PS4 or XBoxOne
device and have it just work out of the box (with the exception that if you rely e.g. on the PS4
analogue triggers you won't get those on the PS3 controller as it doesn't have them)

This library, or previous versions thereof, has been used successfully by several PiWars teams, 
it's focused more at robotics than game creation (there's no support at the moment for multiple
controllers for example).

