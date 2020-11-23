"""Common code for the omics ingest."""

from contextlib import contextmanager
import datetime
import pathlib
import typing

import dateutil.parser
from irods_capability_automated_ingest.sync_irods import irods_session

#: AVU key to use for ``last_update`` attribute.
KEY_LAST_UPDATE = "omics::ingest::last_update"
#: AVU key to use destionation run folder ingestion status.
KEY_STATUS = "omics::ingest::status"
#: AVU key to use for ``first_seen`` attribute.
KEY_FIRST_SEEN = "omics::ingest::first_seen"


@contextmanager
def cleanuping(thing):
    try:
        yield thing
    finally:
        thing.cleanup()


def to_ingested_path(orig_path: typing.Union[str, pathlib.Path]) -> pathlib.Path:
    """Convert a run folder path to an "ingested" path."""
    orig_path = pathlib.Path(orig_path)
    ingested_base = orig_path.parent.parent / (orig_path.parent.name + "-INGESTED")
    return ingested_base / orig_path.name


def _post_job_run_folder_done(
    logger,
    session,
    src_folder,
    dst_collection,
    is_folder_done: typing.Callable[[typing.Union[pathlib.Path, str]], bool],
    delay_until_at_rest,
):
    """Handle run folder being done:

    - Move into ingested folder on source.
    - Update status meta data in destination collection.
    """
    src_folder = pathlib.Path(src_folder)
    # Get "last updated" time from meta data.
    last_update = None
    for meta in dst_collection.metadata.get_all(KEY_LAST_UPDATE):
        value = dateutil.parser.parse(meta.value)
        if last_update is None or value > last_update:
            last_update = value
    last_update_age = datetime.datetime.now() - (last_update or datetime.datetime.now())
    # Do not proceed if not marked as done.
    if not is_folder_done(src_folder):
        logger.info("folder %s is not marked as done" % src_folder)
        return
    # Move it data is considered at rest.
    if last_update_age > delay_until_at_rest:
        logger.info(
            "age of last update of %s is %s (<%s) -- will move to ingested"
            % (dst_collection, last_update_age, delay_until_at_rest)
        )
        new_src_folder = to_ingested_path(src_folder)
        logger.info("attempting move %s => %s" % (src_folder, new_src_folder))
        try:
            new_src_folder.parent.mkdir(exist_ok=True)
            src_folder.rename(new_src_folder)
        except OSError as e:
            logger.error("could not move to ingested: %s" % e)
        # Remove all old ``status`` meta data.
        logger.info("Marking destination collection as complete")
        for meta in dst_collection.metadata.get_all(KEY_STATUS):
            dst_collection.metadata.remove(meta)
        # set ``status`` meta data to not running any more.
        dst_collection.metadata.add(KEY_STATUS, "complete", "")
    else:
        logger.info(
            "age of last update of %s is %s (<%s) -- not moving to ingested"
            % (dst_collection, last_update_age, delay_until_at_rest)
        )


def pre_job(hdlr_mod, logger, meta):
    """Set the ``first_seen`` meta data value."""
    src_root = pathlib.Path(meta["root"])
    with cleanuping(irods_session(hdlr_mod=hdlr_mod, meta=meta, logger=logger)) as session:
        dst_root = session.collections.get(meta["target"])
        dst_collections = {c.name: c for c in dst_root.subcollections}
        for src_folder in sorted([f.name for f in sorted(src_root.iterdir())]):
            if src_folder in dst_collections:
                coll = dst_collections[src_folder]
                if not coll.metadata.get_all(KEY_FIRST_SEEN):
                    coll.metadata.add(KEY_FIRST_SEEN, datetime.datetime.now().isoformat(), "")
            else:
                logger.info("Skipping %s as it corresponds to no destination collection")


def post_job(hdlr_mod, logger, meta, is_folder_done: typing.Callable[[typing.Union[pathlib.Path, str]], bool], delay_until_at_rest):
    """Move completed run folders into the "ingested" area."""
    src_root = pathlib.Path(meta["root"])
    with cleanuping(irods_session(hdlr_mod=hdlr_mod, meta=meta, logger=logger)) as session:
        dst_root = session.collections.get(meta["target"])
        dst_collections = {c.name: c for c in dst_root.subcollections}
        for src_folder in sorted([f.name for f in sorted(src_root.iterdir())]):
            if src_folder in dst_collections:
                _post_job_run_folder_done(
                    logger,
                    session,
                    src_root / src_folder,
                    dst_collections[src_folder],
                    is_folder_done,
                    delay_until_at_rest,
                )
            else:
                logger.info("Skipping %s as it corresponds to no destination collection")


def refresh_last_update_metadata(logger, session, meta):
    """Update the ``last_update`` and ``status`` meta data value."""
    # Get path in irods that corresponds to root and update the meta data there.
    path = pathlib.Path(meta["path"])
    root = pathlib.Path(meta["root"])
    target = pathlib.Path(meta["target"])
    rel_root_path = path.relative_to(root)  # relative to root
    rel_folder_path = "/".join(str(rel_root_path).split("/")[1:])  # relative to run folder
    root_target = str(target)[: -(len(str(rel_folder_path)) + 1)]
    with cleanuping(session) as session:
        coll = session.collections.get(root_target)
        # Remove all old ``last_update`` meta data.
        for meta in coll.metadata.get_all(KEY_LAST_UPDATE):
            coll.metadata.remove(meta)
        # Add new ``last_update`` meta data.
        coll.metadata.add(KEY_LAST_UPDATE, datetime.datetime.now().isoformat(), "")
        # Add new ``status`` meta data if running.
        if not coll.metadata.get_all(KEY_STATUS):
            coll.metadata.add(KEY_STATUS, "running", "")
