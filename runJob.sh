#!/bin/bash

for i in `seq 200 100 1200`
do
	python computeLimit.py CI $i
	echo ">>>> Finished computing ADD with Lambda = $i"
done
