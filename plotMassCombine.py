from ROOT import * 
from setTDRStyle import setTDRStyle
from copy import deepcopy
#import ratios

isMuon = False
resolution = True

from readData import getMassHisto, getMassDistroSignal, getMassDistroDY

# plot invariant mass spectrum for a single lambdaT
def main():

	lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
	signalHists = []

	# read in histograms	
	for lambdaT in lambdas:
		signalHist = getMassDistroSignal("ADD",lambdaT, isMuon, True)
		signalHist.Scale(0.02)
		signalHists.append(signalHist)
		print ">>> Finished reading lambda = %d"%lambdaT
	dyHist = getMassDistroDY(isMuon)
	dyHist.Scale(0.02)

	# set up canvas
	canv = TCanvas("c1","c1",800,800)
	plotPad = TPad("plotPad","plotPad",0,0.03,1,1)
	style = setTDRStyle()
	gStyle.SetOptStat(0)
	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()
	plotPad.SetLogy()
	plotPad.DrawFrame(120,1e-7,7000,3.5e3,";mass [GeV];Events / 50 GeV")

	# plotting
	for (i, histi) in enumerate(signalHists):
		histi.SetLineColor(i + 2)
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
			leg.AddEntry(histi,"Drell-Yan x ADD smeared (#Lambda = %d)"%(1000*(i+4)),"l")
		leg.AddEntry(dyHist,"Drell-Yan smeared","l")
	else:
		for (i, histi) in enumerate(signalHists):
			leg.AddEntry(histi,"Drell-Yan x ADD (#Lambda = %d)"%(1000*(i+4)),"l")
		leg.AddEntry(dyHist,"Drell-Yan","l")

	leg.Draw("same")

	# save graphs
	if resolution:	
		if isMuon:
			canv.Print("rawDataPlots/MassHist_combine_Muon.pdf")
		else:	
			canv.Print("rawDataPlots/MassHist_combine_Electron.pdf")
	else:
		canv.Print("rawDataPlots/MassHist_combine.pdf")



if __name__ == "__main__":
    main()
