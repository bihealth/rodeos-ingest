"""Test the settings of ``rodeos_ingest``"""

from rodeos_ingest import settings


def test_adjusted_settings():
    assert settings.RODEOS_DELAY_UNTIL_AT_REST_SECONDS == 1
    assert settings.RODEOS_HASHDEEP_THREADS == 8
    assert settings.RODEOS_HASHDEEP_ALGO == "md5"
    assert settings.RODEOS_LOOK_FOR_EXECUTABLES is True
