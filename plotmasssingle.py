from ROOT import * 
from numpy import array as ar
from array import array
from setTDRStyle import setTDRStyle
from copy import deepcopy
import ratios

muon = False
resolution = True

if muon:
	from muonResolution import getResolution
else:
	from electronResolution import getResolution
	
rand = TRandom3()

weightHistMu = TFile("rootfiles/effMapMuons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
weightHistEle = TFile("rootfiles/effMapElectrons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
#~ for item in weightHistMu.GetListOfPrimitives():
	#~ print item

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
		

# plot invariant mass spectrum for a single lambdaT
def plotsingle(lambdaT):

	# read in histograms	
	signalHist = getMassDistroSignal("ADD",lambdaT)
	dyHist = getMassDistroDY()

	dyHist.Scale(0.02)
	signalHist.Scale(0.02)

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
	signalHist.SetLineColor(kRed)
	signalHist.Draw("histsame")
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
		
	latex.DrawLatex(0.95, 0.96, "36.3 fb^{-1} (13 TeV)")
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
		leg.AddEntry(dyHist,"Drell-Yan smeared (#Lambda = %d)"%lambdaT,"l")
		leg.AddEntry(signalHist,"Drell-Yan x ADD smeared (#Lambda = %d)"%lambdaT,"l")
	else:
		leg.AddEntry(dyHist,"Drell-Yan (#Lambda = %d)"%lambdaT,"l")
		leg.AddEntry(signalHist,"Drell-Yan x ADD (#Lambda = %d)"%lambdaT,"l")

	leg.Draw("same")

	# draw binning lines
	from ROOT import TLine
	line200 = TLine(200,1e-5,200,5e4)
	line200.Draw("same")
	line400 = TLine(400,1e-5,400,1e4)
	line400.Draw("same")
	line800 = TLine(800,1e-5,800,1e3)
	line800.Draw("same")
	line1400 = TLine(1400,1e-5,1400,1e2)
	line1400.Draw("same")
	line2300 = TLine(2300,1e-5,2300,1)
	line2300.Draw("same")
	line3500 = TLine(3500,1e-5,3500,1e-1)
	line3500.Draw("same")
	line4500 = TLine(4500,1e-5,4500,1e-2)
	line4500.Draw("same")
	line6000 = TLine(6000,1e-5,6000,1e-2)
	line6000.Draw("same")

	# draw ratio pad
	ratioPad.cd()
	ratio = ratios.RatioGraph(signalHist,dyHist, 120, 7000,title="S+B / B ",yMin=0.5,yMax=1.5,ndivisions=10,color=signalHist.GetLineColor(),adaptiveBinning=0.25)
	ratio.draw(gPad,True,False,True,chi2Pos=0.7)					
		
	# save graphs
	if resolution:	
		if muon:
			canv.Print("plots/MassHist_LambdaT%d_Muon.pdf"%(lambdaT))
		else:	
			canv.Print("plots/MassHist_LambdaT%d_Electron.pdf"%(lambdaT))
	else:
		canv.Print("plots/MassHist_LambdaT%d.pdf"%(lambdaT))

		
def main():
    
	# for each lambdaT, plot a single graph for it
	lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
	# lambdas = [4000]
	for lambdaT in lambdas:
		plotsingle(lambdaT)


if __name__ == "__main__":
    main()
