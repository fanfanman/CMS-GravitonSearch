from ROOT import * 
from setTDRStyle import setTDRStyle
from copy import deepcopy

import sys, os
import ratios
import subprocess
import numpy as np
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

from readData import getMassDistroDY, getMassDistro

# write datacards based on
# sigYield = ADD - DY
# dyYield = DY event yield only
def writeDatacard(model, sigYield, dyYield, lambdaT, Mmin, label):
	
	outDir = "%sdataCards/ee_signif%s/"%(model, label)
	if not os.path.exists(outDir):
                os.makedirs(outDir)

	fname = outDir + "dataCard_ee_lambda%d_Mmin%d.txt"%(lambdaT, Mmin)
	fout = open(fname, "w")
	fout.write(template%(sigYield-dyYield, dyYield))
	fout.close()
	return fname


# execute datacards
# and move them to /dataCards
def executeDatacard(model, fname, lambdaT, Mmin, label):

	combine_command = "combine -M Significance %s -t -1 -m %d -n %d --expectSignal=1"%(fname, lambdaT, Mmin)
	print ">>> command: " + combine_command

	p = subprocess.Popen(combine_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		print line.rstrip("\n")
	print ">>> higgsCombine rootfile created"
	retval = p.wait()

	rf = "higgsCombine%d.Significance.mH%d.root"%(Mmin, lambdaT)
	mvfile = subprocess.Popen("mv ./%s ./%sdataCards/ee_signif%s/%s"%(rf, model, label, rf), shell=True)
	print ">>> file moved"
	retval = p.wait()


# plot invariant mass spectrum for a single lambdaT
# write datacards, and execute datacards
def main(argv):

	# read in parameters
	model = argv[0]
	# Mmin = float(argv[1])
	
	if model == "ADD": 
		lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
		#heli = ["_Con", "_Des"]
		heli = [""]
	else: 
		lambdas = [16, 22, 28, 32, 40]
		heli = ["_ConLL", "_ConLR", "_ConRR", "_DesLL", "_DesLR", "_DesRR"]

	# read raw data histograms
	# and DY histograms
	sigHists = []  # sigHists[lambdaT][helicity]
	for lambdaT in lambdas:
		sigHists.append(getMassDistro(model, heli, lambdaT, isMuon))
	dyHist = getMassDistroDY(isMuon)

	# read event yield from mass spectrum
	# above a minimum mass Mmin
	# Mmin = argv[0]
	#dyNum = [0]*len(lambdas)     # DY yield
	#hhNum = []		     # hhNum[lambdaT][helicity]
	#Mmins = [1200 + i * 100 for i in range(21)]
	Mmins = [100 + i * 100 for i in range(40)]
	dyNum = np.zeros((len(Mmins), len(lambdas)))
	hhNum = np.zeros((len(Mmins), len(lambdas), len(heli)))
	#for i in range(len(lambdas)): 
	#	hhNum.append([0]*len(heli)) 
	
	Mmax = 10000
	for m in range(len(Mmins)):
		for i in range(len(lambdas)):
			if model == "ADD": Mmax = lambdas[i]
			dyNum[m][i] = dyHist.Integral(dyHist.FindBin(Mmins[m]), dyHist.FindBin(Mmax))
			for j in range(len(heli)):
				hhNum[m][i][j] = sigHists[i][j].Integral(sigHists[i][j].FindBin(Mmins[m]), sigHists[i][j].FindBin(Mmax))

	# print information
	# and execute datacards
	for m in range(len(Mmins)):
		print "-----------------------------------"
		print ">>> Min mass cut: %f GeV"%Mmins[m]
		for i in range(len(lambdas)):
			print ">>> DY event yield: %f"%dyNum[m][i]
			print ">>> %s model lambda %d event yield:"%(model, lambdas[i])
			print hhNum[m][i]
		print "-----------------------------------"
	
	for m in range(len(Mmins)):
		for i in range(len(lambdas)):
			for j in range(len(heli)):
				fout = writeDatacard(model, hhNum[m][i][j], dyNum[m][i], lambdas[i], Mmins[m], heli[j])
				executeDatacard(model, fout, lambdas[i], Mmins[m], heli[j])
	print ">>> Done!"


# MAIN
if __name__ == "__main__":
	main(sys.argv[1:])
