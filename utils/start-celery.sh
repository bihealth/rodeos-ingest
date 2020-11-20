#!/bin/bash

[[ "$VERBOSE" == "1" ]] && set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR/..

ENV_INGEST=${ENV_INGEST:-../env-ingest}
if [[ -z "$VIRTUAL_ENV" ]]; then
    source $ENV_INGEST/bin/activate
fi

LOG_LEVEL=${-error}

export CELERY_BROKER_URL=redis://127.0.0.1:6379/0
export PYTHONPATH=`pwd`
celery -A irods_capability_automated_ingest.sync_task worker -l "$LOG_LEVEL" -Q restart,path,file
