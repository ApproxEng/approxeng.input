Providing OE Shared Data
========================

To participate in the |OE3| ecosystem as a provider of shared data, a :term:`data provider` (|DP|) must expose an HTTP
|API| secured by the `Financial Grade API`_ (FAPI) standard. This standard is complex, building as it does on top of
OAuth2 and then OpenID Connect, but within the context of Open Energy a provider must:

1. Require MTLS, requesting a client certificate as part of any API call
2. Require a bearer token
3. Validate the supplied token before any other processing is performed

In our case, the third of the above is done by calling the token introspection endpoint of our authorization server and
parsing and processing the response to ensure that the supplied token is valid, live, and belongs to the presenting
client. Only once these checks have passed should your API process the request (and it may then make use of other
information from the token introspection response to determine access control if appropriate).

To simplify this process, the library provides a class `ib1.openenergy.support.AccessTokenValidator` which encapsulates
the process of checking that a request has presented a valid access token. When correctly instantiated, the
`AccessTokenValidator.introspects` can be used as a decorator on regular `Flask`_ routes to automatically perform these
checks before your route handler is called.

Example data provider
---------------------

The example below shows the simplest possible secure application. It configures an instance of
`AccessTokenValidator` with:

* ``introspection_url`` : The URL of the token introspection endpoint on the authorization server
* ``client_id`` : OAuth2 client ID used when making requests to the introspection endpoint
* ``private_key`` : Location on disk of the private key used when making requests to the introspection endpoint
* ``certificate`` : Location on disk of the certificate used when making requests to the introspection endpoint

.. note::
    Although we're configuring a server here, we need to set up the validator with the necessary credentials to access
    the authorization server as a **client**, hence the ``client_id``, ``private_key`` and ``certificate`` arguments.
    If you're a participant in Open Energy you should already have this information, if you do not then please ask us!

Client certificate extraction
#############################

Part of the validation process is to check that the token was originally issued to the same client as is now trying to
use it. To do this we compare the thumbprint of the presented client certificate with the corresponding claim in the
token introspection response, but there is no standard way for an application server to access the client certificate.

In this example, we are using the default mechanism designed to work with the built-in local SSL runner (see
`Local Data Provider Development Mode`) but in any production context you will not be using this and will need to
configure some kind of certificate pass-through. This is typically done by terminating the MTLS connection elsewhere
and configuring that termination point to push the certificate information into a header which is then accessible to
your application.

To support this, the `AccessTokenValidator` takes an additional, optional, initialisation argument:

* ``client_cert_parser`` : a Zero argument function which returns an instance of `cryptography.x509.Certificate`
  containing the presented client certificate.

Using the validator
###################

The configured `AccessTokenValidator` is used to decorate a simple flask route within the app. The decorator takes an
optional ``scope`` argument, if provided then only tokens containing the specified scope will be regarded as valid.

.. literalinclude:: ../../examples/app.py
    :language: python
    :linenos:

The simple route defined on line 26 has been decorated with ``@validator.introspects(scope='directory:software')``,
within the ``@app.route('/')`` decorator. When this route is accessed, the library will examine the request, checking
for presence of a client certificate, presence of a bearer token, then passing that token to the introspection endpoint
and checking the response for validity. The response is cached for 60 seconds by the library for performance, so
repeated calls from the same client will only be validated once (although token liveness is calculated per call based
on the expiry time specified in the introspection response).

Within your decorated route, you can access the actual introspection response through `flask.g` as
``flask.g.introspection_response``, you may need to use this to determine whether to grant the client access to a
given piece of data it's requesting within that route.

.. note::
    This example also includes the necessary extra logic to run locally in dev mode, see
    `Local Data Provider Development Mode` for more details. Normally you wouldn't need the logic on line 12, or the
    command to run the app on line 40 as you'd be running the `Flask`_ app in a server such as `gunicorn`_ and behind a
    front-end system like `NGINX`_.

.. _Financial Grade API: https://openid.net/wg/fapi/
.. _Requests: https://docs.python-requests.org/en/master/
.. _Flask: https://flask.palletsprojects.com/en/1.1.x/
.. _gunicorn: https://gunicorn.org/
.. _NGINX: https://www.nginx.com/