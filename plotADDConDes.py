from ROOT import * 
#from numpy import array as ar
#from array import array
from setTDRStyle import setTDRStyle
from copy import deepcopy
import ratios
from math import *
	
rand = TRandom3()
resolution = True
isMuon = False

weightHistMu = TFile("ADDdata/effMapMuons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
weightHistEle = TFile("ADDdata/effMapElectrons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")


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



# get mass distribution of files
def getMassDistroSignal(name, model, lambdaT, heli, isMuon):
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
		    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
	result = TH1F("h_%s"%name,"h_%s"%name,240,0,12000)

	for massBin in massBins:
		if heli == "Con":
			fname = "%sdata/%s_LambdaT%d_%s_13TeV-pythia8_cff_1.root"%(model, model, lambdaT, massBin)
		else: # model == "CI"
			fname = "%sdata/%s_LambdaT%d_Des_%s_13TeV-pythia8_cff_1.root"%(model, model, lambdaT, massBin)
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
		result.Add(getMassHisto("ADDdata/DYTo%s_%s_13TeV-pythia8_cff_1.root"%(leptype, massBin), isMuon))
	
	return result
		

# get mass spectrum for signal files, for a single lambdaT
# ADD and CI signals
def getMassDistro(model, heli, lambdaT, isMuon):

	retlist = []
	for helicity in heli:
		retlist.append(getMassDistroSignal(model+str(lambdaT)+helicity, model, lambdaT, helicity, isMuon).Clone())
	return retlist


def main():
	
	model = "ADD"
	helicity = ["Con", "Des"]
	lambdaT = 6000

        # read in histograms
        signalHists = []
	for heli in helicity:
		temp = getMassDistroSignal(model+heli, model, lambdaT, heli, isMuon)
		temp.Scale(0.02)
		signalHists.append(temp)

        # read in DY histograms
        dyHist = getMassDistroDY(isMuon)
        dyHist.Scale(0.02)

        # set up canvas
        canv = TCanvas("c1","c1",800,800)
        plotPad = TPad("plotPad","plotPad",0,0.3,1,1)
        ratioPad = TPad("ratioPad","ratioPad",0,0,1,0.3)
        style = setTDRStyle()
        gStyle.SetOptStat(0)
        plotPad.UseCurrentStyle()
        ratioPad.UseCurrentStyle()
        plotPad.Draw()
        ratioPad.Draw()
        plotPad.cd()
        plotPad.SetLogy()
        plotPad.DrawFrame(120,1e-7,7000,2.5e3,";mass [GeV];Events / 50 GeV")

        # plotting
        for (i, sigHist) in enumerate(signalHists):
                sigHist.SetLineColor(i*2+2)
                sigHist.Draw("histsame")
	dyHist.SetLineColor(1)
        dyHist.Draw("histsame")

        # draw CMS prelim
        latex = TLatex()
        latex.SetTextFont(42)
        latex.SetTextAlign(31)
        latex.SetTextSize(0.04)
        latex.SetNDC(True)
        latexCMS = TLatex()
        latexCMS.SetTextFont(61)
        latexCMS.SetTextSize(0.055)
        latexCMS.SetNDC(True)
        latexCMSExtra = TLatex()
        latexCMSExtra.SetTextFont(52)
        latexCMSExtra.SetTextSize(0.03)
        latexCMSExtra.SetNDC(True)

        latexCMSlepton = "ee"
        if isMuon: latexCMSlepton = "#mu#mu"
        latex.DrawLatex(0.95, 0.96, "35.9 fb^{-1} (13 TeV, %s)"%latexCMSlepton)
        cmsExtra = "#splitline{Private Work}{Simulation}"
        latexCMS.DrawLatex(0.19,0.88,"CMS")
        if "Simulation" in cmsExtra:
                yLabelPos = 0.81
        else:
                yLabelPos = 0.84
        latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))

        # draw legend
        leg = TLegend(0.4, 0.71, 0.94, 0.92,"","brNDC")
        leg.SetFillColor(10)
        leg.SetFillStyle(0)
        leg.SetLineColor(10)
        leg.SetShadowColor(0)
        leg.SetBorderSize(1)

        if resolution:
                leg.AddEntry(dyHist,"Drell-Yan smeared (#Lambda_{T} = %d)"%lambdaT,"l")
                for (i, heli) in enumerate(helicity):
                        leg.AddEntry(signalHists[i],"Drell-Yan x %s_%s smeared (#Lambda_{T} = %d)"%(model, heli, lambdaT),"l")
                #leg.AddEntry(signalHists[1],"Drell-Yan x %s Des smeared (#Lambda = %d)"%(model, lambdaT),"l")
        #else:
        #        leg.AddEntry(dyHist,"Drell-Yan (#Lambda = %d)"%lambdaT,"l")
        #        for (i, helicity) in enumerate(heli):
        #                leg.AddEntry(signalHists[i],"Drell-Yan x %s%s (#Lambda = %d)"%(model, helicity, lambdaT),"l")
        #        #leg.AddEntry(signalHists[1],"Drell-Yan x %s Des (#Lambda = %d)"%(model, lambdaT),"l")
        leg.Draw("same")

        # draw ratio pad
        ratioPad.cd()
        ratio = ratios.RatioGraph(signalHists[0], signalHists[1], 120, 7000,title="Con / Des",
                        yMin=0.5,yMax=2.0,ndivisions=10,color=signalHists[0].GetLineColor(),adaptiveBinning=0.25)
        ratio.draw(gPad,True,False,True,chi2Pos=0.7)
        #else: # model == "CI":
        #        ratio = ratios.RatioGraph(signalHists[0], signalHists[3], 120, 7000,title="ConLL / DesLL",
        #                yMin=0.5,yMax=2.0,ndivisions=10,color=signalHists[0].GetLineColor(),adaptiveBinning=0.25)
        #        ratio.draw(gPad,True,False,True,chi2Pos=0.7)


        # save graphs
        #if resolution:
        #        if isMuon:
        #                canv.Print("rawDataPlots/%s_MassHist_LambdaT%d_Muon.pdf"%(model, lambdaT))
        #        else:
        #                canv.Print("rawDataPlots/%s_MassHist_LambdaT%d_Electron.pdf"%(model, lambdaT))
        #else:
        #        canv.Print("rawDataPlots/%s_MassHist_LambdaT%d.pdf"%(model, lambdaT))
	canv.Print("rawDataPlots/ADD_MassHist_LambdaT6000.pdf")





if __name__ == "__main__":
    main()
