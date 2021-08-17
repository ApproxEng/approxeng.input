Accessing OE Shared Data
========================

In order to access an |OE3| shared data API, a client must comply with the `Financial Grade API`_ specification, in
particular it must:

1. Connect using MTLS, presenting a client certificate when requested
2. Present a valid OAuth2 bearer token previously obtained from the authorization server

Tokens are short-lived, opaque, and bound to the certificate of the client which requested them.

This library provides a class `ib1.openenergy.support.FAPISession` which automatically acquires tokens when needed (on
first access, or when a token has expired), and configures the necessary header information required to successfully
call a protected endpoint.

.. note::
    To make requests, you must have previously generated an appropriate private key, uploaded the corresponding certificate
    signing request to our authorization server, and downloaded the resultant certificate. You will also need the OAuth
    client ID corresponding to this certificate.

Once you have this information (if you are one of our trial users you should already know how to obtain this, if not
please ask us!) you can configure the `FAPISession` with:

* ``private_key`` : The file path of the private key
* ``certificate`` : The file path of the certificate
* ``client_id`` : The OAuth client ID
* ``token_url`` : The URL of the token endpoint of the authorization server
* ``requested_scopes`` : The OAuth2 scopes to request for any tokens. This should be a string, if multiple scopes are
  required they should be separated by spaces within this string

Once configured, it exposes a property `session <FAPISession.session>`. This is a `Requests`_
`Session <requests.Session>` instance - use this the same way you'd use it in any other context (i.e. with
`get <requests.Session.get>`, `post <requests.Session.post>` etc), the library will take care of token acquisition and
transport, using the key pair provided both to call the token endpoint and to call the actual resource server.

Example client
--------------

The code below shows how to set up the `FAPISession`, enable better HTTP logging (including timestamps), and make a call
to the trivial data provider defined in the `Example data provider`:

.. literalinclude:: ../../examples/app_client.py
    :language: python
    :linenos:

As you can see, other than the instantiation of the `FAPISession` on line 12, this is identical to using `Requests`_ to
access an unsecured HTTP server, all the token management is handled automatically for you.

.. _Financial Grade API: https://openid.net/wg/fapi/
.. _Requests: https://docs.python-requests.org/en/master/
.. _Flask: https://flask.palletsprojects.com/en/1.1.x/