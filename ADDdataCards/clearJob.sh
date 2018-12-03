#!/bin/bash

for j in `seq 2400 100 3200`
do
	cd ./ee_limit_min$j

	for i in `seq 4000 1000 10000`
	do
		hadd higgsCombine$i.MarkovChainMC.mH$i.root higgsCombineTest.MarkovChainMC.mH$i.*.root
		rm higgsCombineTest.MarkovChainMC.mH$i.*.root
	done

	rm log.log
	cd ..

done
