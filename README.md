# approxeng.input

A Python 3 library to handle game controllers. At the moment it can work with the following:

1) DualShock3, as used by the Sony Playstation 3
2) DualShock4, as used by the Sony Playstation 4
3) XBox One, the most recent version with bluetooth
4) Pi Hut, mixture of DualShock3 and 4
5) Rock Candy
6) Wii U Remote Pro
7) WiiMote
8) 8Bitdo SF30Pro
9) Wired 3dConnexion Spacemouse Pro (yes, really)
10) Steam Controller

See the full documentation [here](http://approxeng.github.io/approxeng.input/)

Note - versions prior to 2.2 had some level of support for Python2, but it's too much extra load to maintain this
library for two different language versions, so the current (and possibly some recent) versions are Python3 only. 
There's really no reason to use earlier Python versions in 2019 so hopefully this won't upset too many people.

Get the code using pip:

```
> pip install approxeng.input
```

You may need to install some prerequisites first, and this will only work on Linux based 
operating systems. See the full docs for more details.

Controls are references by a set of standard names, so you don't need to code against a specific
controller - it should be possible to write code using a PS3 controller then pick up a PS4 or XBoxOne
device and have it just work out of the box (with the exception that if you rely e.g. on the PS4
analogue triggers you won't get those on the PS3 controller as it doesn't have them)

This library, or previous versions thereof, has been used successfully by several PiWars teams, 
it's focused more at robotics than game creation, although there's no reason it couldn't be used in other contexts.

