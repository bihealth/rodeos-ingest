"""Common code for the omics ingest."""

import base64
from contextlib import contextmanager
import datetime
import os
import os.path
import pathlib
import subprocess  # nosec
import tempfile
import typing

import dateutil.parser
from irods_capability_automated_ingest.sync_irods import irods_session
from irods.meta import iRODSMeta

from .settings import (
    RODEOS_HASHDEEP_ALGO as HASHDEEP_ALGO,
    RODEOS_HASHDEEP_THREADS as HASHDEEP_THREADS,
    RODEOS_MANIFEST_LOCAL as MANIFEST_LOCAL,
    RODEOS_MANIFEST_IRODS as MANIFEST_IRODS,
    RODEOS_MOVE_AFTER_INGEST as _MOVE_AFTER_INGEST,
)

#: AVU key to use for ``last_update`` attribute.
KEY_LAST_UPDATE = "rodeos::ingest::last_update"
#: AVU key to use destionation run folder ingestion status.
KEY_STATUS = "rodeos::ingest::status"
#: AVU key to use for ``first_seen`` attribute.
KEY_FIRST_SEEN = "rodeos::ingest::first_seen"
#: AVU key for manifest status
KEY_MANIFEST_STATUS = "rodeos::ingest::manifest_status"
#: AVU key with manifest detailed message
KEY_MANIFEST_MESSAGE = "rodeos::ingest::manifest_message"

MOVE_AFTER_INGEST = _MOVE_AFTER_INGEST


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


