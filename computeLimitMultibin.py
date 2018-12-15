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
withBinError = True

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

multibintemplate = """# Simple counting experiment, with one signal and one background
imax %d  number of channels
jmax 1  number of backgrounds
kmax %d  number of nuisance parameters (sources of systematical uncertainties)
------------
# we have %d channels, in which we observe 0 events
"""


def getBinError(x):
	return 1.09514 - 0.00000697156*x + 0.00000000932386*x*x


from readData import getMassDistroDY, getMassDistro

def templateFormat(sigYieldList, dyYieldList, Mbins):
	
	nbin = len(sigYieldList)
	numErr = 1
	if withBinError: numErr = 2
	curr = multibintemplate%(nbin, numErr, nbin)

	nameline = "%8s "%("bin")
	obsline = "%8s "%("observation")
	for i in range(nbin): 
		nameline = nameline + " bin%d"%i
		obsline = obsline + " -1"
	curr = curr + nameline + "\n"
	curr = curr + obsline + "\n--------------- \n"

	binline = "%8s \t"%("bin")
	pro1line = "%8s \t"%("process") # for pro name
	pro2line = "%8s \t"%("process") # for pro number
	rateline = "%8s \t"%("rate") 	# for rate
	for i in range(nbin):
		binline = binline + " bin%d"%i + " bin%d"%i + "\t"
		pro1line = pro1line + " sig  bkg" + "\t"
		pro2line = pro2line + " 0    1  " + "\t"
		rateline = rateline + " %f   %f "%(sigYieldList[i]-dyYieldList[i], dyYieldList[i]) + "\t"
	curr = curr + binline + "\n"
	curr = curr + pro1line + "\n"
	curr = curr + pro2line + "\n"
	curr = curr + rateline + "\n"
	
	curr = curr + "------------ \n"
	lumiline = "%8s \t %8s \t"%("lumi", "lnN")
	for i in range(nbin):
		lumiline = lumiline + " 1.025   - \t"
	curr = curr + lumiline + "\n"

	if withBinError:
		binline = "%8s \t %8s \t"%("binerr", "lnN")
		for i in range(nbin):
			thisbe = getBinError((Mbins[i]+Mbins[i+1])*0.5)
			binline = binline + " %f \t %f \t"%(thisbe, thisbe)
		curr = curr + binline + "\n"

	return curr


# write datacards based on
# sigYield = ADD - DY
# dyYield = DY event yield only
def writeDatacard(model, sigYield, dyYield, lambdaT, helicity, Mbins):
	
	outDir = "%sdataCards/ee_limit_multibin%s/"%(model, helicity)
	if not os.path.exists(outDir):
                os.makedirs(outDir)

	fname = outDir + "dataCard_ee_lambda%d_multibin.txt"%lambdaT
	fout = open(fname, "w")
	fout.write(templateFormat(sigYield, dyYield, Mbins))
	fout.close()
	return fname


# execute datacards
# and move them to /dataCards
def executeDatacard(model, fname, lambdaT, label):

	# AsymptoticLimit calculation
	combine_command = "combine -M AsymptoticLimits %s -m %d"%(fname, lambdaT)
	print ">>> command: " + combine_command

	p = subprocess.Popen(combine_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		print line.rstrip("\n")
	print ">>> higgsCombine rootfile created"
	retval = p.wait()

	rf = "higgsCombineTest.AsymptoticLimits.mH%d.root"%(lambdaT)
	mvfile = subprocess.Popen("mv ./%s ./%sdataCards/ee_limit_multibin%s/%s"%(rf, model, label, rf), shell=True)
	print ">>> file moved"
	retval = p.wait()



# plot invariant mass spectrum for a single lambdaT
# write datacards, and execute datacards
def main(argv):

	# read in parameters
	# first try of setting bin edges, Mmin = 1800
	#Mbins = [1800, 2200, 2600, 3000, 10000] # in paper, bw400
	#Mbins = [1800, 1900, 2100, 2500, 3300, 4900, 10000] # geometric
	#Mbins = [1800, 2800, 3800, 4800, 10000] # bw1000
	#Mbins = [1800 + i * 100 for i in range(31)]; Mbins.append(10000) # bw100
        #Mbins = [1800 + i * 200 for i in range(16)]; Mbins.append(10000) # bw200

	model = argv[0]
	#Mbins = [1200, 1300, 1500, 1900, 2700, 4300, 10000]
	#Mbins = [1200, 2200, 3200, 4200, 10000]
	#Mbins = [1200, 1700, 2200, 2700, 3200, 3700, 4200, 10000]
	#Mbins = [1200 + i * 200 for i in range(16)]; Mbins.append(10000)
	Mbins = [1200 + i * 100 for i in range(31)]; Mbins.append(10000)

	if model == "ADD": 
		lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
		# heli = ["_Con", "_Des"]
		heli = [""]
	else: 
		lambdas = [16, 22, 28, 32, 40]
		#heli = ["_ConLL", "_ConLR", "_ConRR", "_DesLL", "_DesLR", "_DesRR"]
		heli = ["_ConLL", "_ConLR", "_ConRR"]

	# read raw data histograms
	# and DY histograms
	sigHists = []  # sigHists[lambdaT][helicity]
	for lambdaT in lambdas:
		sigHists.append(getMassDistro(model, heli, lambdaT, isMuon))
	dyHist = getMassDistroDY(isMuon)

	# read event yield from mass spectrum
	# above a minimum mass Mmin
	# Mmin = argv[0]
	dyNum = np.zeros((len(lambdas), len(Mbins)-1))     	# DY yield
	hhNum = np.zeros((len(lambdas), len(heli), len(Mbins)-1)) # hhNum[lambdaT][helicity][Mbin]
	#for i in range(len(lambdas)): 
	#	hhNum.append([0]*len(heli)) 

	Mmax = 10000
	for i in range(len(lambdas)):
		if model == "ADD": 
			Mmax = lambdas[i]
		for m in range(len(Mbins)-1):
			#if Mbins[m] > Mmax: continue
			dyNum[i][m] = dyHist.Integral(dyHist.FindBin(Mbins[m]), dyHist.FindBin(Mbins[m+1]))
		for j in range(len(heli)):
			for m in range(len(Mbins)-1):
				if Mbins[m] > Mmax: continue
				hhNum[i][j][m] = sigHists[i][j].Integral(sigHists[i][j].FindBin(Mbins[m]),
					min(sigHists[i][j].FindBin(Mbins[m+1]), sigHists[i][j].FindBin(Mmax)))
		#dyNum[i] = dyHist.Integral(dyHist.FindBin(Mmin), dyHist.FindBin(Mmax))
		#for j in range(len(heli)):
		#	hhNum[i][j] = sigHists[i][j].Integral(sigHists[i][j].FindBin(Mmin), sigHists[i][j].FindBin(Mmax))

	# print information
	# and execute datacards
	print "-----------------------------------"
	print ">>> Check data values "
	for i in range(len(lambdas)):
		print ">>> Bin edges, DY yield"
		print Mbins
		print dyNum[i]
		print ">>> %s model lambda %d event yield:"%(model, lambdas[i])
		for j in range(len(heli)):
			print hhNum[i][j]
	print "-----------------------------------"
	
	for i in range(len(lambdas)):
		for j in range(len(heli)):
			fout = writeDatacard(model, hhNum[i][j], dyNum[i], lambdas[i], heli[j], Mbins)
			executeDatacard(model, fout, lambdas[i], heli[j])
	print ">>> Done!"


# MAIN
if __name__ == "__main__":
	main(sys.argv[1:])
