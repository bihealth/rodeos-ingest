"""Configuration settings.

The value of the configuration environment variables have to be parseable to the types given for the variables below.
In the case of ``bool`` variables, any string whose lower case value equals ``1``, ``true``, or ``yes`` will be
converted into ``True``, any other value will be convered into ``False``.

The values shown below are the defaults if the environment variable remains unset.
"""

# !!!!!
# IMPORTANT: use the same names here as for the corresponding environment variables.
# IMPORTANT: the documentation text assumes this.
# !!!!!

import os

#: Values to consider for true.
_TRUTHY = ("1", "true", "yes")

#: Set how many seconds should pass before data is detected to be at rest.
RODEOS_DELAY_UNTIL_AT_REST_SECONDS: int = int(
    os.environ.get("RODEOS_DELAY_UNTIL_AT_REST_SECONDS", str(5 * 60))
)

#: Number of threads to use in ``hashdeep```.
RODEOS_HASHDEEP_THREADS: int = int(os.environ.get("RODEOS_HASHDEEP_THREADS", "8"))
#: Algorithm to use for hashing in ``hashdeep```.
RODEOS_HASHDEEP_ALGO: str = os.environ.get("RODEOS_HASHDEEP_ALGO", "md5")

#: Whether or not to look for external dependency.
RODEOS_LOOK_FOR_EXECUTABLES: bool = (
    os.environ.get("RODEOS_LOOK_FOR_EXECUTABLES", "true").lower() in _TRUTHY
)

#: Whether or not to move directories in ingest after completing item.
RODEOS_MOVE_AFTER_INGEST: bool = os.environ.get(
    "RODEOS_MOVE_AFTER_INGEST", "true"
).lower() in _TRUTHY

#: File name for local manifest file.
RODEOS_MANIFEST_LOCAL: str = os.environ.get("RODEOS_MANIFEST_LOCAL", "_MANIFEST_LOCAL.txt")
#: File name for iRODS manifest file.
RODEOS_MANIFEST_IRODS: str = os.environ.get("RODEOS_MANIFEST_IRODS", "_MANIFEST_IRODS.txt")

#: Name of the "done" marker file for Illumina demultiplexing ingest.
RODEOS_ILLUMINA_FASTQ_DONE_MARKER_FILE: str = os.environ.get(
    "RODEOS_ILLUMINA_FASTQ_DONE_MARKER_FILE", "DIGESTIFLOW_DEMUX_DONE.txt"
)
