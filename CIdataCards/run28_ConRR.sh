#!/bin/bash

for j in `seq 400 100 3200`
do
	cd "./ee_limit_min"$j"_ConRR"

	for i in `seq 1 1 100`
	do
	        combine -M MarkovChainMC -m 28 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda28_singlebin.txt
        	echo ">>>> Finished computing CI MCMC with Lambda = $i"
	done
	
	hadd higgsCombine28.MarkovChainMC.mH28.root higgsCombineTest.MarkovChainMC.mH28.*.root
	rm -f higgsCombineTest.MarkovChainMC.mH28.*.root
	cd ..

done
