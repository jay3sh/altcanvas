
#
# A regression script that runs all tests in order.
#

#!/bin/bash

export PYTHONPATH=$HOME/altcanvas/inkface-pygame

python basic.py data/gui-0.svg

python events.py data/gui-1.svg

python change.py

python clone.py

python animation.py

printf "Enter twitter credentials:\n"
printf "Username: "
read TWT_UNAME
printf "Password: "
read TWT_PASSWD
export TWT_USERNAME=$TWT_UNAME
export TWT_PASSWORD=$TWT_PASSWD

python twt.py data/gui-6.svg
python twt.py data/gui-7.svg
python twt.py data/gui-8.svg

python magnify.py
