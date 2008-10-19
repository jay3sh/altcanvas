#!/bin/bash

GDB=cgdb
VALGRIND=valgrind-wrapper

VERBOSITY=0

execute()
{

    export LD_LIBRARY_PATH=$HOME/usr/lib 
    export PYTHONPATH=`pwd`/src 
    export DATADIR=`pwd`/tests/data

    if [ "x$DEBUG" != "x" ]
    then
        $GDB python
    fi

    if [ "x$MEMDEBUG" != "x" ]
    then
        WRAPPER=$VALGRIND       
    fi


    if [ "x$1" == "xall" ]
    then
        for tfile in `ls tests/inkface-*.py`
        do
            $WRAPPER $tfile $DATADIR
        done
    else
        $WRAPPER python tests/inkface-$1.py $DATADIR/$1.svg
    fi

}


usage()
{
    echo "runtests.sh [options]"
    echo "Options:"
    echo "   t <testname> all,basic,visual"
    echo "   v <verbosity level> 0,1,2,3"
    echo "   d Start python with gdb"
    echo "   m Start python in valgrind"
}

while getopts "t:v:dmh" options; do
    case $options in
        t) TEST=$OPTARG;;
        v) VERBOSITY=$OPTARG;;
        d) DEBUG=1;;
        m) MEMDEBUG=1;;
        h) usage;
           exit 0;;
        *) usage;
           exit 0;;
    esac
done

if [ "x$DEBUG" != "x" ] && [ "x$MEMDEBUG" != "x" ]
then
    echo "GDB and Valgrind can't be used together"
    exit 1;
fi

execute $TEST

