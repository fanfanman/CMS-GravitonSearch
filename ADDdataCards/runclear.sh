#!/bin/bash

for j in `seq 400 100 3200`
do
	cd ./ee_limit_min$j
	rm higgsCombine*.MarkovChainMC.*.root
	cd ..

done
