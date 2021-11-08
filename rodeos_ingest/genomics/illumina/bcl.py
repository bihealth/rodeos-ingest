"""Code with ingest capability logic for Illumina sequencer output (BCL files).

- Use ``Operation.PUT_SYNC`` to update changed files in addition to uploading new ones.
- Handle initial upload and update of ``RunInfo.xml`` and ``runParameters.xml`` and update
  collection AVU.
- When a run folder is first seen write current timestamp to ``rodeos::ingest::first_seen``
- Every time a is changed then write current timestamp to ``rodeos::ingest::last_update``
- If the marker file for being done has been written out and ``rodeos::ingest::last_update``
  is longer than ``DELAY_UNTIL_AT_REST`` (e.g., 15 minutes) in the past then move away the
  run folder into the ingested part of the landing zone.
"""

import datetime
import pathlib
import typing

from irods.meta import iRODSMeta
from irods_capability_automated_ingest.core import Core
from irods_capability_automated_ingest.utils import Operation

from rodeos_ingest.genomics.illumina.run_folder import (
    parse_runinfo_xml,
    parse_runparameters_xml,
    parse_netcopy_complete_txt,
    runparameters_to_marker_file,
    RunInfo,
    NetcopyInfo,
)
from rodeos_ingest.common import (
    cleanuping,
    pre_job as common_pre_job,
    post_job as common_post_job,
    refresh_last_update_metadata,
    run_ichksum,
)
from rodeos_ingest.settings import RODEOS_DELAY_UNTIL_AT_REST_SECONDS


#: This time should pass after the previous update and the existance of the output marker file
#: for a run folder to be considered at rest and moved away.
DELAY_UNTIL_AT_REST = datetime.timedelta(seconds=RODEOS_DELAY_UNTIL_AT_REST_SECONDS)


def apply_runinfo_metadata(session, run_info: RunInfo, target: str) -> None:
    """Apply ``RunInfo`` meta data to collection AVUs."""
    target_coll = str(pathlib.Path(target).parent)
    with cleanuping(session):
        coll = session.collections.get(target_coll)
        for avu in run_info.to_avus():
            coll.metadata[avu[0]] = iRODSMeta(*avu)


def apply_runparameters_metadata(session, values: typing.Dict[str, str], target: str) -> None:
    """Apply ``runParameters.xml`` meta data to collection AVUs."""
    target_coll = str(pathlib.Path(target).parent)
    with cleanuping(session):
        coll = session.collections.get(target_coll)
        for key, value in values.items():
            coll.metadata[key] = iRODSMeta(key, value, "")


def apply_netcopy_complete_metadata(session, netcopy_info: NetcopyInfo, target: str) -> None:
    """Apply netcopy complete meta data to collection AVUs."""
    with cleanuping(session):
        coll = session.data_objects.get(target)
        for avu in netcopy_info.to_avus():
            coll.metadata[avu[0]] = iRODSMeta(*avu)


def _post_runinfoxml_create_or_update(logger, session, meta):
    """Actually parse the XML files and apply meta data."""
    path = meta["path"]
    if path.lower().endswith("/runinfo.xml"):
        logger.info("applying RunInfo.xml meta data from %s" % path)
        apply_runinfo_metadata(session, parse_runinfo_xml(path), meta["target"])
    elif path.lower().endswith("/runparameters.xml"):
        values = parse_runparameters_xml(path)
        logger.info("applying runParameters.xml meta data from %s (%d)" % (path, len(values)))
        apply_runparameters_metadata(session, values, meta["target"])
    elif "netcopy_complete" in path.lower():
        netcopy_info = parse_netcopy_complete_txt(path)
        if netcopy_info:
            logger.info("applying Netcopy_complete meta data from %s" % path)
            apply_netcopy_complete_metadata(session, netcopy_info, meta["target"])


def is_runfolder_done(path: typing.Union[str, pathlib.Path]) -> bool:
    path = pathlib.Path(path)
    for name in ("RunParameters.xml", "runParameters.xml"):
        if (path / name).exists():
            markers = runparameters_to_marker_file(
                parse_runparameters_xml(path / name), path / name
            )
            return all((path / marker).exists() for marker in markers)
    return False  # pragma: no cover


class event_handler(Core):
    @staticmethod
    def pre_job(hdlr_mod, logger, meta):
        """Set the ``first_seen`` meta data value."""
        common_pre_job(hdlr_mod, logger, meta)
        common_post_job(hdlr_mod, logger, meta, is_runfolder_done, DELAY_UNTIL_AT_REST)

    @staticmethod
    def post_job(hdlr_mod, logger, meta):
        """Move completed and at rest run folders into the "ingested" area."""
        _, _, _ = hdlr_mod, logger, meta
        common_post_job(hdlr_mod, logger, meta, is_runfolder_done, DELAY_UNTIL_AT_REST)

    @staticmethod
    def operation(session, meta, **options):
        """Return ``Operation.PUT_SYNC`` to also put changed files."""
        _, _, _ = session, meta, options
        return Operation.PUT_SYNC

    @staticmethod
    def post_data_obj_create(hdlr_mod, logger, session, meta, **options):
        """Update run folder meta data from ``RunInfo.xml`` and ``runParameters.xml`` files after
        initial upload and update."""
        _, _ = hdlr_mod, options
        _post_runinfoxml_create_or_update(logger, session, meta)
        refresh_last_update_metadata(logger, session, meta)
        run_ichksum(meta["target"])

    @staticmethod
    def post_data_obj_update(hdlr_mod, logger, session, meta, **options):
        """Update run folder meta data from ``RunInfo.xml`` and ``runParameters.xml`` files after
        initial upload and update."""
        _, _ = hdlr_mod, options
        _post_runinfoxml_create_or_update(logger, session, meta)
        refresh_last_update_metadata(logger, session, meta)
        run_ichksum(meta["target"])

    @staticmethod
    def delay(hdlr_mod, logger, meta, retries):
        _, _, _, _ = hdlr_mod, logger, meta, retries
        return 5

    @staticmethod
    def max_retries(hdlr_mod, logger, meta):
        _, _, _ = hdlr_mod, logger, meta
        return 10
