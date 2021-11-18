#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

#python \
#    -m irods_capability_automated_ingest.irods_sync \
#    start \
#        "$SRC" \
#        "$DEST" \
#        --event_handler rodeos_ingest.genomics.illumina.bcl \
#        $ARGS_BACKGROUND

iinit rods

echo $(which celery)

#tail -f /dev/null

#celery -A irods_capability_automated_ingest.sync_task worker -l "$LOG_LEVEL" -Q restart,path,file &
celery -A irods_capability_automated_ingest.sync_task worker -l error -Q restart,path,file -c 4 &

echo $PWD

env

tail -f /dev/null

py.test -v -x ./tests

tail -f /dev/null
