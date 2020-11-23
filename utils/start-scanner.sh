#!/bin/bash

[[ "$VERBOSE" == "1" ]] && set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR/..

ENV_INGEST=${ENV_INGEST:-../env-ingest}
if [[ -z "$VIRTUAL_ENV" ]]; then
    source $ENV_INGEST/bin/activate
fi

export CELERY_BROKER_URL=redis://127.0.0.1:6379/0
export PYTHONPATH=`pwd`

ZONE=${ZONE:-omicsTestingZone}
SITE=test-site
DEVICE=${DEVICE:-M06205}
DEST="/$ZONE/$SITE/raw-data/$DEVICE"
SRC=${SRC-utils/example}
BACKGROUND=${BACKGROUND:-0}

ARGS_BACKGROUND=""
if [[ "$BACKGROUND" -ne 1 ]]; then
    ARGS_BACKGROUND="--synchronous --progress"
fi

imkdir -p "$DEST"

python \
    -m irods_capability_automated_ingest.irods_sync \
    start \
        "$SRC" \
        "$DEST" \
        --event_handler omics_ingest.genomics.illumina \
        $ARGS_BACKGROUND
