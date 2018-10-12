#!/bin/bash

for l in `seq 4000 1000 10000`
do 
  echo ">>> Lambda = $l"
  
  for m in `seq 1200 100 3600`
  do
    echo ">>>> Mmin = $m"
    mname="dataCard_ee_lambda"$l"_singlebin_Mmin"$m".txt"
    combine -M Significance $mname -t 1500 -m $l -n $m
    echo $mname
  done

done
