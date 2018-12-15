#!/bin/bash

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 5000 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda5000_multibin.txt
       	echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 6000 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda6000_multibin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 7000 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda7000_multibin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 8000 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda8000_multibin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 9000 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda9000_multibin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 100`
do
        combine -M MarkovChainMC -m 10000 -t 1 -i 30000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda10000_multibin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

