#!/bin/bash

for j in `seq 400 100 3200`
do
	cd "./ee_limit_min"$j"_ConLL"

	for i in `seq 1 1 100`
	do
	        combine -M MarkovChainMC -m 22 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda22_singlebin.txt
        	echo ">>>> Finished computing CI MCMC with Lambda = $i"
	done
	
	hadd higgsCombine22.MarkovChainMC.mH22.root higgsCombineTest.MarkovChainMC.mH22.*.root
	rm -f higgsCombineTest.MarkovChainMC.mH22.*.root
	cd ..

done
