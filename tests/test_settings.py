"""Test the settings of ``omics_ingest``"""

import pytest  # noqa


def test_pass(redisdb, irods):
    irods.create_user("ingest", "ingest")
    irods.create_collection("/%s/some" % irods.zone_name, "ingest")
    irods.create_collection("/%s/some/path" % irods.zone_name, "ingest")
    assert True
