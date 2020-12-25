.. _getting_started-setup:

=====
Setup
=====

Setup of SnakeFace if you are the one doing the installation (an admin or user in a virtual environment) comes down to setting parameters in a settings.yml file that sits alongside the
installation (meaning you need write access to it) and then having an ability to
override settings via the environment. You can generally use the same parameters across deployment types.


Authentication
==============

If you don't define an authentication backend (e.g., plugins like ldap, saml, or
OAuth 2), then the default authentication model for Snakeface is akin to a jupyter notebook.
