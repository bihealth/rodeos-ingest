.. _wf_common:

===============
Common Workflow
===============

Generally, ingest works by scanning a **source** directory (``${SOURCE}``) and transferring it into an iRODS **destination** (``${DEST}``) collection.
Each entry of the source directory corresponds to a data set (e.g., a directory or files).

Ingest can be run in a one-time or a repeated/periodic fashion.
Each time that the ingest work is done is called a **job**.

.. _wf_common_multi:

--------------------------
Common Multi-File Workflow
--------------------------

The following workflow has been implemented in a generic fashion and is reused in the case of multi-file data sets.
Such data sets consist of one directory that contains (meta) data files and also marker files that indicate the status of the data by their presence or content.

before each
    job for each directory ``${ENTRY}`` in ``${SOURCE}``:
        - a corresponding collection ``${DEST}/${ENTRY}`` is created in iRODS if it does not exist
        - the meta data ``rodeos::ingest::first_seen`` is set to the current date and time

for each file in the source directory
    - the file is created/updated by the ``irods_capability_automated_ingest`` functionality
    - the collection ``${DEST}/${ENTRY}`` gets its meta data ``rodeos::ingest::last_update`` set to the current date and time
    - the checksum of the file is registered in iRODS using ``ichksum``

after each job
    for each directory ``${ENTRY}`` in ``${SOURCE}``:
        - if ``${DEST}/${ENTRY}`` is checked whether it exists in iRODS and is considered as done and skipped if not so; the detection of whether ``${ENTRY}`` is done is functionality implemented in the specialization of the common workflow
        - if ``${DEST}/${ENTRY}`` has its last update after a certain period of time and is considered at rest; if not then it it is skipped
        - a call to ``ichksum -r`` ensures that all files in ``${DEST}/${ENTRY}`` have checksums
        - a manifest file (listing all files below ``${SOURCE}/${ENTRY}`` with their size in bytes and checksum; excluding the manifest file of course) is created for the local directory using the ``hashdeep`` tool
        - a corresponding manifest file is created using the files in the iRODS catalogue and the checksum known to iRODS
        - the local and iRODS manifest files are compared (semantically, their content will not be byte identically) and the process is stopped if they are not equal
        - both files are uploaded into iRODS (and get their checksum computed)
        - the folder ``${SOURCE}/${ENTRY}`` is moved to ``${SOURCE}-INGESTED/${ENTRY}``
            - this explicitely and verbosely marks the process as done to the user
            - the data generation instrument can be given access only to ``${SOURCE}`` such that it only has access to the data during generation but not afterwards; thus access to the instrument only grants access to the currently created data set but not the backcatalogue
