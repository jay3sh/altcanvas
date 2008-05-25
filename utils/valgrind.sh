#!/bin/bash

mkdir -p valgrind

valgrind \
    --tool=memcheck \
    --leak-check=full \
    --show-reachable=yes \
    --log-file=valgrind/$$.log \
    $*
