#!/bin/bash

for j in `seq 400 100 3200`
do
	cd ./ee_limit_min$j
	for i in `seq 1 1 50`
	do
	        combine -M MarkovChainMC -m 10000 -t 1 -i 20000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda10000_singlebin.txt
        	echo ">>>> Finished computing CI MCMC with Lambda = $i"
	done
	
	hadd higgsCombine10000.MarkovChainMC.mH10000.root higgsCombineTest.MarkovChainMC.mH10000.*.root
	rm -f higgsCombineTest.MarkovChainMC.mH10000.*.root
	cd ..

done
