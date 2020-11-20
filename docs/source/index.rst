CUBI Omics Data Access
======================

The aim of the CUBI Omics Data Access (CODA) system is to facilitate the management and access to Omics raw mass data (e.g., genomics or proteomics data).
The system itself is based on the `iRODS <https://irods.org>`_ ecosystem:

- iRODS for mass data storage and meta data management,
- Metalnx as a graphical user interface to iRODS, and
- Davrods for WebDAV based access to the data.

.. toctree::
   :maxdepth: 2
   :caption: Data Flow

   flow_overview
   flow_landing_zones
   flow_ingest

.. toctree::
   :maxdepth: 2
   :caption: Details

   fs_structure
