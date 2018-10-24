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

weightHistMu = TFile("ADDdata/effMapMuons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
weightHistEle = TFile("ADDdata/effMapElectrons.root","OPEN").Get("hCanvas").GetPrimitive("plotPad").GetPrimitive("bla")
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
		#print "filename = %s, XSec = %f"%(fileName, xsec)
	
	result1 = TH1F("h_%s_1"%fileName,"h_%s_1"%fileName,240,0,12000)  # leading muon
	result2 = TH1F("h_%s_2"%fileName,"h_%s_2"%fileName,240,0,12000)  # trailing muon

	count = 0
	for ev in tree:
		count += 1
		mass = tree.GetLeaf("bosonP4/mass").GetValue()
		weight1 = 1.
		weight2 = 1.
		if resolution:
			eta1 = tree.GetLeaf("decay1P4/eta").GetValue()
			eta2 = tree.GetLeaf("decay2P4/eta").GetValue()
			pt1 = tree.GetLeaf("decay1P4/pt").GetValue()
			pt2 = tree.GetLeaf("decay2P4/pt").GetValue()
			BB = False

			if muon:
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
			
			#if BB:						
			#	mass = mass*rand.Gaus(1,getResolution(mass)["sigma"]["BB"])
			#else:
			#	mass = mass*rand.Gaus(1,getResolution(mass)["sigma"]["BE"])		
		
		result1.Fill(pt1, weight1)
		result2.Fill(pt2, weight2)

	result1.Sumw2()
	result1.Scale(36300*xsec/count)
	result2.Sumw2()
	result2.Scale(36300*xsec/count)

	return deepcopy(result1), deepcopy(result2)


# get mass distribution of ADD files
def getMassDistroSignal(name, mass):
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
		    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
	
	result1 = TH1F("h_%s_1"%name,"h_%s_1"%name,240,0,12000)
	result2 = TH1F("h_%s_2"%name,"h_%s_2"%name,240,0,12000)
	temp1 = TH1F()
	temp2 = TH1F()	

	for massBin in massBins:
		temp1, temp2 = getMassHisto("ADDdata/ADD_LambdaT%d_Con_%s_13TeV-pythia8_cff_1.root"%(mass,massBin))
		result1.Add(temp1)
		result2.Add(temp2)
	
	result1.Scale(0.333333)
	result2.Scale(0.333333)

	return result1, result2


# get mass distribution from DY files	
def getMassDistroDY():
	
	massBins = ["M120To200", "M200To400", "M400To800", "M800To1400", "M1400To2300",
		    "M2300To3500", "M3500To4500", "M4500To6000", "M6000ToInf"]
	
	result1 = TH1F("h_DY_1","h_DY_1",240,0,12000)
	result2 = TH1F("h_DY_2","h_DY_2",240,0,12000)
	temp1 = TH1F()
	temp2 = TH1F()
	
	if (muon): leptype = "MuMu"
	else: leptype = "EE"

	for massBin in massBins:
		temp1, temp2 = getMassHisto("ADDdata/DYTo%s_%s_13TeV-pythia8_cff_1.root"%(leptype, massBin))
		result1.Add(temp1)
		result2.Add(temp2)
	
	return result1, result2


# plot invariant mass spectrum for a single lambdaT
def plotsingle(signalHists, dyHist, label):

	# set up canvas
	canv = TCanvas("c1","c1",800,800)
	plotPad = TPad("plotPad","plotPad",0,0.03,1,1)
	#ratioPad = TPad("ratioPad","ratioPad",0,0,1,0.3)
	style = setTDRStyle()
	gStyle.SetOptStat(0)
	plotPad.UseCurrentStyle()
	#ratioPad.UseCurrentStyle()
	plotPad.Draw()	
	#ratioPad.Draw()	
	plotPad.cd()
	plotPad.SetLogy()
	plotPad.DrawFrame(120,2e-8,5000,2.5e3,";Pt [GeV] (%s);Events / 50GeV"%label)

	# plotting
	for (i, histi) in enumerate(signalHists):
		histi.SetLineColor(i+2)
		histi.SetLineWidth(2)
		histi.Draw("histsame")
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
	leg = TLegend(0.41, 0.57, 0.94, 0.92,"","brNDC")
	leg.SetFillColor(10)
	leg.SetFillStyle(0)
	leg.SetLineColor(10)
	leg.SetShadowColor(0)
	leg.SetBorderSize(1)		

	if resolution:
		for (i, histi) in enumerate(signalHists):
			leg.AddEntry(histi, "Drell-Yan x ADD smeared (#Lambda = %s)"%(1000*(i+4)),"l")
		leg.AddEntry(dyHist,"Drell-Yan smeared","l")
	else:
		for (i, histi) in enumerate(signalHists):
			leg.AddEntry(histi,"Drell-Yan x ADD (#Lambda = %s)"%(1000*(i+4)),"l")
		leg.AddEntry(dyHist,"Drell-Yan","l")

	leg.Draw("same")

	'''# draw binning lines
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
	ratio.draw(gPad,True,False,True,chi2Pos=0.7)'''
		
	# save graphs
	if resolution:	
		if muon:
			canv.Print("rawDataPlots/PtHist_combine_%sMuon_Con.pdf"%label)
		else:	
			canv.Print("rawDataPlots/PtHist_combine_%sElectron_Con.pdf"%label)
	else:
		canv.Print("rawDataPlots/PtHist_combine_%s_Con.pdf"%label)

		
def main():
    
	# for each lambdaT, plot a single graph for it
	# lambdas = [10000]
	lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
	
	sig1 = []
	sig2 = []
	for lambdaT in lambdas:
		temps1, temps2 = getMassDistroSignal("ADD", lambdaT)
		temps1.Scale(0.02)
		temps2.Scale(0.02)
		sig1.append(temps1)
		sig2.append(temps2)
		print ">>> Finished reading lambda = %d"%lambdaT
	dy1, dy2 = getMassDistroDY()
	dy1.Scale(0.02)
	dy2.Scale(0.02)
	plotsingle(sig1, dy1, "leading")
	plotsingle(sig2, dy2, "trailing")


if __name__ == "__main__":
    main()
