#!/bin/bash

for i in `seq 1 1 50`
do
	combine -M MarkovChainMC -m 10000 -t 1 -i 20000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda10000_multibin.txt
	echo ">>>> Finished computing CI MCMC with Lambda = $i"
done
