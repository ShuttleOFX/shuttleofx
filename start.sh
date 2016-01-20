#!/bin/bash

export LOG_BASE_DIR=/var/log/shuttleofx
export DATE_NAME=`date "+%F_%T"`

# echo "DEV MODE"
# export DATE_NAME=
# (cd ${SHUTTLEOFX_DEV}/shuttleofx_client && grunt build)

export LOG_DIR=$LOG_BASE_DIR/$DATE_NAME
mkdir -p $LOG_DIR

echo "Starting mongodb"
(/opt/mongodb/bin/mongod --dbpath /opt/mongo-data > $LOG_DIR/mongo.log 2>&1) &

echo "Starting Analyzer"
(python ${SHUTTLEOFX_DEV}/shuttleofx_analyser/views.py > $LOG_DIR/analyser.log 2>&1) &
echo "Starting Render"
(python ${SHUTTLEOFX_DEV}/shuttleofx_render/views.py > $LOG_DIR/render.log 2>&1) &
echo "Starting Catalog"
(python ${SHUTTLEOFX_DEV}/shuttleofx_catalog/views.py > $LOG_DIR/catalog.log 2>&1) &
echo "Starting Client"
(python ${SHUTTLEOFX_DEV}/shuttleofx_client/views.py > $LOG_DIR/client.log 2>&1) &
echo "END"

wait

