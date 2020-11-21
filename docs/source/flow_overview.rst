.. _flow_overview:

===================
Data Flow: Overview
===================

This section describes some terminology and gives an overview of the work and data flow for raw data in CODA.

-----------------------------
Life Cycle of an Illumina Run
-----------------------------

1. CODA provides a Ceph-based data sink network share for each sequencer to mount as readable and writeable.
   Data is written there using the flow cell naming convention of ``<YYMMDD>_<INSTRUMENT_<RUN_NO>_<FLOWCELLID>``.
2. CODA watches this Ceph folder and continuously ingests the data into the iRODS system into the per-site raw data area.
3. The completion of the sequencing is detected and the data on Ceph is moved from the data sink into the ingested area on the Ceph system.
   This area is not visible to the instrument and read-only by the operators via network shares.

...

--------
Glossary
--------

**Site.**
Each data generating lab corresponds to a site.
Each site has a number of instruments that generate data.

**Landing Zones.**
Data is generated on scientific instruments which are often Windows PCs that write to network shares.
Each instrument gets its own network share / data volume / folder.
The CODA installation provides central volumes that the machines can mount and write to.
In the iRODS language these volumes are called landing zones.
Each writeable storage folder in the landing zone has a shadow folder that is only available as read only and into which the data from the landing zone is moved once completed.

**Data Ingest.**
While the machines generate data and write it into their landing zone, the data ingest process watches and transfers the data into the iRODS data storage system.
Once the ingestion process determines that the data generation is complete and data has been imported correctly, the file or folder with the raw data is moved into the shadow volume.
Here it is not visible by the instrument any more but still visible from the operator's workstation.
The data ingestion process will also extract basic meta data from the raw data in the landing zone and annotate the data in iRODS with it.

**Raw Data Storage.**
Data is stored and organized in the iRODS server.

**Meta Data Management.**
Meta data is stored in the iRODS server and managed through the iCommands command line tools and the Metalnx web front-end.
