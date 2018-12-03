#!/bin/bash

for i in `seq 1 1 50`
do
	combine -M MarkovChainMC -m 4000 -t 1 -i 20000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda4000_singlebin.txt
	echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 50`
do
        combine -M MarkovChainMC -m 5000 -t 1 -i 20000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda5000_singlebin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 50`
do
        combine -M MarkovChainMC -m 6000 -t 1 -i 20000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda6000_singlebin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 50`
do
        combine -M MarkovChainMC -m 7000 -t 1 -i 20000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda7000_singlebin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 50`
do
        combine -M MarkovChainMC -m 8000 -t 1 -i 20000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda8000_singlebin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 50`
do
        combine -M MarkovChainMC -m 9000 -t 1 -i 20000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda9000_singlebin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

for i in `seq 1 1 50`
do
        combine -M MarkovChainMC -m 10000 -t 1 -i 20000 --tries 100 --noDefaultPrior=0 -s -1 dataCard_ee_lambda10000_singlebin.txt
        echo ">>>> Finished computing CI MCMC with Lambda = $i"
done

