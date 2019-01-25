#!/bin/bash

for j in `seq 600 100 3200`
do
	cd ./ee_limit_min$j
	for i in `seq 1 1 100`
	do
	        combine -M MarkovChainMC -m 6000 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda6000_singlebin.txt
        	echo ">>>> Finished computing CI MCMC with Lambda = $i"
	done
	
	hadd higgsCombine6000.MarkovChainMC.mH6000.root higgsCombineTest.MarkovChainMC.mH6000.*.root
	rm -f higgsCombineTest.MarkovChainMC.mH6000.*.root
	cd ..

done
