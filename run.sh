#!/bin/bash

#clean up mininet
sudo mn -c

hosts=15
runtime=180
declare -a traffic=("web" "data")
declare -a cong=("tcp" "mintcp" "none")

for t in "${traffic[@]}"
do
    # sudo rm -rf [oldsavefiles]

    for c in "${cong[@]}"
    do
        sudo python pfabric.py -c $c -t $t -n $hosts --time $runtime
    done


done
