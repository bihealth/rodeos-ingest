RODEOS Ingest
=============

The aim of the RODEOS (Raw Omics Data accEss and Organisation System) system is to facilitate the management and access to Omics raw mass data (e.g., genomics or proteomics data).
The system itself is based on the `iRODS <https://irods.org>`__ ecosystem:

- iRODS for mass data storage and meta data management,
- Metalnx as a graphical user interface to iRODS, and
- Davrods for WebDAV based access to the data.

This is the documentation for the data ingest (aka **data import**) subsystem.
That is, for the import of data into iRODS employing the `irods_capability_automated_ingest <https://github.com/irods/irods_capability_automated_ingest>`__ (ICAI) library.

This documentation provides the following information:

- the implemented logic / workflow,
- the installation of the ingest services (that are based on `Celery <https://docs.celeryproject.org/en/stable/>`__ as ICAI is based on Celery),
- the configuration the module using environment variables, and
- how to properly call the importa via ICAI.

Where necessary, it provides hints on the configuration of external software such as Redis (an indirect dependency through Celery).
However, for an overview of the "super" system RODEOS itself and the individual external libraries, please see the corresponding documentation.

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: Manual

    doc_install
    doc_service
    doc_run

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: Workflows

    wf_common
    wf_bcl
    wf_fastq

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: Developer Information

    dev_overview

.. toctree::
    :hidden:
    :maxdepth: 1
    :caption: API Documentation

    api_settings
    api_common
    api_genomics
