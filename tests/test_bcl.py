"""Tests for the functionality of ``omics_ingest.genomics.illumina.bcl``.

Note that no coverage information is generated from celery jobs right now:

- https://github.com/celery/celery/issues/3422
- https://github.com/nedbat/coveragepy/issues/689#issuecomment-656706935

Thus, we have a "system" end-to-end test here that will not generate any coverage information but
runs through celery and an "integration" test that runs the handler code manually.  If the
internal workings of ``irods_capability_automated_ingest`` changes then the integration test code
has to be adjusted accordingly.
"""
from contextlib import closing
import datetime
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock

from irods.models import Collection
from irods_capability_automated_ingest.utils import Operation
from omics_ingest.genomics.illumina import bcl
from omics_ingest import common

from .conftest import (
    clear_redis,
    start_celery_worker,
    updated_env,
    wait_for_celery_worker,
    IRODS_SYNC_PY,
)


def prepare_run_folder(run_folder, tmp_path):
    """"Helper function to copy a folder on the file system."""
    instrument = run_folder.split("_")[1]
    work_path = tmp_path / "work"
    input_path = work_path / instrument
    input_path.mkdir(parents=True)
    ingested_path = work_path / ("%s-INGESTED" % instrument)
    ingested_path.mkdir(parents=True)
    shutil.copytree("tests/data/ingest_bcl/%s" % run_folder, str(input_path / run_folder))
    return input_path


def test_system_ingest_bcl(
    tmp_path, irods,
):
    """System test for ``omics_ingest.genomics.illumina.bcl``."""
    # Setup iRODS
    dest_coll = "/tempZone/target"
    irods.create_collection(dest_coll, "rods")
    # Copy run folder from repository to temporary directory.
    run_folder = "200305_NB502131_0093_AH2GWKAFX2"
    input_path = prepare_run_folder(run_folder, tmp_path)

    # Start celery and kickoff worker.
    job_name = "test-ingest-bcl"
    redis_url = "redis://redis:6379/0"
    with updated_env(
        RODEOS_HASHDEEP_ALGO="sha256",  # value in Docker image
        RODEOS_DELAY_UNTIL_AT_REST_SECONDS=0,
        REDIS_URL=redis_url,
        CELERY_BROKER_URL=redis_url,
    ):
        clear_redis()
        worker = start_celery_worker(1)
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
                "omics_ingest.genomics.illumina.bcl",
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

    check_bcl_result(dest_coll, irods, input_path, run_folder)


def check_bcl_result(dest_coll, irods, input_path, run_folder):
    """Helper function that checks after the transfer."""
    # Must be marked as "complete".
    run_coll = "%s/%s" % (dest_coll, run_folder)
    coll_meta = {m.name: m for m in irods.session.metadata.get(Collection, run_coll)}
    assert "omics::ingest::status" in coll_meta
    assert coll_meta["omics::ingest::status"].value == "complete"
    # Check that the manifest files are present and have the correct content.
    mf_path = "%s/%s" % (run_coll, common.MANIFEST_IRODS)
    with closing(irods.session.data_objects.open(mf_path, "r")) as inputf:
        manifest_irods = inputf.read().decode("utf-8")
    assert list(sorted(manifest_irods.splitlines())) == [
        "10137,sha2:UEDeL3kiG4NYlxyN7SlO5uMUgR8SL5bsnxFg6rLJ0Uk=,./RunInfo.xml",
        "11317,sha2:3yL/yNigL8SDvriXhwoeWbfrdaaWerIbGAwG1Z1UsZU=,./RunParameters.xml",
        "35,sha2:qr8N53yv3KtHVhk0/S24my9QlicHMd81+qZIaCSZ8uU=,./RTARead3Complete.txt",
        "35,sha2:yfcIt1B/RK7p95hSErGD1aD+8pCcYheZn4RJSRhUImA=,./RTARead2Complete.txt",
        "36,sha2:ZuzPIoFrYgLB/Rdr3DNAM576yeNXdr6SGsCod3l/kgQ=,./RTARead1Complete.txt",
        "45,sha2:4PnYbezblFxFUWw40QMvdkoNVs3hO/1b+WS9ER3oNpI=,./RTAComplete.txt",
        "5712,sha2:Kmpk54OgbgzbtY9SEu1mRBykdiH6FuYSWz1XthglVFc=,./RTAConfiguration.xml",
    ]
    mf_path = "%s/%s" % (run_coll, common.MANIFEST_LOCAL)
    with closing(irods.session.data_objects.open(mf_path, "r")) as inputf:
        manifest_local = inputf.read().decode("utf-8")
    lines = list(sorted(manifest_local.splitlines()))
    lines[2] = "## Invoked from: "
    assert lines == [
        "## ",
        "## $ hashdeep -c sha256 -f /dev/stdin -j 8",
        "## Invoked from: ",
        "%%%% HASHDEEP-1.0",
        "%%%% size,sha256,filename",
        "10137,5040de2f79221b8358971c8ded294ee6e314811f122f96ec9f1160eab2c9d149,./RunInfo.xml",
        "11317,df22ffc8d8a02fc483beb897870a1e59b7eb75a6967ab21b180c06d59d54b195,./RunParameters.xml",
        "35,aabf0de77cafdcab47561934fd2db89b2f5096270731df35faa648682499f2e5,./RTARead3Complete.txt",
        "35,c9f708b7507f44aee9f7985212b183d5a0fef2909c6217999f84494918542260,./RTARead2Complete.txt",
        "36,66eccf22816b6202c1fd176bdc3340339efac9e35776be921ac0a877797f9204,./RTARead1Complete.txt",
        "45,e0f9d86decdb945c45516c38d1032f764a0d56cde13bfd5bf964bd111de83692,./RTAComplete.txt",
        "5712,2a6a64e783a06e0cdbb58f5212ed66441ca47621fa16e6125b3d57b618255457,./RTAConfiguration.xml",
    ]

    # Must have been moved locally.
    assert not (input_path / run_folder).exists()
    assert (Path(str(input_path) + "-INGESTED") / run_folder).exists()


