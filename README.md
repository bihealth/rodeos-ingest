[![Documentation Status](https://readthedocs.org/projects/cubi-omics-data-access/badge/?version=latest)](https://cubi-omics-data-access.readthedocs.io/en/latest/?badge=latest)
![Continuous Integration Status](https://github.com/bihealth/cubi-omics-data-access/workflows/CI/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2eaafb57fbb74a46b918e9f58142c880)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=bihealth/cubi-omics-data-access&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2eaafb57fbb74a46b918e9f58142c880)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/cubi-omics-data-access&amp;utm_campaign=Badge_Grade)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

# omics-irods-ingest


Code for ingesting omics data into omics storage based on iRODS capabilities

## iRODS Ingest Event Handler Modules

- `omics_ingest.genomics.illumina.bcl` --
  Ingest a landing zone folder where Illumina instruments write their run folders to.
- `omics_ingest.genomics.illumina.fastq` --
  Ingest a landing zone folder for demultiplexing results.

## Developer Information

- https://robinpokorny.github.io/git3moji/
