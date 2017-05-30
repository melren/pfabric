#!/bin/bash

#clean up mininet
sudo mn -c

hosts=15
runtime=60
savedir="/outputs"
declare -a traffic=("web" "data")
declare -a cong=("tcp" "mintcp" "none")

sudo rm -rf $savedir

for t in "${traffic[@]}"
do

    for c in "${cong[@]}"
    do
        sudo python pfabric.py -o $savedir -c $c -t $t -n $hosts --time $runtime
    done
done

sudo python plots.py -o $savedir
