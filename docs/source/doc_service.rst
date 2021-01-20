.. _doc_service:

==============
Worker Service
==============

The next step is setting up the worker (which is based on the Celery work queue).
You might want to create an appropriate service user for this on your ingest server (the user must be able to use the irods icommands without having to authenticate again).
Below is an example systemd file (that could be placed into ``/etc/systemd/system/rodeos-ingest.service``).
Please refer to the systemd configuration on details for running this.

::

    [Unit]
    Description=RODEOS Ingest Celery Queue
    AssertPathExists=/home/rodeos-ingest/.irods/irods_environment.json
    AssertPathExists=/home/rodeos-ingest/.irods/.irodsA

    [Service]
    Type=forking
    User=rodeos-ingest
    Environment=CELERY_APP=irods_capability_automated_ingest.sync_task
    Environment=CELERY_BIN=/opt/rodeos-ingest-env/bin/celery
    Environment=CELERY_BROKER_URL=redis://127.0.0.1:6379/0
    Environment=CELERYD_NODES=worker1
    Environment=CELERYD_LOG_FILE="/var/log/rodeos-ingest/rodeos-ingest-%n%I.log"
    Environment=CELERYD_PID_FILE="/var/run/rodeos-ingest/%n.pid"
    Environment=CELERYD_LOG_LEVEL=INFO
    Environment=CELERYD_OPTS=--concurrency=8
    RuntimeDirectory=rodeos-ingest
    WorkingDirectory=/home/rodeos-ingest
    ExecStart=/bin/sh -c '${CELERY_BIN} multi start ${CELERYD_NODES} \
      -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
      --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} \
      ${CELERYD_OPTS}'
    ExecStop=/bin/sh -c '${CELERY_BIN} multi stopwait ${CELERYD_NODES} \
      --pidfile=${CELERYD_PID_FILE}'
    ExecReload=/bin/sh -c '${CELERY_BIN} multi restart ${CELERYD_NODES} \
      -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
      --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} \
       ${CELERYD_OPTS}'

    [Install]
    WantedBy=multi-user.target

You could also run this manually using the following command.
Make sure that you activate the appropriate virtualenv before.

::

    /opt/rodeos-ingest-env/bin/celery \
        multi start \
        worker1 \
        -A irods_capability_automated_ingest.sync_task \
        --logfile=path/to/logs-%n%I.log \
        --pidfile=path/to/pid-%n.pid \
        --loglevel=INFO \
        --concurrency=8

-------------
Configuration
-------------

Configuration is done using environment variables.
As the Celery workers are actually performing the ingest work you have to update the environment variables when starting the ``celery`` executable.

You can find a documentation of the environment variables in :ref:`api_settings`.
