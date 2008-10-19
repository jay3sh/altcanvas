export LD_LIBRARY_PATH=$HOME/usr/lib 
export PYTHONPATH=`pwd`/src 
export DATADIR=`pwd`/tests/data

#if [ "x$1" == "x--valgrind" ]
#then
#    valgrind-wrapper python tests/inkface-basic.py $DATADIR
#else
#    python tests/inkface-basic.py $DATADIR
#fi

#export INKFACE_FULLSCREEN=TRUE

#python tests/inkface-basic.py $DATADIR
#python tests/inkface-visual.py $DATADIR
#python tests/inkface-keyboard.py $DATADIR/keyboard-entry.svg
python tests/inkface-irc.py tests/data/irc.svg
