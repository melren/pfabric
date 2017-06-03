#!/bin/bash

#clean up mininet
sudo mn -c

hosts=28
runtime=240
savedir="outputs/"
declare -a traffic=("data" "web")
#declare -a cong=("tcp" "mintcp" "none")
declare -a cong=("tcp" "mintcp")

sudo rm -rf $savedir

for t in "${traffic[@]}"
do
    for c in "${cong[@]}"
    do
        sudo python pfabric.py -o $savedir -c $c -t $t -n $hosts --time $runtime
    done
    if [ $t = "data" ]; then
        echo Pausing for 1min before next run to free up CPU
        sleep 1m
    fi
done

sudo python plots.py -o $savedir
