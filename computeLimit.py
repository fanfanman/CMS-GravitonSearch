from ROOT import * 
from numpy import array as ar
from array import array
from setTDRStyle import setTDRStyle
from copy import deepcopy

import sys
import ratios
import subprocess
rand = TRandom3()


## Initialization
muon = False
resolution = True
if muon:
	from muonResolution import getResolution
else:
	from electronResolution import getResolution


## efficiency map
weightHistMu = TFile("rootfiles/effMapMuons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
weightHistEle = TFile("rootfiles/effMapElectrons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")


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


# get invariant mass spectrum
def getMassHisto(fileName):
	f = TFile(fileName,"OPEN")

	from ROOT import TChain
	tree = TChain()
	tree.Add(fileName+"/pdfTree")	

	xsecTree = TChain()
	xsecTree.Add(fileName+"/crossSecTree")
	for entry in xsecTree:
		xsec = entry.crossSec
	result = TH1F("h_%s"%fileName,"h_%s"%fileName,240,0,12000)

	for ev in tree:
		mass = tree.GetLeaf("bosonP4/mass").GetValue()
		weight = 1.
		if resolution:
			eta1 = tree.GetLeaf("decay1P4/eta").GetValue()
			eta2 = tree.GetLeaf("decay2P4/eta").GetValue()
			pt1 = tree.GetLeaf("decay1P4/pt").GetValue()
			pt2 = tree.GetLeaf("decay2P4/pt").GetValue()
			BB = False
			if muon:
				if abs(eta1) > 2.4 or abs(eta2) > 2.4: continue
				weight = weightHistMu.GetBinContent(weightHistMu.GetXaxis().FindBin(abs(eta1)),
								    weightHistMu.GetYaxis().FindBin(pt1)
				) * weightHistMu.GetBinContent(	    weightHistMu.GetXaxis().FindBin(abs(eta2)),
								    weightHistMu.GetYaxis().FindBin(pt2))
				if abs(eta1) < 1.2 and abs(eta2) < 1.2:
					BB = True
			else:
				if abs(eta2) > 2.5 or abs(eta2) > 2.5: continue
				#~ print pt2
				#~ print weightHistEle.GetYaxis().FindBin(pt2)
				weight = weightHistEle.GetBinContent(weightHistEle.GetXaxis().FindBin(abs(eta1)),
								     weightHistEle.GetYaxis().FindBin(pt1)
				) * weightHistEle.GetBinContent(     weightHistEle.GetXaxis().FindBin(abs(eta2)),
								     weightHistEle.GetYaxis().FindBin(pt2))				
				#~ print weight
				if abs(eta1) < 1.4442 and abs(eta2) < 1.4442:
					BB = True
			if BB:						
				mass = mass*rand.Gaus(1,getResolution(mass)["sigma"]["BB"])
			else:
				mass = mass*rand.Gaus(1,getResolution(mass)["sigma"]["BE"])		
		result.Fill(mass,weight)
	result.Sumw2()
	result.Scale(36300*xsec/100000)
	return deepcopy(result)


# get mass distribution of ADD files
def getMassDistroSignal(name, mass):
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
		    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
	
	result = TH1F("h_%s"%name,"h_%s"%name,240,0,12000)
	
	for massBin in massBins:
		result.Add(getMassHisto("rootfiles/ADD_LambdaT%d_%s_13TeV-pythia8_cff_1.root"%(mass,massBin)))
	
	result.Scale(0.333333)
	return result


# get mass distribution from DY files	
def getMassDistroDY():
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
		    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
	
	result = TH1F("h_DY","h_DY",240,0,12000)
	
	if (muon): leptype = "MuMu"
	else: leptype = "EE"

	for massBin in massBins:
		result.Add(getMassHisto("rootfiles/DYTo%s_%s_13TeV-pythia8_cff_1.root"%(leptype, massBin)))
	
	return result


# write datacards based on
# sigYield = ADD - DY
# dyYield = DY event yield only
def writeDatacard(sigYield, dyYield, lambdaT):
	
	fname = "dataCards/ee_limit/dataCard_ee_lambda%d_singlebin.txt"%(lambdaT)
	fout = open(fname, "w")
	fout.write(template%(sigYield-dyYield, dyYield))
	fout.close()
	return fname


# execute datacards
# and move them to /dataCards
def executeDatacard(fname, lambdaT):

	combine_command = "combine -M AsymptoticLimits %s -m %d"%(fname, lambdaT)
	print ">>> command: " + combine_command

	p = subprocess.Popen(combine_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		print line.rstrip("\n")
	print ">>> higgsCombine rootfile created"
	retval = p.wait()

	rf = "higgsCombineTest.AsymptoticLimits.mH%d.root"%(lambdaT)
	mvfile = subprocess.Popen("mv ./%s ./dataCards/ee_limit/%s"%(rf, rf), shell=True)
	print ">>> file moved"
	retval = p.wait()


# plot invariant mass spectrum for a single lambdaT
# write datacards, and execute datacards
def main():

	lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
	# lambdas = [4000]
	signalHists = []

	# read in histograms
	# and scale by (1/binwidth)	
	for lambdaT in lambdas:
		signalHist = getMassDistroSignal(str(lambdaT), lambdaT)
		signalHist.Scale(0.02)
		signalHists.append(signalHist)
		print ">>> Finished reading lambda = %d"%lambdaT
	dyHist = getMassDistroDY()
	dyHist.Scale(0.02)

	# read event yield from mass spectrum
	# above a minimum mass Mmin
	Mmin = 2800
	dyNum = 0                    # DY yield
	sigNum = [0]*len(lambdas)    # signal yields for lambdas
	bw = dyHist.GetBinWidth(1)   # binwidth = 50 GeV

	for bini in range(1, dyHist.GetSize()-1):
		if (dyHist.GetBinCenter(bini) < Mmin):
			continue
		dyNum += dyHist.GetBinContent(bini) * bw
		for (i, histi) in enumerate(signalHists):
			if (histi.GetBinCenter(bini) > lambdas[i]):
				continue
			sigNum[i] += histi.GetBinContent(bini) * bw

	# print information
	# and execute datacards
	print "-----------------------------------"
	print ">>> Min mass cut: %f GeV"%Mmin
	print ">>> DY event yield: %f"%dyNum
	for i in range(len(lambdas)):
		print ">>> Signal lambda %d event yield: %f"%(lambdas[i], sigNum[i])
	print "-----------------------------------"
	
	for i in range(len(lambdas)):
		fname = writeDatacard(sigNum[i], dyNum, lambdas[i])
		executeDatacard(fname, lambdas[i])
	print ">>> Done!"


# MAIN
if __name__ == "__main__":
	main()
