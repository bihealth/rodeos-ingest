.. _doc_install:

============
Installation
============

Please also refer to the the documentation of `irods_capability_automated_ingest <https://github.com/irods/irods_capability_automated_ingest>`__ (ICAI).

------------
Dependencies
------------

Python 3
========

Python version 3.6 is required.
There currently (January 2020) is a limitation in ICAI that prevents it from being run on Python 3.7 and above.
Once this limitation has been removed, RODEOS Ingest will be able to run on Python 3.6 and above.

iRODS and iRODS iCommands
=========================

- You will need a working iRODS (catalogue/provider and resource) server(s).
- You must install iRODS iCommands on the machine that you want to run RODEOS Ingest on.
- The account that the RODEOS Ingest runs as must be properly setup and authenticated with the iRODS server.
  In other words, ``ils`` should work.
  Note well that PAM accounts will generally be affected by PAM login timeouts so you might want to use native authentication for such service users.

Redis
=====

Redis is a key value store/database.
ICAI is based on Celery and both Celery and ICAI directly use Redis for queue management and data caching.
The default settings of redis in many systems is to have no limit on its memory which can lead to out of memory situations when ingesting many files.
Make sure to adjust the following settings in ``redis.conf``, below are sensible defaults.

::

    maxmemory 1073741824            # 1GB, can be adjusted
    maxmemory-policy allkeys-lru    # enable cache evication based on LRU

-----
Steps
-----

We recommend installing the software in a Python `virtualenv <https://virtualenv.pypa.io/en/latest/>`__.

Perform a checkout

::

    # git clone git@github.com:bihealth/rodeos-ingest.git

Next install using ``pip``.

::

    # cd rodeos-ingest
    # pip install -e .
