.. _getting_started-auth:


Authentication
==============

If you don't define an authentication backend (e.g., plugins like ldap, saml, or
OAuth 2), then the default authentication model for Snakeface is akin to a jupyter notebook.
You'll be given a token to enter in the interface, and this will log you in. This
is currently the only authentication supported, as we haven't developed the other
deployment types.
