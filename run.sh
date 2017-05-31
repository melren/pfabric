#!/bin/bash

#clean up mininet
sudo mn -c

hosts=54
runtime=180
savedir="outputs/"
declare -a traffic=("data" "web")
#declare -a traffic=("web")
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
