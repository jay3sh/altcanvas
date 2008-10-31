#!/bin/bash

export LD_LIBRARY_PATH=$HOME/usr/lib 
export PYTHONPATH=`pwd`/src/bindings/python 
export DATADIR=`pwd`/tests/data


valgrind_memcheck()
{
    valgrind \
        --log-file=$1.valgrind \
        --tool=memcheck \
        --leak-check=full \
        --show-reachable=yes \
        $*
}

valgrind_helgrind()
{
    valgrind \
        -v \
        --log-file=$1.valgrind \
        --tool=helgrind \
        --happens-before=all \
        $*
}

GDB=cgdb
VALGRIND=valgrind_memcheck

VERBOSITY=0

execute()
{

    if [ "x$MEMDEBUG" != "x" ]
    then
        WRAPPER=$VALGRIND       
    fi

    if [ "x$1" == "x" ]
    then
        $WRAPPER python
        
    elif [ "x$1" == "xall" ]
    then
        for test in basic visual keyboard irc
        do
            $WRAPPER python tests/inkface-$test.py $DATADIR/$test.svg
        done
    else
        $WRAPPER python tests/inkface-$1.py $DATADIR/$1.svg
    fi

}


usage()
{
    echo "runtests.sh -t <testname> [options]"
    echo "<testname> all,basic,visual,keyboard,anim"
    echo "Options:"
    echo "   -v <verbosity level> 0,1,2,3"
    echo "   -d Start python with gdb"
    echo "   -m Run test inside valgrind (output generated in python.valgrind)"
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

if [ "x$DEBUG" != "x" ]
then
    $GDB python
    exit 0;
fi


execute $TEST

