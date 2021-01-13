Adding support for a new controller type
========================================

The library supports a number of controllers but it's quite possible, given the variety of cheap clones on the market,
that your particular controller isn't one of them. You have a few options, depending on the scenario you find yourself
in. Firstly though you'll need both product and vendor IDs for your device - these are allocated by the USB consortium
so will definitely not be the same for a clone device as for an original one, for example.

Finding your product and vendor ID
----------------------------------

Once you have a controller paired over bluetooth, or, in the case of those with specific dongles, otherwise connected,
you can run the `scripts/list_devices.py` to print out a list of all connected devices, including the vendor and product
identifiers. For example, with my XBox One controller paired and connected I see this:

.. code-block:: bash

    (viridia-env) tom@Ogre ~/git/approxeng.input/scripts $ python list_devices.py
    { 'bus': 5,
      'fn': '/dev/input/event14',
      'name': 'Xbox Wireless Controller',
      'phys': '5c:f3:70:66:5c:e2',
      'product': 736,
      'vendor': 1118,
      'version': 2307}

In general this should show you enough information to identify the controller you've just connected and get the details.

Clones of a supported controller
--------------------------------

If you have a controller which is an exact copy of one the library supports, but isn't autodetected, you can sub-class
the existing one and specify the appropriate return values for `registration_ids`

Writing a new controller class
------------------------------

It's possible you have a controller which is completely different to the ones the library already supports. This might
be because it's something we've just never got our hands on, or because the manufacturer has decided to produce a clone
controller with completely different codes for buttons or axes (it happens!). In this case you'll need to create a new
subclass of :class:`~approxeng.input.Controller` and use the mechanism above to register it. Fortunately this is fairly
simple. First create your class, this won't include any button or axis bindings, we'll add these later:

.. code-block:: python

    from approxeng.input import Controller

    MY_VENDOR_ID = ...
    MY_PRODUCT_ID = ...

    __all__ = ['MyNewController']

    class MyNewController(Controller):
        """
        Driver for my new controller type
        """

        def __init__(self, dead_zone=0.05, hot_zone=0.0):
            """
            Axis and button definitions for my new controller class

            :param float dead_zone:
                Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
            :param float hot_zone:
                Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
            """
            super(MyNewController, self).__init__(controls=[],
                                                  dead_zone=dead_zone,
                                                  hot_zone=hot_zone)

        @staticmethod
        def registration_ids():
            """
            :return: list of (vendor_id, product_id) for this controller
            """
            return [(MY_VENDOR_ID, MY_PRODUCT_ID)]

        def __repr__(self):
            return 'My new controller'

This is a fairly useless controller, because it doesn't have any buttons or axes, but it will get us to the point where
the library tries to send events to it, and that's important because when an event is received and not processed by the
controller class we just print it to the console. This means that if you register your new class with its associated
vendor and product IDs (as above) and run the `scripts/select_binder_resource_example.py` script you should start seeing
messages about unknown axes and buttons. You can then go back to this class definition and use this information to add
controls until you're not getting any of these 'missing control' messages and everything's working.

Controls are all added to the `controls` parameter of the constructor, you should look at the documentation for the
various axis and button classes to see what they take as arguments, these are currently:

- :class:`~approxeng.input.CentredAxis` for analogue axes which have a resting point in the centre of their range.

- :class:`~approxeng.input.TriggerAxis` for analogue axes which have a resting point at one end of their range.

- :class:`~approxeng.input.BinaryAxis` for analogue axes which are really pairs of buttons, both the PS4 and XBox One
  controllers use this for their direction pads, the buttons on these pads don't appear as buttons in the event stream
  but as an analogue axis which only ever takes the values -1, 0 or 1.

- :class:`~approxeng.input.Button` for buttons

You should take a look at the source for the existing controller classes, i.e.
:class:`~approxeng.input.xboxone.WirelessXBoxOneSPad` to see how these are used. For every control you need to know the
event code, for analogue axes you'll also need to know the range of values the controller can produce so the library
can normalise these to a -1.0 to 1.0, or 0.0 to 1.0 range. Check out the list of :ref:`sname-label` to make your new
controller class drop-in compatible with existing code, and let me know about it by raising either a pull request or a
new issue on github, I'm sure others would like to know about the new functionality!