#!/bin/bash

for i in `seq 1300 100 3200`
do
	python computeLimit.py ADD $i
	echo ">>>> Finished computing ADD with Lambda = $i"
done
