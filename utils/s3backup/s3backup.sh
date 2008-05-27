#!/bin/bash

PROJECT=$1
BACKUP_SRC=$2

BASE_DIR="$HOME/.S3backup"
LOG_FILE="$BASE_DIR.$PROJECT.log"


if [ -f $LOG_FILE ]
then
    MAX_INCR_BACKUPS=10
    TOTAL_BACKUPS=`cat $LOG_FILE | wc -l`
    if [ $TOTAL_BACKUPS -gt $MAX_INCR_BACKUPS ]
    then
        # Time for full backup
        rm -f $LOG_FILE
    fi
fi

if [ -f $LOG_FILE ]
then
    TIMESTAMP="-newer $LOG_FILE"
fi

TS=`date +%F%T | sed 's/[^0-9]//g'`

ARCHIVE=/tmp/$PROJECT.$TS.tgz

FILE_LIST=`find $BACKUP_SRC $TIMESTAMP | \
    grep '\.py$\|\.c$\|\.ac$\|\.am$\|\.h$\|\.cpp\|\.hpp\|\.sh$'`

if [ "x$FILE_LIST" != "x" ]
then
    tar czf $ARCHIVE $FILE_LIST
    AmazonS3.py --bucket $PROJECT --save $ARCHIVE 
    ARCHIVE_SIZE=`ls -lh $ARCHIVE | awk '{printf $5 "\n"}'`
    ARCHIVE_TIME=`date`
    echo "$ARCHIVE - $ARCHIVE_SIZE - $ARCHIVE_TIME" >> $LOG_FILE
    rm -f $ARCHIVE
fi


