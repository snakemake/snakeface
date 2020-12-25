.. _getting_started-notebook:

========
Notebook
========

Make sure that before you run a notebook, you are comfortable with Snakemake
and have a workflow with a Snakefile read to run. If not, you can start
with the instructions for an example workflow (:ref:`getting_started-example-workflow`).


Local Notebook
==============

If you have installed Snakeface on your own, you likely want a notebook. You can
run snakeface without any arguments to run one by default: This works because
the default install settings have set ``NOTEBOOK_ONLY`` and it will start a Snakeface
session.

.. code:: console

    $ snakeface

However, if your center is running Snakeface as a service, you will need to ask for
a notebook explicitly:

.. code:: console

    $ snakeface notebook

For either of the two you can optionally specify a port:

.. code:: console

    $ snakeface notebook --port 5555
    $ snakeface --port 5555


For the notebook install, you will be given a token in your console, and you can copy
paste it into the interface to log in. 

image:: ../images/notebook-login.png

You can then browse to localhost at the port specified to see the interface!
The first prompt will ask you to create a collection, which is a grouping of workflows.
You might find it useful to organize your projects.

image:: ../images/after-notebook-login.png

Next, choose a name for your collection. If you are doing a notebook, the private and
public fields aren't relevant - everything is private to you.

image:: ../images/new-collection.png


You'll be taken to your new collection, which doesn't have any workflows.

image:: ../images/new-collection.png

You can click on the button to create a workflow to create one. The next
form will provide input fields for all arguments provided by your Snakemake
installation. You can select the blue buttons at the top (they are always at the
top) to jump to a section, and see the command being previewed at the bottom.
The command will always update when you make a new selection.

image:: ../images/new-workflow.png

Note that if you start running your notebook in a location without any Snakefiles,
you will get a message that tells you to create one first. A Snakefile matching
some pattern of snakefile* (case ignored) must be present. When you've finished your
workflow, click on "Run Workflow." If the workflow is invalid (e.g., you've moved the
Snakefile, or provided conflicting commands) then you'll be returned to this
view with an error message. If it's valid, you'll be redirected to a page to monitor
the workflow.

**under development**

Finally, you'll also be able to see your new collection in the Workflow Collections table
on the dashboard.

image:: ../images/dashboard.png
