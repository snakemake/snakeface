.. _manual-main:

=========
Snakeface
=========

.. image:: https://github.com/snakemake/snakeface/workflows/CI/badge.svg?branch=main&label=CI
    :target: https://github.com/snakemake/snakeface/actions?query=branch%3Amain+workflow%3ACI

.. image:: https://img.shields.io/discord/753690260830945390?label=discord%20chat   
    :alt: Discord
    :target: https://discord.gg/NUdMtmr

.. image:: https://img.shields.io/github/stars/snakemake/snakeface?style=social
    :alt: GitHub stars
    :target: https://github.com/snakemake/snakeface/stargazers


Snakeface is the Snakemake Interface, where you can easily run workflows.
To learn more about Snakemake, visit the `official documentation <https://snakemake.readthedocs.io/>`_

.. _main-getting-started:

---------------
Getting started
---------------

Snakeface can be used on your local machine to provide a nice interface to running
snakemake workflows, or deployed by a group to run shared workflows. See
 :ref:`use-cases` for an overview of different use cases.

.. _main-support:

-------
Support
-------

* In case of **questions**, please post on `stack overflow <https://stackoverflow.com/questions/tagged/snakemake>`_.
* To **discuss** with other Snakemake users, you can use the `mailing list <https://groups.google.com/forum/#!forum/snakemake>`_. **Please do not post questions there. Use stack overflow for questions.**
* For **bugs and feature requests**, please use the `issue tracker <https://github.com/snakemake/snakeface/issues>`_.
* For **contributions**, visit Snakemake on `Github <https://github.com/snakemake/snakeface>`_.

---------
Resources
---------

`Snakemake Repository <https://snakemake.readthedocs.org>`_
    The Snakemake workflow manager repository houses the core software for Snakemake.

`Snakemake Wrappers Repository <https://snakemake-wrappers.readthedocs.org>`_
    The Snakemake Wrapper Repository is a collection of reusable wrappers that allow to quickly use popular tools from Snakemake rules and workflows.

`Snakemake Workflows Project <https://github.com/snakemake-workflows/docs>`_
    This project provides a collection of high quality modularized and re-usable workflows.
    The provided code should also serve as a best-practices of how to build production ready workflows with Snakemake.
    Everybody is invited to contribute.

`Snakemake Profiles Project <https://github.com/snakemake-profiles/doc>`_
    This project provides Snakemake configuration profiles for various execution environments.
    Please consider contributing your own if it is still missing.

`Bioconda <https://bioconda.github.io/>`_
    Bioconda can be used from Snakemake for creating completely reproducible workflows by defining the used software versions and providing binaries.

.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 1

   getting_started/installation

.. toctree::
  :caption: Deploy templates
  :name: deployTemplates
  :hidden:
  :maxdepth: 1

  deploy/deploy
  deploy/template

.. toctree::
    :caption: API Reference
    :name: api-reference
    :hidden:
    :maxdepth: 1

    api_reference/snakeface
    api_reference/internal/modules
