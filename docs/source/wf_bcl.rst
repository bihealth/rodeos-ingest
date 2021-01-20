.. _wf_bcl:

============
BCL Workflow
============

This workflow implements ingest for directories as created by Illumina sequencing machines with BCL (base call) files.
The overall pattern follows the one described in the section :ref:`wf_common_multi`.
The specialization are:

for each file in the source directory
    - in addition to the steps described in the common workflow,
    - if the file is the run info or run parameters XML file then meta data is appropriately extracted from the XML file and applied to ``${DEST}/${ENTRY}``
    - if the file is a netcopy complete file then the timestamp is extracted and applied to ``${DEST}/${ENTRY}``

done detection
    - is implemented by the presence of the appropriate marker files depending on the Illumina device type and version
    - the device type and version is detected by logic analyzing the run info and run parameters XML files
