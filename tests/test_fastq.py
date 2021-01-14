"""Tests for the functionality of ``rodeos_ingest.genomics.illumina.fastq``.

See docstring of ``.bcl`` on collection of coverage information.
"""
from contextlib import closing
import datetime
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock

from irods.models import Collection
from irods_capability_automated_ingest.utils import Operation
from rodeos_ingest.genomics.illumina import fastq
from rodeos_ingest import common

from .conftest import (
    clear_redis,
    start_celery_worker,
    updated_env,
    wait_for_celery_worker,
    IRODS_SYNC_PY,
)


def prepare_fastq_folder(folder_name, tmp_path):
    """"Helper function to copy a folder on the file system."""
    work_path = tmp_path / "work"
    input_path = work_path / "FASTQ"
    input_path.mkdir(parents=True)
    ingested_path = work_path / "FASTQ-INGESTED"
    ingested_path.mkdir(parents=True)
    shutil.copytree("tests/data/ingest_fastq/%s" % folder_name, str(input_path / folder_name))
    return input_path


def test_system_ingest_fastq(
    tmp_path, irods,
):
    """System test for ``rodeos_ingest.genomics.illumina.fastq``."""
    # Setup iRODS
    dest_coll = "/tempZone/target"
    irods.create_collection(dest_coll, "rods")
    # Copy run folder from repository to temporary directory.
    folder_name = "200506_ST-K00106_0095_A_HFNLJBBXY"
    input_path = prepare_fastq_folder(folder_name, tmp_path)

    # Start celery and kickoff worker.
    job_name = "test-ingest-fastq"
    redis_url = "redis://redis:6379/0"
    with updated_env(
        RODEOS_HASHDEEP_ALGO="sha256",  # value in Docker image
        RODEOS_DELAY_UNTIL_AT_REST_SECONDS=0,
        REDIS_URL=redis_url,
        CELERY_BROKER_URL=redis_url,
    ):
        clear_redis()
        worker = start_celery_worker(1, write_logs=True)
        subprocess.run(
            [
                "coverage",
                "run",
                "-m",
                IRODS_SYNC_PY,
                "start",
                "--synchronous",
                "--exclude_file_name",
                ".*_MANIFEST_*.txt",
                "--event_handler",
                "rodeos_ingest.genomics.illumina.fastq",
                "--job_name",
                job_name,
                "--log_level",
                "INFO",
                "--files_per_task",
                "1",
                "--",
                str(input_path),
                dest_coll,
            ],
            check=False,
        )
        wait_for_celery_worker(worker, job_name)

    check_fastq_result(dest_coll, irods, input_path, folder_name)


def check_fastq_result(dest_coll, irods, input_path, folder_name):
    """Helper function that checks after the transfer."""
    # Must be marked as "complete".
    run_coll = "%s/%s" % (dest_coll, folder_name)
    coll_meta = {m.name: m for m in irods.session.metadata.get(Collection, run_coll)}
    assert "rodeos::ingest::status" in coll_meta
    assert coll_meta["rodeos::ingest::status"].value == "complete"
    # Check that the manifest files are present and have the correct content.
    mf_path = "%s/%s" % (run_coll, common.MANIFEST_IRODS)
    with closing(irods.session.data_objects.open(mf_path, "r")) as inputf:
        manifest_irods = inputf.read().decode("utf-8")
    assert list(sorted(manifest_irods.splitlines())) == [
        "0,sha2:47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=,./DIGESTIFLOW_DEMUX_DONE.txt",
        "0,sha2:47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=,./example2.txt",
    ]
    mf_path = "%s/%s" % (run_coll, common.MANIFEST_LOCAL)
    with closing(irods.session.data_objects.open(mf_path, "r")) as inputf:
        manifest_local = inputf.read().decode("utf-8")
    lines = list(sorted(manifest_local.splitlines()))
    lines[1] = lines[1].replace("$", "#")
    lines[2] = "## Invoked from: "
    assert lines == [
        "## ",
        "## # hashdeep -c sha256 -f /dev/stdin -j 8",
        "## Invoked from: ",
        "%%%% HASHDEEP-1.0",
        "%%%% size,sha256,filename",
        "0,e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855,./DIGESTIFLOW_DEMUX_DONE.txt",
        "0,e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855,./example2.txt",
    ]

    # Must have been moved locally.
    assert not (input_path / folder_name).exists()
    assert (Path(str(input_path) + "-INGESTED") / folder_name).exists()


def test_integration_ingest_fastq(
    tmp_path, irods, mocker,
):
    """Integration test for ``rodeos_ingest.genomics.illumina.ingest_bcl``."""
    mocker.patch.object(fastq, "DELAY_UNTIL_AT_REST", datetime.timedelta(seconds=30))
    mocker.patch.object(common, "HASHDEEP_ALGO", "sha256")

    # Setup iRODS
    dest_coll = Path("/tempZone/target")
    irods.create_collection(dest_coll, "rods")

    # Copy run folder from repository to temporary directory.
    folder_name = "200506_ST-K00106_0095_A_HFNLJBBXY"
    input_path = prepare_fastq_folder(folder_name, tmp_path)

    # Use irods-icommands to transfer the data.
    subprocess.check_call(["imkdir", "-p", "%s/%s" % (dest_coll, folder_name)])
    subprocess.check_call(
        [
            "irsync",
            "-r",
            "%s/%s/." % (input_path, folder_name),
            "i:%s/%s/." % (dest_coll, folder_name),
        ]
    )

    # Manually call the event handlers.
    hdlr_mod = fastq.event_handler
    logger = Mock()
    meta_base = {"root": str(input_path), "idle_disconnect_seconds": 60}
    session = irods.session
    fastq.event_handler.pre_job(hdlr_mod, logger, {**meta_base, "target": str(dest_coll)})
    for e in (input_path / folder_name).iterdir():
        if not (input_path / folder_name / e).is_dir():
            meta = {
                **meta_base,
                "target": str(dest_coll / folder_name / e.name),
                "path": str(input_path / folder_name / e.name),
            }
            fastq.event_handler.post_data_obj_create(hdlr_mod, logger, session, meta)
            fastq.event_handler.post_data_obj_update(hdlr_mod, logger, session, meta)
    mocker.patch.object(fastq, "DELAY_UNTIL_AT_REST", datetime.timedelta(seconds=0))
    fastq.event_handler.post_job(hdlr_mod, logger, {**meta_base, "target": str(dest_coll)})

    check_fastq_result(dest_coll, irods, input_path, folder_name)


def test_module():
    """Tests for functions that just return stuff."""
    hdlr_mod = fastq.event_handler
    logger = Mock()
    meta = {}
    assert fastq.event_handler.operation(hdlr_mod, logger) == Operation.PUT_APPEND
    assert fastq.event_handler.delay(hdlr_mod, logger, meta, 1) == 5
    assert fastq.event_handler.max_retries(hdlr_mod, logger, meta) == 10
