#!/bin/bash

for i in `seq 400 100 3200`
do
	python computeLimit.py CI $i
	echo ">>>> Finished computing ADD with Lambda = $i"
done
