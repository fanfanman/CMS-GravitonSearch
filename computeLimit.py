from ROOT import * 
from setTDRStyle import setTDRStyle
from copy import deepcopy

import sys, os
import ratios
import subprocess
rand = TRandom3()

## Initialization
isMuon = False
resolution = True

## template for dataCards
template = """
# Simple counting experiment, with one signal and one background
imax 1  number of channels
jmax 1  number of backgrounds
kmax 1  number of nuisance parameters (sources of systematical uncertainties)
------------
# we have just one channel, in which we observe 0 events
bin bin1
observation -1
------------
# now we list the expected events for signal and all backgrounds in that bin
# the second 'process' line must have a positive number for backgrounds, and 0 for signal
# then we list the independent sources of uncertainties, and give their effect (syst. error)
# on each process and bin
bin             bin1 bin1
process         ADD  DY
process          0     1 
rate            %f   %f
------------
lumi    lnN    1.025    -
"""

from readData import getMassHisto, getMassDistroSignal, getMassDistroDY

# write datacards based on
# sigYield = ADD - DY
# dyYield = DY event yield only
def writeDatacard(sigYield, dyYield, lambdaT, Mmin, label):
	
	outDir = "dataCards/ee_limit_min%d_%s/"%(Mmin, label)
	if not os.path.exists(outDir):
                os.makedirs(outDir)

	fname = outDir + "dataCard_ee_lambda%d_singlebin.txt"%lambdaT
	fout = open(fname, "w")
	fout.write(template%(sigYield-dyYield, dyYield))
	fout.close()
	return fname


# execute datacards
# and move them to /dataCards
def executeDatacard(fname, lambdaT, Mmin, label):

	combine_command = "combine -M AsymptoticLimits %s -m %d"%(fname, lambdaT)
	print ">>> command: " + combine_command

	p = subprocess.Popen(combine_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		print line.rstrip("\n")
	print ">>> higgsCombine rootfile created"
	retval = p.wait()

	rf = "higgsCombineTest.AsymptoticLimits.mH%d.root"%(lambdaT)
	mvfile = subprocess.Popen("mv ./%s ./dataCards/ee_limit_min%d_%s/%s"%(rf, Mmin, label, rf), shell=True)
	print ">>> file moved"
	retval = p.wait()


# plot invariant mass spectrum for a single lambdaT
# write datacards, and execute datacards
def main():

	lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
	# lambdas = [4000]
	sigCon = []
	sigDes = []

	# read in histograms
	# and scale by (1/binwidth)	
	for lambdaT in lambdas:
		signalCon = getMassDistroSignal(str(lambdaT), lambdaT, isMuon, True)
		signalDes = getMassDistroSignal(str(lambdaT), lambdaT, isMuon, False)
		sigCon.append(signalCon)
		sigDes.append(signalDes)
		print ">>> Finished reading lambda = %d"%lambdaT
	dyHist = getMassDistroDY(isMuon)

	# read event yield from mass spectrum
	# above a minimum mass Mmin
	Mmin = 3200
	dyNum = [0]*len(lambdas)     # DY yield
	conNum = [0]*len(lambdas)    # signal yields for lambdas
	desNum = [0]*len(lambdas)    # interference term
	for i in range(len(lambdas)):
		dyNum[i] = dyHist.Integral(dyHist.FindBin(Mmin), dyHist.FindBin(lambdas[i]))
		conNum[i] = sigCon[i].Integral(sigCon[i].FindBin(Mmin), sigCon[i].FindBin(lambdas[i]))
		desNum[i] = sigDes[i].Integral(sigDes[i].FindBin(Mmin), sigDes[i].FindBin(lambdas[i]))

	# print information
	# and execute datacards
	print "-----------------------------------"
	print ">>> Min mass cut: %f GeV"%Mmin
	for i in range(len(lambdas)):
		print ">>> DY event yield: %f"%dyNum[i]
		print ">>> Signal lambda %d event yield: %f and %f"%(lambdas[i], conNum[i], desNum[i])
	print "-----------------------------------"
	
	for i in range(len(lambdas)):
		fcon = writeDatacard(conNum[i], dyNum[i], lambdas[i], Mmin, "Con")
		fdes = writeDatacard(desNum[i], dyNum[i], lambdas[i], Mmin, "Des")
		executeDatacard(fcon, lambdas[i], Mmin, "Con")
		executeDatacard(fdes, lambdas[i], Mmin, "Des")
	print ">>> Done!"


# MAIN
if __name__ == "__main__":
	main()
