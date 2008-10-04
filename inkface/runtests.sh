export LD_LIBRARY_PATH=$HOME/usr/lib 
export PYTHONPATH=`pwd`/src 
export DATADIR=`pwd`/tests/data

python tests/inkface-basic.py $DATADIR
