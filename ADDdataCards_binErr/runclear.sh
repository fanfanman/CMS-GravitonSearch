#!/bin/bash

for j in `seq 400 100 3200`
do
	cd ./ee_limit_min$j
	mv higgsCombine6000.MarkovChainMC.mH8000.root higgsCombine8000.MarkovChainMC.mH8000.root
	cd ..

done
