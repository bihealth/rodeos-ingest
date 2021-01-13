[![Documentation Status](https://readthedocs.org/projects/cubi-omics-data-access/badge/?version=latest)](https://cubi-omics-data-access.readthedocs.io/en/latest/?badge=latest)
![Continuous Integration Status](https://github.com/bihealth/cubi-omics-data-access/workflows/CI/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2eaafb57fbb74a46b918e9f58142c880)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=bihealth/cubi-omics-data-access&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2eaafb57fbb74a46b918e9f58142c880)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/cubi-omics-data-access&amp;utm_campaign=Badge_Grade)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

# omics-irods-ingest

Code for ingesting omics data into iRODS based on [iRODS capability automated ingest](https://github.com/irods/irods_capability_automated_ingest).

## iRODS Ingest Event Handler Modules

- `omics_ingest.genomics.illumina.bcl` --
  Ingest a landing zone folder where Illumina instruments write their run folders to.
- `omics_ingest.genomics.illumina.fastq` --
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
