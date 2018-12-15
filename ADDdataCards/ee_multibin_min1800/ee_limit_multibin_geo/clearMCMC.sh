#!/bin/bash

for i in `seq 5000 1000 10000`
do
        hadd higgsCombine$i.MarkovChainMC.mH$i.root higgsCombineTest.MarkovChainMC.mH$i.*.root
	rm -f higgsCombineTest.MarkovChainMC.mH$i.*.root
done
