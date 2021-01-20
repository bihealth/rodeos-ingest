.. _dev_overview:

==================
Developer Overview
==================

Contributions are welcome via GitHub pull requests.
Continuous integration (CI) has been setup and it is expected that patches are accompanied with appropriate tests.
Further, static analysis and coverage analysis via Codacy is integrated via CI and it is expected that code does not strongly decrease code coverage or introduce true issues detected by static analysis.

---------------
Commit Messages
---------------

Prefix your commit messages with 3 letter emojis as documented here.

- https://robinpokorny.github.io/git3moji/

-----------------
Development Setup
-----------------

The following currently is a sketch only.

- install redis or run via docker
- add ``redis`` to ``/etc/hosts`` with appropriate IP (e.g., localhost)
- install irods or run via docker
- add ``irods`` to ``/etc/hosts`` with appropriate IP (e.g., localhost)
- setup ``.irods/irods_environment.json`` file, e.g. ::

        {
            "irods_host": "irods",
            "irods_port": 1247,
            "irods_authentication_scheme": "NATIVE",
            "irods_default_hash_scheme": "MD5",
            "irods_zone_name": "tempZone",
            "irods_user_name": "rods",
            "irods_password": "rods"
        }
