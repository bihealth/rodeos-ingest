#!/bin/bash

#set -euo pipefail
#IFS=$'\n\t'

/usr/local/bin/wait
sleep 5 # sometimes port is already open during data base setup


if [[ "$1" == "run-tests" ]]; then
    cp .github/workflows/ci/irods_environment-rods.json /root/.irods/irods_environment.json
    echo $IRODS_PASS | iinit
    if [ $? -ne 0 ]; then
        echo "iinit failed"
    fi

    py.test -v -x ./tests


elif [[ "$1" == "run-ingest" ]]; then
    envsubst < /root/.irods/irods_environment.json.tmpl > /root/.irods/irods_environment.json
    echo $IRODS_PASS | iinit
    if [ $? -ne 0 ]; then
        echo "iinit failed"
    fi

    celery -A irods_capability_automated_ingest.sync_task worker -l error -Q restart,path,file -c 12 &

    for i in $RODEOS_INGEST_PATH/*; do
        echo "Going for the following ingest path:"
        echo $i
        TARGET=/$IRODS_ZONE_NAME/home/$IRODS_USER/$RODEOS_TARGET_COLLECTION
        DIR=$(basename $i)
        YEAR=20${DIR::2}  # first two chars
        imkdir $TARGET
        imkdir $TARGET/$YEAR
        imkdir $TARGET/$YEAR/$DIR

        python -m irods_capability_automated_ingest.irods_sync start \
            --event_handler $RODEOS_EVENT_HANDLER \
            $i $TARGET/$YEAR/$DIR
        sleep 10
    done


else
    envsubst < /root/.irods/irods_environment.json.tmpl > /root/.irods/irods_environment.json
    echo $IRODS_PASS | iinit
    if [ $? -ne 0 ]; then
        echo "iinit failed"
    fi

    exec "$@"
fi
