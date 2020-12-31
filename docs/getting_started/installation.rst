.. _getting_started-installation:

============
Installation
============

Snakeface can be installed and run from a virtual environment, or from a container.


Virtual Environment
===================

First, clone the repository code.

.. code:: console

    $ git clone git@github.com:snakemake/snakeface.git
    $ cd snakeface


Then you'll want to create a new virtual environment, and install dependencies.

.. code:: console

    $ python -m venv env
    $ source env/bin/activate
    $ pip install -r requirements.txt


And install Snakeface (from the repository directly)

.. code:: console
 
    $ pip install -e .


Install via pip
===============

Snakeface can also be installed with pip.

.. code:: console

    $ pip install snakeface


Once it's installed, you should be able to inspect the client!


.. code:: console

    $ snakeface --help
    usage: snakeface [-h] [--version] [--noreload] [--verbosity {0,1,2,3}]
                     [--workdir [WORKDIR]] [--auth {token}] [--port PORT]
                     [--verbose] [--log-disable-color] [--log-use-threads]
                     [--force]
                     [repo] [dest] {notebook} ...

    Snakeface: interface to snakemake.

    positional arguments:
      repo                  Repository address and destination to deploy, e.g.,
                            <source> <dest>
      dest                  Path to clone the repository, should not exist.

    optional arguments:
      -h, --help            show this help message and exit
      --version             print the version and exit.
      --noreload            Tells Django to NOT use the auto-reloader.
      --verbosity {0,1,2,3}
                            Verbosity (0, 1, 2, 3).
      --workdir [WORKDIR]   Specify the working directory.
      --force               If the folder exists, force overwrite, meaning remove
                            and replace.

    SETTINGS:
      --auth {token}        Authentication type to create for the interface,
                            defaults to token.

    NETWORKING:
      --port PORT           Port to serve application on.

    LOGGING:
      --verbose             verbose output for logging.
      --log-disable-color   Disable color for snakeface logging.
      --log-use-threads     Force threads rather than processes.

    actions:
      subparsers for Snakeface

      {notebook}            snakeface actions
        notebook            run a snakeface notebook


Setup
=====

As a user, you most likely want to use Snakeface as an on demand notebook, so no additional
setup is needed other than installing the package. As we add more deployment types that
warrant additional configuration, or in the case of installing Snakeface as a cluster admin,
you likely will want to install from the source repository (or a release) and 
edit the settings.yml file in the root of the repository before deploying your service.
More information will be added as this is developed. If you are interested, you can
look at :ref:`getting_started-settings`.
