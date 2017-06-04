#!/bin/bash

#clean up mininet
sudo mn -c

hosts=28
runtime=240
savedir="outputs/"
declare -a traffic=("data" "web")
#declare -a cong=("tcp" "mintcp" "none")
declare -a cong=("tcp" "mintcp")
declare -a load=("0.1" "0.2" "0.3" "0.4" "0.5" "0.6" "0.7" "0.8")

sudo rm -rf $savedir

for t in "${traffic[@]}"
do
    for c in "${cong[@]}"
    do
        for l in "${load[@]}"
    	do
        	sudo python pfabric.py -o $savedir -c $c -t $t -n $hosts --time $runtime --load $l
        	sudo mn -c > /dev/null 2>&1
    		sleep 10s
        done
    done
done

sudo python plots.py -o $savedir
