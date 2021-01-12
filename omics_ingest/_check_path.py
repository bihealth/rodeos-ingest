"""Checking for presence of required external programs."""

import subprocess  # nosec
import typing


def _executable_in_path(name: str) -> typing.Union[str, bool]:
    """Check whether an executable with the given ``name`` is in the ``$PATH``.

    Uses ``which``.

    Return path to executable or ``True`` if output is empty.  Returns ``False``
    if ``which`` could not find it.
    """
    res = subprocess.run(  # nosec
        ["which", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1, encoding="utf-8"
    )  # noqa
    if res.returncode == 0:
        return res.stdout or True
    else:
        return False


def _check_executables_in_path(names: typing.List[str]) -> None:
    """Checks whether/that executables in ``names`` are in the path."""
    problematic = [name for name in names if not _executable_in_path(name)]
    if problematic:
        tpl = "The following executable(s) are required but not in PATH: %s"
        raise RuntimeError(tpl % ", ".join(problematic))
