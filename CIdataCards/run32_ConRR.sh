#!/bin/bash

for j in `seq 400 100 3200`
do
	cd "./ee_limit_min"$j"_ConRR"

	for i in `seq 1 1 100`
	do
	        combine -M MarkovChainMC -m 32 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda32_singlebin.txt
        	echo ">>>> Finished computing CI MCMC with Lambda = $i"
	done
	
	hadd higgsCombine32.MarkovChainMC.mH32.root higgsCombineTest.MarkovChainMC.mH32.*.root
	rm -f higgsCombineTest.MarkovChainMC.mH32.*.root
	cd ..

done
