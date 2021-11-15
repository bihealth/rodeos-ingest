#!/bin/bash

#python \
#    -m irods_capability_automated_ingest.irods_sync \
#    start \
#        "$SRC" \
#        "$DEST" \
#        --event_handler rodeos_ingest.genomics.illumina.bcl \
#        $ARGS_BACKGROUND

iinit rods

#celery -A irods_capability_automated_ingest.sync_task worker -l error -Q restart,path,file -c 4 &

echo $PWD

env

py.test -v -x ./tests

tail -f /dev/null
