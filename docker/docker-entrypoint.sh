#!/bin/bash

#imkdir -p "$DEST"

python \
    -m irods_capability_automated_ingest.irods_sync \
    start \
        "$SRC" \
        "$DEST" \
        --event_handler rodeos_ingest.genomics.illumina.bcl \
        $ARGS_BACKGROUND
