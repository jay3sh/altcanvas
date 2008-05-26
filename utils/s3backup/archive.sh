#!/bin/bash

PROJECT=$1
BACKUP_SRC=$2

LOG_FILE="$PROJECT.log"


if [ -f $LOG_FILE ]
then
    TIMESTAMP="-newer $LOG_FILE"
fi

find $BACKUP_SRC $TIMESTAMP | \
    grep '\.py$\|\.c$\|\.ac$\|\.am$\|\.h$\|\.cpp\|\.hpp\|\.sh$' | xargs echo 

date >> $LOG_FILE
