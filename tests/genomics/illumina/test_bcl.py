"""Tests for the functionality of ``omics_ingest.genomics.illumina.bcl``."""

import shutil

import omics_ingest.genomics.illumina.bcl


def prepare_run_folder(run_folder, tmp_path):
    instrument = run_folder.split("_")[1]
    work_path = tmp_path / "work"
    input_path = work_path / instrument
    input_path.mkdir(parents=True)
    ingested_path = work_path / ("%s-INGESTED" % instrument)
    ingested_path.mkdir(parents=True)
    shutil.copytree("tests/data/ingest_bcl/%s" % run_folder, str(input_path / run_folder))


def test_ingest_bcl(tmp_path):
    run_folder = "200305_NB502131_0093_AH2GWKAFX2"
    prepare_run_folder(run_folder, tmp_path)
