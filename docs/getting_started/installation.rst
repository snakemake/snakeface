.. _getting_started-installation:

============
Installation
============

Snakeface can be installed and run from a virtual environment, or from a container.


Install via pip
===============

Snakeface can be installed with pip.

.. code:: console

    $ pip install snakeface


Once it's installed, you should be able to inspect the client!


.. code-block:: console

    $ snakeface --help


The first thing you should do is run ``snakeface init``, which will create a 
structure in your $HOME for snakeface settings, static files, and a local
database.

.. code-block:: console

    $ snakeface init
    Init complete. Settings are at /home/vanessa/.snakeface/settings.yml
    tree ~/.snakeface/
    /home/vanessa/.snakeface/
    ├── data
    └── static


At this point you can inspect the settings file generated, and make any updates.
When you run a notebook, this file will be updated with a secret key for the
server, so you should keep this settings file private.  If you ever
need to regenerate it from scratch, you can remove the file or entire
folder and re-run snakeface init. See :ref:`getting_started-settings` for more detail.


Virtual Environment
===================

First, clone the repository code.

.. code-block:: console

    $ git clone git@github.com:snakemake/snakeface.git
    $ cd snakeface


Then you'll want to create a new virtual environment, and install dependencies.

.. code-block:: console

    $ python -m venv env
    $ source env/bin/activate
    $ pip install -r requirements.txt


And install Snakeface (from the repository directly)

.. code:: console
 
    $ pip install -e .


Setup
=====

As a user, you most likely want to use Snakeface as an on demand notebook, so no additional
setup is needed other than installing the package. As we add more deployment types that
warrant additional configuration, or in the case of installing Snakeface as a cluster admin,
you likely will want to install from the source repository (or a release) and 
edit the settings.yml file in the snakemake folder before deploying your service.
More information will be added as this is developed. If you are interested, you can
look at :ref:`getting_started-settings`.