def test_integration_ingest_bcl(
    tmp_path, irods, mocker,
):
    """Integration test for ``omics_ingest.genomics.illumina.ingest_bcl``."""
    mocker.patch.object(bcl, "DELAY_UNTIL_AT_REST", datetime.timedelta(seconds=30))
    mocker.patch.object(common, "HASHDEEP_ALGO", "sha256")

    # Setup iRODS
    dest_coll = Path("/tempZone/target")
    irods.create_collection(dest_coll, "rods")

    # Copy run folder from repository to temporary directory.
    run_folder = "200305_NB502131_0093_AH2GWKAFX2"
    input_path = prepare_run_folder(run_folder, tmp_path)

    # Use irods-icommands to transfer the data.
    subprocess.check_call(["imkdir", "-p", "%s/%s" % (dest_coll, run_folder)])
    subprocess.check_call(
        [
            "irsync",
            "-r",
            "%s/%s/." % (input_path, run_folder),
            "i:%s/%s/." % (dest_coll, run_folder),
        ]
    )

    # Manually call the event handlers.
    hdlr_mod = bcl.event_handler
    logger = Mock()
    meta_base = {"root": str(input_path), "idle_disconnect_seconds": 60}
    session = irods.session
    bcl.event_handler.pre_job(hdlr_mod, logger, {**meta_base, "target": str(dest_coll)})
    for e in (input_path / run_folder).iterdir():
        if not (input_path / run_folder / e).is_dir():
            meta = {
                **meta_base,
                "target": str(dest_coll / run_folder / e.name),
                "path": str(input_path / run_folder / e.name),
            }
            bcl.event_handler.post_data_obj_create(hdlr_mod, logger, session, meta)
            bcl.event_handler.post_data_obj_update(hdlr_mod, logger, session, meta)
    mocker.patch.object(bcl, "DELAY_UNTIL_AT_REST", datetime.timedelta(seconds=0))
    bcl.event_handler.post_job(hdlr_mod, logger, {**meta_base, "target": str(dest_coll)})

    check_bcl_result(dest_coll, irods, input_path, run_folder)


def test_module():
    """Tests for functions that just return stuff."""
    hdlr_mod = bcl.event_handler
    logger = Mock()
    meta = {}
    assert bcl.event_handler.operation(hdlr_mod, logger) == Operation.PUT_SYNC
    assert bcl.event_handler.delay(hdlr_mod, logger, meta, 1) == 5
    assert bcl.event_handler.max_retries(hdlr_mod, logger, meta) == 10
