"""Code with ingest capability logic for Illumina sequencer output.

- Use ``Operation.PUT_SYNC`` to update changed files in addition to uploading new ones.
"""

import pathlib
import typing

from irods_capability_automated_ingest.core import Core
from irods_capability_automated_ingest.utils import Operation

from ._illumina import parse_runinfo_xml, parse_runparameters_xml, RunInfo
from ._helpers import cleanuping


def apply_runinfo_metadata(session, run_info: RunInfo, target: str) -> None:
    """Apply ``RunInfo`` meta data to collection AVUs."""
    target_coll = str(pathlib.Path(target).parent)
    with cleanuping(session):
        coll = session.collections.get(target_coll)
        for avu in run_info.to_avus():
            coll.metadata.add(*avu)


def apply_runparameters_metadata(session, values: typing.Dict[str, str], target: str) -> None:
    """Apply ``runParameters.xml`` meta data to collection AVUs."""
    target_coll = str(pathlib.Path(target).parent)
    with cleanuping(session):
        coll = session.collections.get(target_coll)
        for key, value in values.items():
            coll.metadata.add(key, value, "")


def _post_runinfoxml_create_or_update(logger, session, meta):
    path = meta["path"]
    if path.lower().endswith("/runinfo.xml"):
        logger.info("applying RunInfo.xml meta data from %s" % path)
        apply_runinfo_metadata(session, parse_runinfo_xml(path), meta["target"])
    elif path.lower().endswith("/runparameters.xml"):
        values = parse_runparameters_xml(path)
        logger.info("applying runParameters.xml meta data from %s (%d)" % (path, len(values)))
        apply_runparameters_metadata(session, values, meta["target"])


class event_handler(Core):
    # @staticmethod
    # def to_resource(session, target, path, **options):
    #     return "regiResc2a"

    @staticmethod
    def operation(session, meta, **options):
        """Return ``Operation.PUT_SYNC`` to also put changed files."""
        return Operation.PUT_SYNC

    @staticmethod
    def post_data_obj_create(hdlr_mod, logger, session, meta, **options):
        return _post_runinfoxml_create_or_update(logger, session, meta)

    @staticmethod
    def post_data_obj_update(hdlr_mod, logger, session, meta, **options):
        return _post_runinfoxml_create_or_update(logger, session, meta)
