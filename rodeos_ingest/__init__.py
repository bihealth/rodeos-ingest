from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

from ._check_path import _check_executables_in_path

# _check_executables_in_path(["hashdeep", "sort", "find", "ichksum", "iquest"])
# del _check_executables_in_path
