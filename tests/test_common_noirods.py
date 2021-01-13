"""Tests for code in ``rodeos_ingest.common`` that does not need irods."""

import pathlib
from unittest.mock import MagicMock

import pytest

from rodeos_ingest.common import cleanuping, to_ingested_path, _compare_manifests


def test_cleanuping():
    m = MagicMock()
    m.cleanup = MagicMock()
    with cleanuping(m):
        assert not m.cleanup.called
    assert m.cleanup.called


def test_to_ingested_path_str():
    assert to_ingested_path("foo/bar") == pathlib.Path("foo-INGESTED/bar")


def test_to_ingested_path_pathlib():
    assert to_ingested_path(pathlib.Path("foo/bar")) == pathlib.Path("foo-INGESTED/bar")


def _test_compare_manifests(tmp_path, lines_local, lines_irods):
    logger = MagicMock()
    p_local = tmp_path / "local.txt"
    with p_local.open("wt") as f_local:
        print("\n".join(lines_local), file=f_local)
    p_irods = tmp_path / "irods.txt"
    with p_irods.open("wt") as f_irods:
        print("\n".join(lines_irods), file=f_irods)
    return _compare_manifests(str(p_local), str(p_irods), logger) is None


def test_compare_manifests_equal(tmp_path):
    assert (
        _test_compare_manifests(
            tmp_path,
            ["#", "%", "10,xyz,./name.txt", "20,abc,./name2.txt"],
            ["20,abc,./name2.txt", "10,xyz,./name.txt"],
        )
        is True
    )


def test_compare_manifests_diff_sizes(tmp_path):
    with pytest.raises(RuntimeError):
        _test_compare_manifests(
            tmp_path,
            ["#", "%", "10,xyz,./name.txt", "21,abc,./name2.txt"],
            ["20,abc,./name2.txt", "10,xyz,./name.txt"],
        )


def test_compare_manifests_diff_checksum(tmp_path):
    with pytest.raises(RuntimeError):
        _test_compare_manifests(
            tmp_path,
            ["#", "%", "10,xyz,./name.txt", "20,abd,./name2.txt"],
            ["20,abc,./name2.txt", "10,xyz,./name.txt"],
        )


def test_compare_manifests_diff_more_local(tmp_path):
    with pytest.raises(RuntimeError):
        _test_compare_manifests(
            tmp_path, ["#", "%", "10,xyz,./name.txt", "20,abc,./name2.txt"], ["20,abc,./name2.txt"],
        )


def test_compare_manifests_diff_more_irods(tmp_path):
    with pytest.raises(RuntimeError):
        _test_compare_manifests(
            tmp_path, ["#", "%", "10,xyz,./name.txt"], ["20,abc,./name2.txt", "10,xyz,./name.txt"],
        )
