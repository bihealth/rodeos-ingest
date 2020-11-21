.. _flow_overview:

===================
Data Flow: Overview
===================

This section describes some terminology and gives an overview of the work and data flow for raw data in CODA.

-----------------------------
Life Cycle of an Illumina Run
-----------------------------

The instruments generates data and writes to a network share on the Ceph system.

1. CODA provides a Ceph-based data sink network share for each sequencer to mount as readable and writeable.
   Data is written there using the flow cell naming convention of ``<YYMMDD>_<INSTRUMENT_<RUN_NO>_<FLOWCELLID>``.
2. CODA watches this Ceph folder and continuously ingests the data into the iRODS system into an iRODS collection in the per-site raw data area.
3. The completion of the sequencing is detected and the data on Ceph is moved from the data sink into the "ingested" area on the Ceph system.
   This area is not visible to the instrument and read-only by the operators via Ceph-based network shares.
4. Meta data is extracted from the raw data by the ingestion process and the corresponding raw data collection in iRODS is annotated via AVU.
5. Further, the iRODS meta data annotation contains a status flag that marks the sequencing process as being done.

After these steps:

- The instrument is done writing data.
- Data in the Ceph system is in a folder accessible read-only by the operator and inaccessible by the instrument.
- Data has been completely ingested into an iRODS collection (iRODS terminology for a folder) in an area that is accessible by the operators.
- The iRODS collection has been annotated with meta data extracted from the information written by the instrument.

NB: data in the "ingested area" has to be deleted by a yet to be defined process (e.g., data older than 6 months montly by the instrument operators).

Completion of data geneneration triggers the start of demultiplexing.
A watchdog program looks for newly completed collections with raw Illumina data.

6. Data is staged from the iRODS collection to the fast scratch storage of the HPC 4 Research cluster.
7. After staging, the conversion from base calls to sequences is triggered.
   The result includes standard QC.
8. The conversion results are written to a separate "conversion result landing zone" on the scratch volume of the HPC 4 Research cluster.
9. A (second) sequence ingestion watches for new conversion results and starts an ingestion process into the "sequence data" area of the iROD system.
   This area is accessible read/write by the operators.
   The ingestion process also annotates each resulting collection and data objects (iRODS term for files) with the corresponding meta data from the flow cell and the demultiplexing process itself.

After these steps:

- The demultiplexing process is done.
- All demultiplexing results have been ingested into the "sequence data" area of the iRODS system.
- Demultiplexing results have been annotated with meta data from the sequencing and demultiplexing.

NB: data is removed from the scratch volume of HPC 4 Research cluster automatically after 6 weeks.

Now that the sequence creation is complete, data can be delivered.
There exists a "project area" in the iRODS system with read/write permissions for the instrument operators.
There is a folder for each of the projects with one sub folder for each of the sequencing runs related to the project.
Delivery can happen in one of the following ways:

- Instrument operators move data into the appropriate folder of the project area.
  They also give read permissions to the project areas to one or more members of the recipient group.
- Instrument operators give read permissions to collections in the raw data folder.
  This can be done only on run folders and maybe on the lane level in case a customer buys a full lane.
  With NovaSeq and NextSeq, this is an unlikely scenario because of high degree of per lane multiplexing.
- Instrument operators give read access to either area using iRODS tickets.
  This allows access to users outside of the member organization user repositories.

Data access can happen in the following ways:

- Via the iRODS protocol, e.g., the iRODS iCommands.
- Via DavRods / mounting volumes.

To be discussed:

- How long should raw data, sequence data, and delivered data be kept?
  Instrument operators could annotate the collections with 

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
