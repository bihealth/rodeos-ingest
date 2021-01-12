"""Code with ingest capability logic for Illumina sequencer output (BCL files).

- Use ``Operation.PUT_APPEND`` to update changed files in addition to uploading new ones.
- When an output folder is first seen write current timestamp to ``omics::ingest::first_seen``
- Every time a is changed then write current timestamp to ``omics::ingest::last_update``
- If the marker file for being done has been written out and ``omics::ingest::last_update``
  is longer than ``DELAY_UNTIL_AT_REST`` (e.g., 15 minutes) in the past then move away the
  run folder into the ingested part of the landing zone.
"""

import datetime
import pathlib
import typing

from irods_capability_automated_ingest.core import Core
from irods_capability_automated_ingest.utils import Operation

from ...common import (
    pre_job as common_pre_job,
    post_job as common_post_job,
    refresh_last_update_metadata,
    run_ichksum,
)
from ..settings import RODEOS_DELAY_UNTIL_AT_REST_SECONDS

#: This time should pass after the previous update and the existance of the output marker file
#: for a run folder to be considered at rest and moved away.
DELAY_UNTIL_AT_REST = datetime.timedelta(seconds=RODEOS_DELAY_UNTIL_AT_REST_SECONDS)


def is_demuxfolder_done(path: typing.Union[str, pathlib.Path]) -> bool:
    path = pathlib.Path(path)
    return (path / "DIGESTIFLOW_DEMUX_DONE.txt").exists()


class event_handler(Core):
    @staticmethod
    def pre_job(hdlr_mod, logger, meta):
        """Set the ``first_seen`` meta data value."""
        common_pre_job(hdlr_mod, logger, meta)
        common_post_job(hdlr_mod, logger, meta, is_demuxfolder_done, DELAY_UNTIL_AT_REST)

    @staticmethod
    def post_job(hdlr_mod, logger, meta):
        """Move completed and at rest run folders into the "ingested" area."""
        _, _, _ = hdlr_mod, logger, meta

    @staticmethod
    def operation(session, meta, **options):
        """Return ``Operation.PUT_APPEND`` to only upload new data."""
        _, _, _ = session, meta, options
        return Operation.PUT_APPEND

    @staticmethod
    def post_data_obj_create(hdlr_mod, logger, session, meta, **options):
        _, _ = hdlr_mod, options
        refresh_last_update_metadata(logger, session, meta)
        run_ichksum(meta["target"])

    @staticmethod
    def post_data_obj_update(hdlr_mod, logger, session, meta, **options):
        _, _ = hdlr_mod, options
        refresh_last_update_metadata(logger, session, meta)
        run_ichksum(meta["target"])

    @staticmethod
    def delay(hdlr_mod, logger, meta):
        _, _, _ = hdlr_mod, logger, meta
        return 5

    @staticmethod
    def max_retries(hdlr_mod, logger, meta):
        _, _, _ = hdlr_mod, logger, meta
        return 10
