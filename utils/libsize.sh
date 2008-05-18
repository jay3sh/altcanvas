#!/bin/bash

SUM_STR='0'
LIBRARIES=`ldd $1 | awk '{printf $3 "\n"}' | grep "^/"` 
for i in $LIBRARIES
do 
    SUM_STR=$SUM_STR+`ls -lL $i | awk '{printf $5}'`
done

echo $SUM_STR
