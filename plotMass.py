from ROOT import * 
from numpy import array as ar
from array import array
from setTDRStyle import setTDRStyle
from copy import deepcopy

muon = False
resolution = True

if muon:
	from muonResolution import getResolution
else:
	from electronResolution import getResolution
	
rand = TRandom3()

weightHistMu = TFile("effMapMuons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
weightHistEle = TFile("effMapElectrons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
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
				) * weightHistMu.GetBinContent(     weightHistMu.GetXaxis().FindBin(abs(eta2)),
								    weightHistMu.GetYaxis().FindBin(pt2))
				if abs(eta1) < 1.2 and abs(eta2) < 1.2:
					BB = True
			else:
				if abs(eta2) > 2.5 or abs(eta2) > 2.5: continue
				#~ print pt2
				#~ print weightHistEle.GetYaxis().FindBin(pt2)
				weight = weightHistEle.GetBinContent(weightHistEle.GetXaxis().FindBin(abs(eta1)),
								     weightHistEle.GetYaxis().FindBin(pt1)
				)*weightHistEle.GetBinContent(	     weightHistEle.GetXaxis().FindBin(abs(eta2)),
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
	result.Scale(36300*xsec/10000)
	return deepcopy(result)
	
def getMassDistroSignal(name,mass):
	
	massBins = ["M120To200","M200To400","M400To800","M800To1400","M1400To2300","M2300To3500","M3500To4500","M4500To6000","M6000ToInf"]
	
	result = TH1F("h_%s"%name,"h_%s"%name,240,0,12000)
	
	for massBin in massBins:
		result.Add(getMassHisto("ADD_LambdaT%d_%s_13TeV-pythia8_cff_1.root"%(mass,massBin)))
	result.Scale(0.33)
	return result
	
def getMassDistroDY():
	
	massBins = ["M120To200","M200To400","M400To800","M800To1400","M1400To2300","M2300To3500","M3500To4500","M4500To6000","M6000ToInf"]
	
	result = TH1F("h_DY","h_DY",240,0,12000)
	
	if (muon): leptype = "MuMu"
	else: leptype = "EE"	

	for massBin in massBins:
		result.Add(getMassHisto("DYTo%s_%s_13TeV-pythia8_cff_1.root"%(leptype, massBin)))
	
	return result
		
	
def main():
	### for data

	lambdaT = 10000
	
	#~ for signal in ["Chi","Eta","I","N","Q","SQ","PSI","SSM"]:
	signalHist = getMassDistroSignal("ADD",lambdaT)
	dyHist = getMassDistroDY()

	signalHist.SetLineColor(kRed)

	canv = TCanvas("c1","c1",800,800)

	plotPad = TPad("plotPad","plotPad",0,0.3,1,1)
	ratioPad = TPad("ratioPad","ratioPad",0,0,1,0.3)
	style = setTDRStyle()
	ROOT.gStyle.SetOptStat(0)
	plotPad.UseCurrentStyle()
	ratioPad.UseCurrentStyle()
	plotPad.Draw()	
	ratioPad.Draw()	
	plotPad.cd()
	plotPad.SetLogy()

	plotPad.DrawFrame(120,1e-5,7000,2.5e5,";mass [GeV];Events / 50 GeV")

	signalHist.Draw("histsame")
	dyHist.Draw("histsame")




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

	leg = TLegend(0.4, 0.71, 0.89, 0.92,"","brNDC")
	leg.SetFillColor(10)
	leg.SetFillStyle(0)
	leg.SetLineColor(10)
	leg.SetShadowColor(0)
	leg.SetBorderSize(1)		

	if resolution:
		leg.AddEntry(dyHist,"Drell-Yan smeared","l")
		leg.AddEntry(signalHist,"Drell-Yan x ADD smeared","l")
	else:
		leg.AddEntry(dyHist,"Drell-Yan","l")
		leg.AddEntry(signalHist,"Drell-Yan x ADD","l")

	leg.Draw("same")

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

	ratioPad.cd()
					
	import ratios
	ratio = ratios.RatioGraph(signalHist,dyHist, 120, 7000,title="S+B / B ",yMin=0.5,yMax=1.5,ndivisions=10,color=signalHist.GetLineColor(),adaptiveBinning=0.25)
	ratio.draw(ROOT.gPad,True,False,True,chi2Pos=0.7)					
		


	if resolution:	
		if muon:
			canv.Print("generationExample_LambdaT%d_Muon.pdf"%(lambdaT))
		else:	
			canv.Print("generationExample_LambdaT%d_Electron.pdf"%(lambdaT))
	else:
		canv.Print("generationExample_LambdaT%d.pdf"%(lambdaT))
		#~ 
		

		
main()
