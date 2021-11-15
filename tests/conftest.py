import contextlib
import os
from pwd import getpwnam
import subprocess
import time
import typing

import attr
from celery import Celery
from irods.access import iRODSAccess
from irods.models import DataObject, Collection, User
from irods.session import iRODSSession
from redis import StrictRedis, ConnectionPool
#from irods_capability_automated_ingest.sync_job import sync_job

def tasks_key(job_name):
    return "tasks:/"+job_name

def get_with_key(r, key, path, typefunc):
    sync_time_bs = r.get(key(path))
    if sync_time_bs is None:
        sync_time = None
    else:
        sync_time = typefunc(sync_time_bs)
    return sync_time

def done(r, job_name):
    ntasks = get_with_key(r, tasks_key, job_name, int)
    return ntasks is None or ntasks == 0

import pytest


@pytest.fixture(scope="session")
def celery_config():
    return {"broker_url": "memory://", "result_backend": "redis://"}


#: Path to configuration file for ingest user.
IRODS_ENV_INGEST = os.path.realpath(".github/workflows/ci/irods_environment-ingest.json")

#: Module to sync tool.
IRODS_SYNC_PY = "irods_capability_automated_ingest.irods_sync"


@contextlib.contextmanager
def updated_env(**kwargs):
    prev = os.environ.copy()
    for k, v in kwargs.items():
        os.environ[k] = str(v)
    yield
    os.environ.clear()
    os.environ.update(prev)


def make_irods_session(**kwargs):
    """Helper to make a new iRODS session."""
    try:
        env_file = kwargs["irods_env_file"]
    except KeyError:
        try:
            env_file = os.environ["IRODS_ENVIRONMENT_FILE"]
            if not env_file:
                env_file = IRODS_ENV_INGEST
        except KeyError:
            env_file = os.path.expanduser("~/.irods/irods_environment.json")

    print(f"{env_file} has been chosen")

    try:
        #_ = os.environ["IRODS_CI_TEST_RUN"]
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
        self.zone_name = "rodeosZone"
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
            own_acl = iRODSAccess("own", path, user_name=owner or "")
            self.session.permissions.set(own_acl, recursive=recursive)
        inherit_acl = iRODSAccess("inherit", path, user_name=owner or "")
        self.session.permissions.set(inherit_acl, recursive=recursive)

    def tear_down(self):
        # Cleanup users and data.
        self._cleanup()
        # Cleanup session with connection pool.
        self.session.cleanup()


@pytest.fixture()
def irods():
    """Initialize a new ``IrodsFixture``."""
    fixture = IrodsFixture()
    yield fixture
    fixture.tear_down()


def start_celery_worker(n, args=None, write_logs=False):
    """Start celery worker with ``n`` threads and additional ``args``."""
    if write_logs:
        log_args = ["-f", "worker.log"]
    else:
        log_args = []
    worker = subprocess.Popen(
        [
            "celery",
            "-A",
            "irods_capability_automated_ingest.sync_task",
            "worker",
            "-c",
            str(n),
            "-l",
            "INFO",
            "-Q",
            "restart,path,file",
        ]
        + log_args
        + (args or [])
    )
    return worker


def wait_for_celery_worker(worker, job_name="job-name", timeout=60):
    """Wait for the celery process (``Popen`` in ``worker``) to finish all tasks
    for job ``job_name`` using a timeout of ``timeout`` (``None`` implies no timeout).
    """
    # Wait for all jobs to be complete.
    r = get_redis()
    t0 = time.time()
    while timeout is None or time.time() - t0 < timeout:
        restart = r.llen("restart")
        i = app.control.inspect()
        act = i.active()
        if act is None:
            active = 0
        else:
            active = sum(map(len, act.values()))
        #d = sync_job.done(r, job_name)
        d = done(r, job_name)
        if restart != 0 or active != 0 or not d:
            time.sleep(1)
        else:
            break

    # Try really hard for half a second to kill celery.
    t_end = time.time() + 0.5
    while timeout is None or time.time() < t_end:
        worker.terminate()
    worker.wait()


app = Celery("icai")


redis_connection_pool_map = {}


def sync_utils_get_redis(config):
    redis_config = config["redis"]
    host = redis_config["host"]
    port = redis_config["port"]
    db = redis_config["db"]
    url = "redis://" + host + ":" + str(port) + "/" + str(db)
    pool = redis_connection_pool_map.get(url)
    if pool is None:
        pool = ConnectionPool(host=host, port=port, db=db)
        redis_connection_pool_map[url] = pool

    return StrictRedis(connection_pool=pool)


def get_redis(host="redis", port=6379, db=0):
    redis_config = {}
    redis_config["host"] = host
    redis_config["port"] = port
    redis_config["db"] = db
    config = {}
    config["redis"] = redis_config
    return sync_utils_get_redis(config)


def clear_redis():
    get_redis().flushdb()
