.. _wf_fastq:

==============
FASTQ Workflow
==============

This workflow is used for ingesting the result of the base call to sequence conversion step (sometimes also referred to as "demultiplexing" of raw Illumina base call data).
The overall pattern follows the one described in the section :ref:`wf_common_multi`.
The specialization are:

done file detection
    - is performed by the presence of a marker file configured by ``RODEOS_ILLUMINA_FASTQ_DONE_MARKER_FILE``
