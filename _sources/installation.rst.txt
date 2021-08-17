Installation
============

The library requires Python 3.8 or newer. Use of a `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_
is strongly recommended.

Installing with pip
-------------------

.. note::
    This library is still alpha, and has not yet been pushed to PyPI. If you need to use it in its current form please
    install from source as described below.

.. code-block:: bash

    > pip3 install ob1.openenergy.support

Installing from source
----------------------

This will install the library in development mode - this means any changes you make to source files in your local git
repository will be immediately reflected in the contents of the library as used by other code. In other respects this
behaves identically to installing with either ``python3 setup.py install`` or by installing via ``pip`` as shown above.

.. code-block:: bash

    > git clone git@github.com:icebreakerone/open-energy-python-infrastructure.git
    > cd open-energy-python-infrastructure/src/python
    > python3 setup.py develop

Adding OE3 root certificates
----------------------------

The certificates used to mutually authenticate between data and service providers within |OE3| are signed by our
authorization server. In order to validate correctly, you need to add the root and intermediate signing certificates
to the ``certifi`` CA file used by Python (Python does not use the operating system CA store).

Once ``certifi`` is installed (it will be pulled in as a dependency when you install this library) you can do the
following on the command line to concatenate the necessary files to its store, this will fetch the current UAT root and
signing certificates from this repository, then append them to the file location returned by ``python3 -m certifi``

.. note::

    You must activate any virtual environment before running this command

.. code-block:: bash

    > curl https://raw.githubusercontent.com/icebreakerone/open-energy-python-infrastructure/main/certificates/raidiam_certificate_chain.pem >> `python3 -m certifi`

If you need to reset your certifi installation, or if it is ever updated (it's good practice to check periodically for
changes to this library as this is the way root CAs are provided or invalidated for Python code) you will need to redo
the above command. For consistency, it's best to explicitly uninstall then reinstall the certifi library, that way you
know you're always starting from a clean, unmodified, CA file:

.. code-block:: bash

    > pip3 uninstall certifi
    > pip3 install certifi
    > curl https://raw.githubusercontent.com/icebreakerone/open-energy-python-infrastructure/main/certificates/raidiam_certificate_chain.pem >> `python3 -m certifi`
