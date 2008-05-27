#!/bin/bash

PROJECT=$1
BACKUP_SRC=$2

BASE_DIR="$HOME/.S3backup"
LOG_FILE="$BASE_DIR.$PROJECT.log"


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
    rm -f $ARCHIVE
    date >> $LOG_FILE
fi


