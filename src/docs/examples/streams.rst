.. _example_stream:

Streaming Axis and Button Hold values
=====================================

Some other APIs, most notably Gpiozero_ can configure devices to read from iterators over data such as axis values. To
use this facility we need to be able to produce generators (iterators which work over lazily evaluated, potentially
infinite, sets of data) containing streams of axis and button hold values. These generators can then be set as the
source for anything in e.g. Gpiozero which has a SourceMixin_ defined, including motors and similar.

The example below doesn't use Gpiozero, but instead shows how a stream of x,y values from the left analogue stick is
created, then used by an infinite loop to print those values. The loop only exits with a StopIteration exception when
the controller disconnects. This is also an example of explicitly creating and binding a controller, rather than using
the resource abstraction shown in the other examples.

.. literalinclude:: ../../../scripts/streams.py
    :language: python
    :linenos:

Note particularly that there's only one call to create the stream, on line 21, and that afterwards this is just like any
other iterable thing in Python, each time around the loop the next value (in this case a tuple of lx and ly axis values)
is taken off the stream.

.. _Gpiozero: http://gpiozero.readthedocs.io/en/stable/index.html

.. _SourceMixin: http://gpiozero.readthedocs.io/en/stable/api_generic.html#sourcemixin