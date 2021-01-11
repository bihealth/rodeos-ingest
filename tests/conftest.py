import contextlib
import os
from pwd import getpwnam
import typing

import attr
from irods.access import iRODSAccess
from irods.exception import UserDoesNotExist
from irods.session import iRODSSession
import pytest
from pytest_redis import factories


#: Define ``redisdb`` fixture to connect to an already running redis server
#: such as on CI.
redisdb = factories.redisdb("redis_nooproc")


def make_irods_session(**kwargs):
    """Helper to make a new iRODS session."""
    try:
        env_file = kwargs["irods_env_file"]
    except KeyError:
        try:
            env_file = os.environ["IRODS_ENVIRONMENT_FILE"]
        except KeyError:
            env_file = os.path.expanduser("~/.irods/irods_environment.json")

    try:
        os.environ["IRODS_CI_TEST_RUN"]
        uid = getpwnam("irods").pw_uid
    except KeyError:
        uid = None

    return iRODSSession(irods_authentication_uid=uid, irods_env_file=env_file)


@attr.s(frozen=True, auto_attribs=True)
class IrodsUserInfo:
    """Information for a user."""

    #: The name of the user.
    name: str
    #: Password to set for the user.
    password: str
    # The user type.
    user_type: str = "rodsuser"


class IrodsFixture:
    """Helper class for managing setUp/tearDown within iRODS."""

    def __init__(self, **kwargs):
        self.session = make_irods_session(**kwargs)
        # The zone name (hard-coded for now).
        self.zone_name = "tempZone"
        # The users created through this sesssion.
        self._users = []
        # The collections created through this session.
        self._collections = []

    def create_user(self, name: str, password: str, user_type=None) -> None:
        """Create user and mark for deletion when tearing down."""
        user_type = user_type or "rodsuser"
        self._users.append(IrodsUserInfo(name, password, user_type))
        self.session.users.create(name, user_type, self.zone_name)
        self.session.users.modify(name, "password", password)

    def create_collection(
        self, path: str, owner: typing.Optional[str] = None, recursive: bool = True
    ) -> None:
        """Create a collection."""
        self._collections.append(path)
        self.session.collections.create(path)
        if owner:
            acl = iRODSAccess("inherit", path, user_name=owner or "")
            self.session.permissions.set(acl, recursive=recursive)

    def _tear_down(self):
        # Remove users.
        for user in self._users:
            obj = self.session.users.get(user.name, self.zone_name)
            if obj:
                try:
                    obj.remove()
                except UserDoesNotExist:
                    pass  # swallow
        # Remove collections.
        for coll in reversed(self._collections):
            self.session.collections.remove(coll, force=True)
        # Cleanup session with connection pool.
        self.session.cleanup()


@pytest.fixture()
def irods():
    fixture = IrodsFixture()
    yield fixture
    fixture._tear_down()
