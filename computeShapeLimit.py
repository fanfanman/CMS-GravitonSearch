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
#withBinError = True

## template for dataCards
template1 = """
# Simple counting experiment, with one signal and one background
imax 1  number of channels
jmax 1  number of backgrounds
kmax 2  number of nuisance parameters (sources of systematical uncertainties)
------------
"""

template2 = """
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
process         %s  DY
process          0     1 
rate            -1   -1
------------
lumi    lnN    1.025    -  
"""

binErr = [1.107058442576, 1.107129646424, 1.111071388532, 1.111959151426, 1.110467880822, 1.111761850127, 1.116025662214, 1.112919784656, 1.125483028407, 1.146522316471, 1.120540349664, 1.127278435499, 1.129628607788, 1.132347263131, 1.136856450828, 1.277332285789, 1.148252803167, 1.149009214745, 1.151986350084, 1.15818259897, 1.160844810768, 1.167101670272, 1.169584818388, 1.178803537067, 1.18009873585, 1.190822942538, 1.191051550759, 1.211513491907, 1.205783776747]
binErrEdges = [400 + i * 100 for i in range(29)]

from readData import getMassDistroDY, getMassDistro


# store shape histograms to root files
# for shape analysis
def writeShapefiles(model, sighis, dyhis, lambdaT, Mmin, label):

        outDir = "%sshapeCards/ee_limit_min%d%s/"%(model, Mmin, label)
        if not os.path.exists(outDir):
                os.makedirs(outDir)

	fname = outDir + "shape_ee_%d.root"%(lambdaT)
	fout = TFile(fname, "NEW")
	fout.cd()

        Mmax = 10000
	if model == "ADD": Mmax = lambdaT
	binnum = (Mmax - Mmin)/50
        newsig = TH1F("h_sig_%d%s"%(lambdaT, label), "h_sig_%d%s"%(lambdaT, label), binnum, Mmin, Mmax)
        newbkg = TH1F("h_bkg_%d%s"%(lambdaT, label), "h_bkg_%d%s"%(lambdaT, label), binnum, Mmin, Mmax)
        for i in range(binnum):
                bincenter = Mmin + 25 + i * 50
                binnum = Mmin/50 + 1 + i
                #print "check bin center %d matches with %d ?"%(bincenter, dyHist.GetBinCenter(binnum))
                newsig.Fill(bincenter, sighis.GetBinContent(binnum) - dyhis.GetBinContent(binnum))
                newbkg.Fill(bincenter, dyhis.GetBinContent(binnum))

        newsig.Write()
        newbkg.Write()
        fout.Close()
        print "SAVED!"
	return fname


# write datacards based on
# sigYield = ADD - DY
# dyYield = DY event yield only
def writeDatacard(model, lambdaT, Mmin, label):
	
	outDir = "%sshapeCards/ee_limit_min%d%s/"%(model, Mmin, label)
	if not os.path.exists(outDir):
                os.makedirs(outDir)

	# write the first half of datacard
	fname = outDir + "dataCard_ee_lambda%d_singlebin.txt"%lambdaT
	fout = open(fname, "w")
	fout.write(template1)

	# write shape lines
	bkgline = "shapes  *  *  shape_ee_%d.root  h_bkg_%d%s \n"%(lambdaT, lambdaT, label)
	sigline = "shapes  %s  *  shape_ee_%d.root  h_sig_%d%s \n"%(model, lambdaT, lambdaT, label)
	fout.write(bkgline)
	fout.write(sigline)

	# write second half of datacard
	fout.write(template2%(model))
	binindex = binErrEdges.index(Mmin)
	binerrorline = "binerr    lnN   %f   %f \n"%(binErr[binindex], binErr[binindex])
	fout.write(binerrorline)

	fout.close()
	return fname


# execute datacards
# and move them to /dataCards
def executeDatacard(model, fname, lambdaT, Mmin, label):

	combine_command = "combine -M AsymptoticLimits %s -m %d"%(fname, lambdaT)
	print ">>> command: " + combine_command

	p = subprocess.Popen(combine_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		print line.rstrip("\n")
	print ">>> higgsCombine rootfile created"
	retval = p.wait()

	rf = "higgsCombineTest.AsymptoticLimits.mH%d.root"%(lambdaT)
	mvfile = subprocess.Popen("mv ./%s ./%sshapeCards/ee_limit_min%d%s/%s"%(rf, model, Mmin, label, rf), shell=True)
	print ">>> file moved"
	retval = p.wait()


# plot invariant mass spectrum for a single lambdaT
# write datacards, and execute datacards
def main(argv):

	# read in parameters
	model = argv[0]
	Mmin = int(argv[1])
	
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

	# for each lambdaT, each helicity
	# store histograms into shape files
	# write data cards
	# and run combine AsymptoticLimits method
	for i in range(len(lambdas)):
		for j in range(len(heli)):
			fshape = writeShapefiles(model, sigHists[i][j], dyHist, lambdas[i], Mmin, heli[j])
			fout = writeDatacard(model, lambdas[i], Mmin, heli[j])
			executeDatacard(model, fout, lambdas[i], Mmin, heli[j])
	print ">>> Done!"


# MAIN
if __name__ == "__main__":
	main(sys.argv[1:])
