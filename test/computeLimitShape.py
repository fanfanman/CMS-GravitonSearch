from ROOT import * 
from setTDRStyle import setTDRStyle
from copy import deepcopy

import sys, os
#import ratios
import subprocess
import numpy as np
rand = TRandom3()

## Initialization
isMuon = False
resolution = True
withBinError = True

from readData import getMassDistroDY, getMassDistro

# plot invariant mass spectrum for a single lambdaT
# write datacards, and execute datacards
def main(argv):

	# read in parameters
	model = argv[0]
	#Mmin = float(argv[1])
	
	if model == "ADD": 
		lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
		# heli = ["_Con", "_Des"]
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

	outputfile = TFile("test.root", "NEW")
	outputfile.cd()
	#dyHist.Write()
	#sigHists[2][0].Write()
	newsig = TH1F("h_ADD", "h_ADD", 66, 2700, 6000)
	newbkg = TH1F("h_DY2", "h_DY2", 66, 2700, 6000)
	for i in range(66):
		bincenter = 2725 + i * 50
		binnum = 2700/50 + 1 + i
		print "check bin center %d matches with %d ?"%(bincenter, dyHist.GetBinCenter(binnum))
		newsig.Fill(bincenter, sigHists[2][0].GetBinContent(binnum))
		newbkg.Fill(bincenter, dyHist.GetBinContent(binnum))

	newsig.Write()
	newbkg.Write()
	outputfile.Close()
	print "SAVED!"


# MAIN
if __name__ == "__main__":
	main(sys.argv[1:])