def _compare_manifests(path_local, path_irods, logger):
    """Compare manifests at paths ``path_local`` and ``path_irods``."""
    # Load file sizes and checksums.
    info_local = {}
    with open(path_local, "rt") as inputf:
        for line in inputf:
            if line.startswith("#") or line.startswith("%"):
                continue
            line = line.strip()
            size, chksum, path = line.split(",", 2)
            info_local[path] = (size, chksum)
    info_irods = {}
    with open(path_irods, "rt") as inputf:
        for line in inputf:
            line = line.strip()
            size, chksum, path = line.split(",", 2)
            if chksum.startswith("sha2:"):
                chksum = base64.b64decode(chksum[5:]).hex()
            info_irods[path] = (size, chksum)

    # Compare file sizes and checksums.
    problem = None
    for path in sorted(info_local.keys() & info_irods.keys()):
        size_local, chksum_local = info_local[path]
        size_irods, chksum_irods = info_irods[path]
        if size_local != size_irods:
            problem = "file size mismatch %s vs %s for %s" % (size_local, size_irods, path)
            logger.error(
                "file size does not match %s vs %s for %s" % (size_local, size_irods, path)
            )
        if chksum_local != chksum_irods:
            problem = "file checksum mismatch %s vs %s for %s" % (chksum_local, chksum_irods, path)
            logger.error(
                "file checksum does not match %s vs %s for %s" % (chksum_local, chksum_irods, path)
            )
    # Find extra items on either side.
    extra_local = info_local.keys() - info_irods.keys()
    if sorted(extra_local):
        problem = "extra file in local: %s" % list(sorted(extra_local))[0]
        logger.error(
            "%d items locally that are not in irods, up to 10 shown:\n  %s"
            % (len(extra_local), "  \n".join(list(sorted(extra_local))[:10]))
        )
    extra_irods = info_irods.keys() - info_local.keys()
    if sorted(extra_irods):
        problem = "extra file in irods : %s" % list(sorted(extra_irods))[0]
        logger.error(
            "%d items in irods that are not present locally, up to 10 shown:\n  %s"
            % (len(extra_irods), "  \n".join(list(sorted(extra_irods))[:10]))
        )

    if problem:
        raise RuntimeError("Difference in manifests: %s" % problem)


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
    now = datetime.datetime.now()
    last_update_age = now - (last_update or now)
    # Do not proceed if not marked as done.
    if not is_folder_done(src_folder):  # pragma: no cover
        logger.info("folder %s is not marked as done" % src_folder)
        return
    # Compute and check manifest and move if data is considered at rest.
    if last_update_age >= delay_until_at_rest:
        logger.info(
            "age of last update of %s is %s (<%s) -- will finalize (manifest+move)"
            % (dst_collection.path, last_update_age, delay_until_at_rest)
        )
        local_path = compute_local_manifest(logger, src_folder)
        irods_path = compute_irods_manifest(dst_collection, logger, src_folder)
        # Compare the manifest files.
        try:
            _compare_manifests(local_path, irods_path, logger)
        except RuntimeError as e:  # pragma: no cover
            dst_collection.metadata[KEY_MANIFEST_STATUS] = iRODSMeta(
                KEY_MANIFEST_STATUS, "failed", ""
            )
            dst_collection.metadata[KEY_MANIFEST_MESSAGE] = iRODSMeta(
                KEY_MANIFEST_MESSAGE, str(e), ""
            )
            raise
        else:
            dst_collection.metadata[KEY_MANIFEST_STATUS] = iRODSMeta(
                KEY_MANIFEST_STATUS, "success", ""
            )
            dst_collection.metadata[KEY_MANIFEST_MESSAGE] = iRODSMeta(
                KEY_MANIFEST_MESSAGE, "all good", ""
            )
        # Put local hashdeep manifest.
        local_manifest_dest = os.path.join(dst_collection.path, MANIFEST_LOCAL)
        session.data_objects.put(local_path, local_manifest_dest)
        run_ichksum(local_manifest_dest)
        # Put manifest built from irods.
        irods_manifest_dest = os.path.join(dst_collection.path, MANIFEST_IRODS)
        session.data_objects.put(irods_path, irods_manifest_dest)
        run_ichksum(irods_manifest_dest)
        # Move folder.
        if MOVE_AFTER_INGEST:
            new_src_folder = to_ingested_path(src_folder)
            logger.info("attempting move %s => %s" % (src_folder, new_src_folder))
            try:
                new_src_folder.parent.mkdir(exist_ok=True)
                src_folder.rename(new_src_folder)
            except OSError as e:  # pragma: no cover
                logger.error("could not move to ingested: %s" % e)
        else:
            logger.info("configured to not move %s" % src_folder)
        # Update ``status`` meta data.
        dst_collection.metadata[KEY_STATUS] = iRODSMeta(KEY_STATUS, "complete", "")
    else:
        logger.info(
            "age of last update of %s is %s (<%s) -- not moving to ingested"
            % (dst_collection.path, last_update_age, delay_until_at_rest)
        )


def compute_irods_manifest(dst_collection, logger, src_folder):
    """Compute manifest from irods checksums."""
    logger.info("pull irods checksums into manifest")
    irods_path = os.path.join(src_folder, MANIFEST_IRODS)
    try:
        with tempfile.TemporaryFile("w+t") as tmp_f:
            # Obtain information for files directly in destination collection.
            cmd = [
                "iquest",
                "%d,%s,%s/%s",
                (
                    "SELECT DATA_SIZE, DATA_CHECKSUM, COLL_NAME, DATA_NAME "
                    "WHERE COLL_NAME = '%s' AND DATA_NAME != '%s' AND DATA_NAME != '%s'"
                )
                % (dst_collection.path, MANIFEST_LOCAL, MANIFEST_IRODS),
            ]
            subprocess.run(cmd, stdout=tmp_f, encoding="utf-8", check=True)  # nosec
            # Obtain information for files destination subcollections.
            cmd_sub = [
                "iquest",
                "%d,%s,%s/%s",
                (
                    "SELECT DATA_SIZE, DATA_CHECKSUM, COLL_NAME, DATA_NAME "
                    "WHERE COLL_NAME like '%s/%%'"
                )
                % dst_collection.path,
            ]
            subprocess.run(cmd_sub, stdout=tmp_f, encoding="utf-8", check=True)  # nosec
            # Copy to final output file.
            tmp_f.flush()
            tmp_f.seek(0)
            with open(irods_path, "wt") as chk_f:
                for line in tmp_f:
                    line = line.strip()
                    if line.startswith("CAT_NO_ROWS_FOUND"):
                        continue
                    size, chksum, path = line.split(",", 2)
                    path = ".%s" % path[len(dst_collection.path) :]
                    print(",".join([size, chksum, path]), file=chk_f)

    except subprocess.CalledProcessError as e:  # pragma: no cover
        logger.warn("Creation of iRODS manifest failed, aborting: %s" % e)
        os.remove(irods_path)
        raise
    return irods_path


