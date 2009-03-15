
#
# A regression script that runs all tests in order.
#

#!/bin/bash

DATA_DIR=../data

export PYTHONPATH=$HOME/altcanvas/inkface-pygame

python basic.py $DATA_DIR/gui-0.svg

python events.py $DATA_DIR/gui-0.svg

python change.py $DATA_DIR/gui-4.svg

#python clone.py $DATA_DIR/gui-5.svg

#python animation.py $DATA_DIR/gui-1.svg

#printf "Enter twitter credentials:\n"
#printf "Username: "
#read TWT_UNAME
#printf "Password: "
#read TWT_PASSWD
#export TWT_USERNAME=$TWT_UNAME
#export TWT_PASSWORD=$TWT_PASSWD

#python twt.py $DATA_DIR/gui-6.svg
#python twt.py $DATA_DIR/gui-7.svg
#python twt.py $DATA_DIR/gui-8.svg

#python magnify.py $DATA_DIR/gui-10.svg

#python keyboard.py $DATA_DIR/gui-11.svg
#python keyboard.py $DATA_DIR/gui-12.svg
#python keyboard.py $DATA_DIR/gui-13.svg

#python textbox.py $DATA_DIR/gui-14.svg

#python hide.py $DATA_DIR/gui-15.svg
