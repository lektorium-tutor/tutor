.. _local:

Local deployment
================

This method is for deploying Open edX locally on a single server, where docker images are orchestrated with `docker-compose <https://docs.docker.com/compose/overview/>`_.

.. note::
    Lekt is compatible with the ``docker compose`` subcommand. However, this support is still in beta and we're not sure it will behave the same as the previous ``docker-compose`` command. So ``docker-compose`` will be preferred, unless you set an environment variable ``LEKT_USE_COMPOSE_SUBCOMMAND`` to enforce using ``docker compose``.

.. _tutor_root:

In the following, environment and data files will be generated in a user-specific project folder which will be referred to as the "**project root**". On Linux, the default project root is ``~/.local/share/lekt``. An alternative project root can be defined by passing the ``--root=...`` option to the ``tutor`` command, or defining the ``LEKT_ROOT=...`` environment variable::

    lekt --root=/path/to/tutorroot run ...
    # Or equivalently:
    export LEKT_ROOT=/path/to/tutorroot
    lekt run ...

.. note::
    As of v10.0.0, a locally-running Open edX platform can no longer be accessed from http://localhost or http://studio.localhost. Instead, when running ``lekt local quickstart``, you must now decide whether you are running a platform that will be used in production. If not, the platform will be automatically be bound to http://local.lektorium.tv and http://studio.local.lektorium.tv, which are domain names that point to 127.0.0.1 (localhost). This change was made to facilitate internal communication between Docker containers.

Main commands
-------------

All available commands can be listed by running::

    lekt local --help

All-in-one command
~~~~~~~~~~~~~~~~~~

A fully-functional platform can be configured and run in one command::

    lekt local quickstart

But you may want to run commands one at a time: it's faster when you need to run only part of the local deployment process, and it helps you understand how your platform works. In the following, we decompose the ``quickstart`` command.

Configuration
~~~~~~~~~~~~~

::

    lekt config save --interactive

This is the only non-automatic step in the installation process. You will be asked various questions about your Open edX platform and appropriate configuration files will be generated. If you would like to automate this step then you should run ``lekt config save --interactive`` once. After that, there will be a ``config.yml`` file at the root of the project folder: this file contains all the configuration values for your platform, such as randomly generated passwords, domain names, etc.

If you want to run a fully automated installation, upload the ``config.yml`` file to wherever you want to run Open edX. You can then entirely skip the configuration step.

Update docker images
~~~~~~~~~~~~~~~~~~~~

::

    lekt local dc pull

This downloads the latest version of the Docker images from `Docker Hub <https://hub.docker.com/r/lektorium-tutor/openedx/>`_. Depending on your bandwidth, this might take a long time. Minor image updates will be incremental, and thus much faster.

Running Open edX
~~~~~~~~~~~~~~~~

::

    lekt local start

This will launch the various docker containers required for your Open edX platform. The LMS and the Studio will then be reachable at the domain name you specified during the configuration step.

To stop the running containers, just hit Ctrl+C.

In production, you will probably want to daemonize the services. To do so, run::

    lekt local start --detach

And then, to stop all services::

    lekt local stop

Service initialisation
~~~~~~~~~~~~~~~~~~~~~~

::

    lekt local init

This command should be run just once. It will initialise all applications in a running platform. In particular, this will create the required databases tables and apply database migrations for all applications.

If initialisation is stopped with a ``Killed`` message, this certainly means the docker containers don't have enough RAM. See the :ref:`troubleshooting` section.

Logging
~~~~~~~

By default, logs from all containers are forwarded to the `default Docker logging driver <https://docs.docker.com/config/containers/logging/configure/>`_: this means that logs are printed to the standard output when running in non-daemon mode (``lekt local start``). In daemon mode, logs can still be accessed with ``lekt local logs`` commands (see :ref:`logging <logging>`).

In addition, all LMS and CMS logs are persisted to disk by default in the following files::

    $(lekt config printroot)/data/lms/logs/all.log
    $(lekt config printroot)/data/cms/logs/all.log

Finally, tracking logs that store `user events <https://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/index.html>`_ are persisted in the following files::

    $(lekt config printroot)/data/lms/logs/tracking.log
    $(lekt config printroot)/data/cms/logs/tracking.log

Status
~~~~~~

You can view your platform's containers::

    lekt local status

Notice the **State** column in the output. It will tell you whether each container is starting, restarting, running (``Up``), cleanly stopped (``Exit 0``), or stopped on error (``Exit N``, where N ≠ 0).

Common tasks
------------

.. _createuser:

Creating a new user with staff and admin rights
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will most certainly need to create a user to administer the platform. Just run::

    lekt local createuser --staff --superuser yourusername user@email.com

You will be asked to set the user password interactively.

.. _democourse:

Importing the demo course
~~~~~~~~~~~~~~~~~~~~~~~~~

After a fresh installation, your platform will not have a single course. To import the `Open edX demo course <https://github.com/openedx/edx-demo-course>`_, run::

    lekt local importdemocourse

.. _settheme:

Setting a new theme
~~~~~~~~~~~~~~~~~~~

The default Open edX theme is rather bland, so Lekt makes it easy to switch to a different theme::

    lekt local settheme mytheme

Out of the box, only the default "open-edx" theme is available. We also developed `Indigo, a beautiful, customizable theme <https://github.com/lektorium-tutor/indigo>`__ which is easy to install with Lekt.

Running arbitrary ``manage.py`` commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any ``./manage.py`` command provided by Open edX can be run in a local platform deployed with Lekt. For instance, to delete a course, run::

    lekt local run cms ./manage.py cms delete_course <your_course_id>

To update the course search index, run::

    # Run this command periodically to ensure that course search results are always up-to-date.
    lekt local run cms ./manage.py cms reindex_course --all --setup

Reloading Open edX settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

After modifying Open edX settings, for instance when running ``lekt config save``, you will want to restart the web processes of the LMS and the CMS to take into account those new settings. It is possible to simply restart the whole platform (with ``lekt local reboot``) or just a single service (``lekt local restart lms``) but that is overkill. A quicker alternative is to send the HUP signal to the uwsgi processes running inside the containers. The "openedx" Docker image comes with a convenient script that does just that. To run it, execute::

    lekt local exec lms reload-uwsgi


Customizing the deployed services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You might want to customise the docker-compose services listed in ``$(lekt config printroot)/env/local/docker-compose.yml``. To do so, you should create a ``docker-compose.override.yml`` file in that same folder::

    vim $(lekt config printroot)/env/local/docker-compose.override.yml

The values in this file will override the values from ``docker-compose.yml`` and ``docker-compose.prod.yml``, as explained in the `docker-compose documentation <https://docs.docker.com/compose/extends/#adding-and-overriding-configuration>`__.

Similarly, the job service configuration can be overridden by creating a ``docker-compose.jobs.override.yml`` file in that same folder.
