[![Documentation Status](https://readthedocs.org/projects/rodeos-ingest/badge/?version=latest)](https://rodeos-ingest.readthedocs.io/en/latest/?badge=latest)
![Continuous Integration Status](https://github.com/bihealth/cubi-omics-data-access/workflows/CI/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/4d09b08edd034c538e1d7247df7b5684)](https://www.codacy.com/gh/bihealth/rodeos-ingest/dashboard?utm_source=github.com&utm_medium=referral&utm_content=bihealth/rodeos-ingest&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/4d09b08edd034c538e1d7247df7b5684)](https://www.codacy.com/gh/bihealth/rodeos-ingest/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/rodeos-ingest&amp;utm_campaign=Badge_Grade)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

# RODEOS Ingest

Code for ingesting omics data into iRODS based on [iRODS capability automated ingest](https://github.com/irods/irods_capability_automated_ingest).

## iRODS Ingest Event Handler Modules

- `rodeos_ingest.genomics.illumina.bcl` --
  Ingest a landing zone folder where Illumina instruments write their run folders to.
- `rodeos_ingest.genomics.illumina.fastq` --
  Ingest a landing zone folder for demultiplexing results.

## Developer Information

### Commit Message Emojis

- https://robinpokorny.github.io/git3moji/

## Development Setup

- install redis or run via docker
- add `redis` to `/etc/hosts` with appropriate IP (e.g., localhost)
- install irods or run via docker
- add `irods` to `/etc/hosts` with appropriate IP (e.g., localhost)
- setup `.irods/irods_environment.json` file, e.g.
    ```json
    {
        "irods_host": "irods",
        "irods_port": 1247,
        "irods_authentication_scheme": "NATIVE",
        "irods_default_hash_scheme": "MD5",
        "irods_zone_name": "tempZone",
        "irods_user_name": "rods",
        "irods_password": "rods"
    }
    ```
