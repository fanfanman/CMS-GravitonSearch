from ROOT import * 
#from numpy import array as ar
#from array import array
#from setTDRStyle import setTDRStyle
from copy import deepcopy
import ratios
from math import *
	
rand = TRandom3()
resolution = True

weightHistMu = TFile("../ADDdata/effMapMuons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
weightHistEle = TFile("../ADDdata/effMapElectrons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")


# calculate collins angle from three vectors
def calcCosThetaCS(v_dil, v_mum, v_mup):
        ### Function to return value of cos(theta*) in Collins-Soper frame
        ### takes as input 4-vector of dilepton in lab frame, and 4-vectors of mu+
        ### and mu- in dilepton CM frame.

        ### Get pz and E components of mu+ and mu- in lab frame.
        pz_mum = v_mum.Pz()
        e_mum  = v_mum.E()
        pz_mup = v_mup.Pz()
        e_mup  = v_mup.E()

        ## Get mass and pt of dilepton in lab frame
        pt_dil   = v_dil.Pt()
        pl_dil   = v_dil.Pz()
        mass_dil = v_dil.M()
        cos_theta_cs = calcCosThetaCSAnal(pz_mum, e_mum, pz_mup, e_mup, pt_dil, pl_dil, mass_dil)
        return cos_theta_cs


# calculate collins angle
def calcCosThetaCSAnal(pz_mum, e_mum, pz_mup, e_mup, pt_dil, pl_dil, mass_dil):
        ## Analytical calculation of Collins-Soper cos(theta).  Uses pz, e of mu+
        ## and mu-, and pt, pl, and mass of dilepton in lab frame.
        ## debug = false;

        mum_minus = (1./sqrt(2.))*(e_mum - pz_mum)
        mum_plus  = (1./sqrt(2.))*(e_mum + pz_mum)
        mup_minus = (1./sqrt(2.))*(e_mup - pz_mup)
        mup_plus  = (1./sqrt(2.))*(e_mup + pz_mup)

        #~ print mass_dil, pt_dil
        dil_term  = 2./(mass_dil*sqrt((mass_dil*mass_dil) + (pt_dil*pt_dil)))
        mu_term   = (mum_plus*mup_minus) - (mum_minus*mup_plus)
        cos_cs    = dil_term*mu_term

        ## The above calculation assumed dilepton pL > 0. Flip the sign of
        ## cos_cs if this isn't true.
        if (pl_dil < 0.):
                cos_cs *= -1.

        return cos_cs


# get mass histo for a single file
def getMassHisto(fileName, isMuon):

	f = TFile(fileName,"OPEN")

	if isMuon: from muonResolution import getResolution
	else: from electronResolution import getResolution

	from ROOT import TChain
	xsecTree = TChain()
	xsecTree.Add(fileName+"/crossSecTree")
	xsec = 0
	for entry in xsecTree:
		xsec = entry.crossSec
	
	tree = TChain()
	tree.Add(fileName+"/pdfTree")
	result = TH1F("h_%s"%fileName,"h_%s"%fileName,240,0,12000)
	count = tree.GetEntries()
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

	#print count
	result.Sumw2()
	result.Scale(36300*xsec/count)
	return deepcopy(result)


# get kinematics information for a single file
# pt and eta, for leading and trailing leptons
def getKinematicsHisto(fileName, isMuon):
        f = TFile(fileName,"OPEN")

        from ROOT import TChain
        tree = TChain()
        tree.Add(fileName+"/pdfTree")

        xsecTree = TChain()
        xsecTree.Add(fileName+"/crossSecTree")
        for entry in xsecTree:
                xsec = entry.crossSec
                # print xsec

        result1 = TH1F("h_%s_1"%fileName,"h_%s_1"%fileName,240,0,12000)  # leading muon pt
        result2 = TH1F("h_%s_2"%fileName,"h_%s_2"%fileName,240,0,12000)  # trailing muon pt
	result3 = TH1F("h_%s_3"%fileName,"h_%s_3"%fileName,48,-2.4,2.4)  # leading muon eta
	result4 = TH1F("h_%s_4"%fileName,"h_%s_4"%fileName,48,-2.4,2.4)  # trailing muon eta

        count = tree.GetEntries()
        for ev in tree:
                mass = tree.GetLeaf("bosonP4/mass").GetValue()
                weight1 = 1.
                weight2 = 1.
                if resolution:
                        eta1 = tree.GetLeaf("decay1P4/eta").GetValue()
                        eta2 = tree.GetLeaf("decay2P4/eta").GetValue()
                        pt1 = tree.GetLeaf("decay1P4/pt").GetValue()
                        pt2 = tree.GetLeaf("decay2P4/pt").GetValue()
                        BB = False

                        if isMuon:
                                if abs(eta1) > 2.4 or abs(eta2) > 2.4: continue
                                weight1 = weightHistMu.GetBinContent(weightHistMu.GetXaxis().FindBin(abs(eta1)),
                                                                     weightHistMu.GetYaxis().FindBin(pt1))
                                weight2 = weightHistMu.GetBinContent(weightHistMu.GetXaxis().FindBin(abs(eta2)),
                                                                     weightHistMu.GetYaxis().FindBin(pt2))
                                if abs(eta1) < 1.2 and abs(eta2) < 1.2:
                                        BB = True
                        else:
                                if abs(eta2) > 2.5 or abs(eta2) > 2.5: continue
                                weight1 = weightHistEle.GetBinContent(weightHistEle.GetXaxis().FindBin(abs(eta1)),
                                                                      weightHistEle.GetYaxis().FindBin(pt1))
                                weight2 = weightHistEle.GetBinContent(weightHistEle.GetXaxis().FindBin(abs(eta2)),
                                                                      weightHistEle.GetYaxis().FindBin(pt2))
                                if abs(eta1) < 1.4442 and abs(eta2) < 1.4442:
                                        BB = True

                result1.Fill(pt1, weight1)
                result2.Fill(pt2, weight2)
		result3.Fill(eta1, weight1)
		result4.Fill(eta2, weight2)

        result1.Sumw2()
	result2.Sumw2()
	result3.Sumw2()
	result4.Sumw2()
        result1.Scale(36300*xsec/count)
        result2.Scale(36300*xsec/count)
	result3.Scale(36300*xsec/count)
	result4.Scale(36300*xsec/count)

        return deepcopy(result1), deepcopy(result2), deepcopy(result3), deepcopy(result4)


def getKinematicsSignal(name, model, lambdaT, heli, isMuon):
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
                    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
        res1 = TH1F("h_%s_1"%name,"h_%s_1"%name,240,0,12000)
	res2 = TH1F("h_%s_2"%name,"h_%s_2"%name,240,0,12000)
	res3 = TH1F("h_%s_3"%name,"h_%s_3"%name,48,-2.4,2.4)
	res4 = TH1F("h_%s_4"%name,"h_%s_4"%name,48,-2.4,2.4)

        for massBin in massBins:
                if model == "ADD":
                        fname = "%sdata/%s_LambdaT%d%s_%s_13TeV-pythia8_cff_1.root"%(model, model, lambdaT, heli, massBin)
                else: # model == "CI"
                        fname = "%sdata/%s_Lambda%d%s_%s_13TeV-pythia8_cff_1.root"%(model, model, lambdaT, heli, massBin)
                temp1, temp2, temp3, temp4 = getKinematicsHisto(fname, isMuon)
		res1.Add(temp1)
		res2.Add(temp2)
		res3.Add(temp3)
		res4.Add(temp4)
	
	if model == "ADD":
		res1.Scale(0.333333)
		res2.Scale(0.333333)
		res3.Scale(0.333333)
		res4.Scale(0.333333)
	return res1, res2, res3, res4


def getKinematicsDY(isMuon):

        massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
                    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
        res1 = TH1F("h_DY_1","h_DY_1",240,0,12000)
        res2 = TH1F("h_DY_2","h_DY_2",240,0,12000)
        res3 = TH1F("h_DY_3","h_DY_3",48,-2.4,2.4)
        res4 = TH1F("h_DY_4","h_DY_4",48,-2.4,2.4)

        if (isMuon): leptype = "MuMu"
        else: leptype = "EE"

        for massBin in massBins:
                temp1, temp2, temp3, temp4 = getKinematicsHisto("ADDdata/DYTo%s_%s_13TeV-pythia8_cff_1.root"%(leptype, massBin), isMuon)
		res1.Add(temp1)
		res2.Add(temp2)
		res3.Add(temp3)
		res4.Add(temp4)

        return res1, res2, res3, res4


# get mass distribution of files
def getMassDistroSignal(name, model, lambdaT, heli, isMuon):
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
		    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
	result = TH1F("h_%s"%name,"h_%s"%name,240,0,12000)

	for massBin in massBins:
		if model == "ADD":
			fname = "../%sdata/%s_LambdaT%d%s_%s_13TeV-pythia8_cff_1.root"%(model, model, lambdaT, heli, massBin)
		else: # model == "CI"
			fname = "../%sdata/%s_Lambda%d%s_%s_13TeV-pythia8_cff_1.root"%(model, model, lambdaT, heli, massBin)
		result.Add(getMassHisto(fname, isMuon))

	# ADD cannot be separable, but CI separable
	if model == "ADD": result.Scale(0.333333)
	return result


# get mass distribution from DY files	
def getMassDistroDY(isMuon):
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
		    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
	result = TH1F("h_DY","h_DY",240,0,12000)
	
	if (isMuon): leptype = "MuMu"
	else: leptype = "EE"

	for massBin in massBins:
		result.Add(getMassHisto("../ADDdata/DYTo%s_%s_13TeV-pythia8_cff_1.root"%(leptype, massBin), isMuon))
	
	return result
		

# get mass spectrum for signal files, for a single lambdaT
# ADD and CI signals
def getMassDistro(model, heli, lambdaT, isMuon):

	retlist = []
	for helicity in heli:
		retlist.append(getMassDistroSignal(model+str(lambdaT)+helicity, model, lambdaT, helicity, isMuon).Clone())
	return retlist


if __name__ == "__main__":
    main()
