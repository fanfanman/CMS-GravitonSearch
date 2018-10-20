from ROOT import * 
#from numpy import array as ar
#from array import array
#from setTDRStyle import setTDRStyle
from copy import deepcopy
import ratios

#muon = False
#resolution = True

#if muon:
#	from muonResolution import getResolution
#else:
#	from electronResolution import getResolution
	
rand = TRandom3()
resolution = True

weightHistMu = TFile("ADDdata/effMapMuons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
weightHistEle = TFile("ADDdata/effMapElectrons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")


def getMassHisto(fileName, isMuon):

	f = TFile(fileName,"OPEN")

	if isMuon: from muonResolution import getResolution
	else: from electronResolution import getResolution

	from ROOT import TChain
	xsecTree = TChain()
	xsecTree.Add(fileName+"/crossSecTree")
	for entry in xsecTree:
		xsec = entry.crossSec
	
	tree = TChain()
	tree.Add(fileName+"/pdfTree")
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
			if isMuon:
				if abs(eta1) > 2.4 or abs(eta2) > 2.4: continue
				weight = weightHistMu.GetBinContent(weightHistMu.GetXaxis().FindBin(abs(eta1)),
								    weightHistMu.GetYaxis().FindBin(pt1)
				) * weightHistMu.GetBinContent(	    weightHistMu.GetXaxis().FindBin(abs(eta2)),
								    weightHistMu.GetYaxis().FindBin(pt2))
				if abs(eta1) < 1.2 and abs(eta2) < 1.2:
					BB = True
			else:
				if abs(eta2) > 2.5 or abs(eta2) > 2.5: continue
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
def getMassDistroSignal(name, lambdaT, isMuon, isCon):
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
		    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
	result = TH1F("h_%s"%name,"h_%s"%name,240,0,12000)
	
	if isCon: label = "Con"
	else: label = "Des"

	for massBin in massBins:
		result.Add(getMassHisto("ADDdata/ADD_LambdaT%d_%s_%s_13TeV-pythia8_cff_1.root"%(lambdaT,label,massBin), isMuon))

	result.Scale(0.333333)
	return result


# get mass distribution from DY files	
def getMassDistroDY(isMuon):
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
		    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
	result = TH1F("h_DY","h_DY",240,0,12000)
	
	if (isMuon): leptype = "MuMu"
	else: leptype = "EE"

	for massBin in massBins:
		result.Add(getMassHisto("ADDdata/DYTo%s_%s_13TeV-pythia8_cff_1.root"%(leptype, massBin), isMuon))
	
	return result
		

if __name__ == "__main__":
    main()