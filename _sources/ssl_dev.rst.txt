Local Data Provider Development Mode
====================================

.. warning::
    Please note! This should not be used in production. It is solely to help make your life simpler, when developing a
    :term:`data provider`, by allowing you to run everything locally with full SSL support enabled.

You may want to run your `Flask`_ app locally when testing, but the security requirements of |OE3| mean you really need
to use HTTPS, and have everything validate correctly. In addition, to make use of the `AccessTokenValidator` you need
any test clients to present valid client certificates. This can all get rather messy, so this library includes a couple
of helper functions to allow you to run your app locally using Flask's built-in development server.

Obtaining a valid server certificate
------------------------------------

To run on ``localhost`` or ``127.0.0.1`` you will need a corresponding SSL certificate, and you'll need to get the
signing chain for that certificate into Python's list of trusted CAs. For this we recommend the minimal CA project
that can be found at https://github.com/jsha/minica - this will create a certificate for your server as well as a root
certificate. You need to add this root certificate to the ``certifi`` CA, assuming your root is called ``minica.pem``
(the default) you can install it with:

.. code-block:: bash

    > cat minica.pem >> `python3 -m certifi`

This must be done on any virtual environment that's going to make calls *to* your server as it will be used when
validating the server certificate. Ensure that you have any virtual environment activated before running this command,
it will install into whatever python is currently active.

Running in dev mode
-------------------

Once you have a certificate for your server to hand, and have installed the appropriate root cert, you can use the
helper functions in `ib1.openenergy.support.flask_ssl_dev` to run your app.

The function `get_command_line_ssl_args` can be used to parse command line arguments and add help functionality, putting
this in your app then calling it with ``myapp.py --help`` will produce output similar to this:

.. code-block:: bash

    tom@sparkles:~/Desktop/certs$ python myapp.py --help
    usage: app.py [-h] [-sk SERVER_PRIVATE_KEY] [-sc SERVER_CERTIFICATE] [-ck CLIENT_PRIVATE_KEY]
                  [-cc CLIENT_CERTIFICATE] [-cid CLIENT_ID]

    optional arguments:
      -h, --help            show this help message and exit
      -sk SERVER_PRIVATE_KEY, --server_private_key SERVER_PRIVATE_KEY
                            Server private key file, default "127.0.0.1/key.pem"
      -sc SERVER_CERTIFICATE, --server_certificate SERVER_CERTIFICATE
                            Server certificate file, default "127.0.0.1/cert.pem"
      -ck CLIENT_PRIVATE_KEY, --client_private_key CLIENT_PRIVATE_KEY
                            Client private key file, default "a.key"
      -cc CLIENT_CERTIFICATE, --client_certificate CLIENT_CERTIFICATE
                            Client certificate file, default "a.pem"
      -cid CLIENT_ID, --client_id CLIENT_ID
                            OAuth2 client ID for calls made from this app

You can set defaults for certificate locations and client ID in the call to `get_command_line_ssl_args`. This function
produces a `SSLOptions` object from which properties can be extracted to actually run your app with `run_app`

The example data provider from `Providing OE Shared Data`, repeated below, uses `get_command_line_ssl_args` on line 12
to get locations of certificate files as well as the OAuth2 client ID, these are then passed both to the
`AccessTokenValidator` on line 18 and the call to actually run the app with `run_app` on line 40.

.. literalinclude:: ../../examples/app.py
    :language: python
    :linenos:

.. _Financial Grade API: https://openid.net/wg/fapi/
.. _Requests: https://docs.python-requests.org/en/master/
.. _Flask: https://flask.palletsprojects.com/en/1.1.x/
.. _gunicorn: https://gunicorn.org/
.. _NGINX: https://www.nginx.com/