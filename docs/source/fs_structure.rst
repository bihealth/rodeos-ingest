.. _fs_structure:

=====================
File System Structure
=====================

::

    /.../omics/
    ├── irods-vault
    │   │   ...
    │   ├── site-1
    │   │   └── raw-data
    │   │       └── 2020
    │   │           └── M00001
    │   │               └── 200602_M00001_0001_000000000
    │   │                   ├── Config
    │   │                   │   ├── Effective.cfg
    │   │                   │   ├── MiSeqOverride.cfg
    │   │                   │   └── RTAStart.bat
    │   │                   |   ...
    │   │                   ├── RunInfo.xml
    │   │                   ├── runParameters.xml
    │   │                   └── SampleSheet.csv
    │   └── ...
    └── lz
        ├── site-1
        │   ├── M00001
        │   ├── M00001-INGESTED
        ...