def compute_local_manifest(logger, src_folder):
    """Compute local hashdeep manifest."""
    local_path = os.path.join(src_folder, MANIFEST_LOCAL)
    logger.info("compute checksums and store to %s" % local_path)
    try:
        with open(local_path, "wt") as chk_f:
            cmd_find = [
                "find",
                ".",
                "-type",
                "f",
                "-and",
                "-not",
                "-path",
                "./%s" % MANIFEST_LOCAL,
                "-and",
                "-not",
                "-path",
                "./%s" % MANIFEST_IRODS,
            ]
            p_find = subprocess.Popen(cmd_find, cwd=src_folder, stdout=subprocess.PIPE,)  # nosec
            subprocess.run(  # nosec
                ["hashdeep", "-c", HASHDEEP_ALGO, "-f", "/dev/stdin", "-j", str(HASHDEEP_THREADS),],
                cwd=src_folder,
                stdin=p_find.stdout,
                stdout=chk_f,
                encoding="utf-8",
                check=True,
            )
            if p_find.wait() != 0:  # pragma: no cover
                raise subprocess.CalledProcessError(
                    cmd_find, "Problem running find: %s" % p_find.returncode
                )
    except subprocess.CalledProcessError as e:  # pragma: no cover
        logger.warn("Computing checksums failed, aborting: %s" % e)
        os.remove(local_path)
        raise
    return local_path


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
                    coll.metadata[KEY_FIRST_SEEN] = iRODSMeta(
                        KEY_FIRST_SEEN, datetime.datetime.now().isoformat(), ""
                    )
            else:
                logger.info("Skipping %s as it corresponds to no destination collection")


def post_job(
    hdlr_mod,
    logger,
    meta,
    is_folder_done: typing.Callable[[typing.Union[pathlib.Path, str]], bool],
    delay_until_at_rest,
):
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
    _ = logger
    # Get path in irods that corresponds to root and update the meta data there.
    path = pathlib.Path(meta["path"])
    root = pathlib.Path(meta["root"])
    target = pathlib.Path(meta["target"])
    logger.info("meta = %s" % meta)
    print("meta = %s" % meta)
    rel_root_path = path.relative_to(root)  # relative to root
    print("... %s" % rel_root_path)
    rel_folder_path = "/".join(str(rel_root_path).split("/")[1:])  # relative to run folder
    print("... %s" % rel_folder_path)
    root_target = str(target)[: -(len(str(rel_folder_path)) + 1)]
    print("... %s" % root_target)
    with cleanuping(session) as wrapped_session:
        coll = wrapped_session.collections.get(root_target)
        # Replace ``last_update`` and ``status`` meta data.
        coll.metadata[KEY_LAST_UPDATE] = iRODSMeta(
            KEY_LAST_UPDATE, datetime.datetime.now().isoformat(), ""
        )
        coll.metadata[KEY_STATUS] = iRODSMeta(KEY_STATUS, "running", "")


def run_ichksum(irods_path: str) -> None:
    """Run ``ichksum $irods_path``."""
    subprocess.run(["ichksum", irods_path], check=True)
