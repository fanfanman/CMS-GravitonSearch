#!/bin/bash

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 16 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda16_multibin.txt
       	echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

hadd higgsCombine16.MarkovChainMC.mH16.root higgsCombineTest.MarkovChainMC.mH16.*.root
rm -f higgsCombineTest.MarkovChainMC.mH16.*.root

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 22 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda22_multibin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

hadd higgsCombine22.MarkovChainMC.mH22.root higgsCombineTest.MarkovChainMC.mH22.*.root
rm -f higgsCombineTest.MarkovChainMC.mH22.*.root

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 28 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda28_multibin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

hadd higgsCombine28.MarkovChainMC.mH28.root higgsCombineTest.MarkovChainMC.mH28.*.root
rm -f higgsCombineTest.MarkovChainMC.mH28.*.root

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 32 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda32_multibin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

hadd higgsCombine32.MarkovChainMC.mH32.root higgsCombineTest.MarkovChainMC.mH32.*.root
rm -f higgsCombineTest.MarkovChainMC.mH32.*.root

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 40 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda40_multibin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

hadd higgsCombine40.MarkovChainMC.mH40.root higgsCombineTest.MarkovChainMC.mH40.*.root
rm -f higgsCombineTest.MarkovChainMC.mH40.*.root

