"""Configuration settings."""

import os

# Values to consider for true.
_TRUTHY = ("1", "true", "yes")

#: Set how many seconds should pass before data is detected to be at rest.
RODEOS_DELAY_UNTIL_AT_REST_SECONDS = int(
    os.environ.get("RODEOS_DELAY_UNTIL_AT_REST_SECONDS", str(5 * 60))
)

#: Number of threads to use in ``hashdeep```.
RODEOS_HASHDEEP_THREADS = int(os.environ.get("RODEOS_HASHDEEP_THREADS", "8"))
#: Algorithm to use for hashing in ``hashdeep```.
RODEOS_HASHDEEP_ALGO = os.environ.get("RODEOS_HASHDEEP_ALGO", "md5")

#: Whether or not to look for external dependency.
RODEOS_LOOK_FOR_EXECUTABLES = (
    os.environ.get("RODEOS_LOOK_FOR_EXECUTABLES", "true").lower() in _TRUTHY
)

#: Whether or not to move directories in ingest after completing item.
RODEOS_MOVE_AFTER_INGEST = os.environ.get("RODEOS_MOVE_AFTER_INGEST", "true").lower() in _TRUTHY

#: File name for local manifest file.
RODEOS_MANIFEST_LOCAL = os.environ.get("RODEOS_MANIFEST_LOCAL", "_MANIFEST_LOCAL.txt")
#: File name for iRODS manifest file.
RODEOS_MANIFEST_IRODS = os.environ.get("RODEOS_MANIFEST_IRODS", "_MANIFEST_IRODS.txt")
