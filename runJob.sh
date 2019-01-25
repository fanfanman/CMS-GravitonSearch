#!/bin/bash

for i in `seq 400 100 3200`
do
	python computeShapeLimit.py ADD $i
	echo ">>>> Finished computing ADD with Lambda = $i"
done
