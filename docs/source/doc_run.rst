.. _doc_run:

=======
Running
=======

You run the ingest from the directory ``$SOURCE`` to the destination collection ``$DEST`` as follows.
Use the papropriate path to the handler module that you want to use.

::

    /opt/rodeos-ingest-env/bin/python \
        -m irods_capability_automated_ingest.irods_sync \
        start \
            --event_handler rodeos_ingest.genomics.illumina.bcl \
            --job_name rodeos-ingest-$(date +%Y-%m-%d_%H-%M-%S) \
             \
            --exclude_file_name ".*_MANIFEST_*.txt"  \
            -- \
            $SOURCE \
            $DEST

Please refer to the ICAI documentation (or the output when including ``--help``) for more information.

The following handler modules are provided.

=========================================  ============================
module                                     data type
=========================================  ============================
``rodeos_ingest.genomics.illumina.bcl``    Illumina run folders
``rodeos_ingest.genomics.illumina.fastq``  FASTQ demultiplexing results
=========================================  ============================
