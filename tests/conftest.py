import os
from pwd import getpwnam
import typing

import attr
from irods.access import iRODSAccess
from irods.models import DataObject, Collection, User
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
        _ = os.environ["IRODS_CI_TEST_RUN"]
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
        #: The zone name (hard-coded for now).
        self.zone_name = "tempZone"
        #: The super user name.
        self.rods_user_name = "rods"
        #: The users created through this sesssion.
        self._users = []
        #: The collections created through this session.
        self._collections = []
        # Cleanup at startup.
        self._cleanup()

    def _cleanup(self):
        """Cleanup data, to be executed at startup."""
        # Remove all users except for the rods user.
        for user_rec in self.session.query(User).all():
            if user_rec[User.name] not in (self.rods_user_name, "public", "rodsadmin"):
                self.session.users.get(user_rec[User.name]).remove()
        # Remove data objects.
        for dobj_rec in self.session.query(DataObject).order_by(DataObject.name).all():
            coll_rec = (
                self.session.query(Collection)
                .filter(Collection.id == dobj_rec[DataObject.collection_id])
                .first()
            )
            self.session.data_objects.unlink(
                "%s/%s" % (coll_rec[Collection.name], dobj_rec[DataObject.name]), force=True
            )
        # Remove all collections except for the rods home.
        keep_colls = tuple(
            "/%s/%s/" % (self.zone_name, x)
            for x in ("home/%s" % self.rods_user_name, "home/public", "trash/home")
        )
        for coll_rec in (
            self.session.query(Collection).order_by(Collection.name, order="desc").all()
        ):
            coll_path = coll_rec[Collection.name]
            if not coll_path.endswith("/"):
                coll_path = "%s/" % coll_path
            if not any(keep_coll.startswith(coll_path) for keep_coll in keep_colls):
                self.session.collections.remove(coll_path[:-1], force=True)

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

    def tear_down(self):
        # Cleanup users and data.
        self._cleanup()
        # Cleanup session with connection pool.
        self.session.cleanup()


@pytest.fixture()
def irods():
    fixture = IrodsFixture()
    yield fixture
    fixture.tear_down()
