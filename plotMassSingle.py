from ROOT import * 
from setTDRStyle import setTDRStyle
from copy import deepcopy
import ratios

# Parameter setting
resolution = True
isMuon = False

from readData import getMassHisto, getMassDistroSignal, getMassDistroDY		

# plot invariant mass spectrum for a single lambdaT
def plotsingle(lambdaT):

	# read in histograms	
	signalCon = getMassDistroSignal("ADD", lambdaT, isMuon, True)
	signalDes = getMassDistroSignal("ADD", lambdaT, isMuon, False)
	dyHist = getMassDistroDY(isMuon)
	
	signalCon.Scale(0.02)
	signalDes.Scale(0.02)
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
	signalCon.SetLineColor(kRed)
	signalDes.SetLineColor(kBlue)
	signalCon.Draw("histsame")
	signalDes.Draw("histsame")
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
		leg.AddEntry(signalCon,"Drell-Yan x ADD Con smeared (#Lambda = %d)"%lambdaT,"l")
		leg.AddEntry(signalDes,"Drell-Yan x ADD Des smeared (#Lambda = %d)"%lambdaT,"l")
	else:
		leg.AddEntry(dyHist,"Drell-Yan (#Lambda = %d)"%lambdaT,"l")
		leg.AddEntry(signalCon,"Drell-Yan x ADD Con (#Lambda = %d)"%lambdaT,"l")
		leg.AddEntry(signalDes,"Drell-Yan x ADD Des (#Lambda = %d)"%lambdaT,"l")

	leg.Draw("same")

	# draw ratio pad
	ratioPad.cd()
	ratioCon = ratios.RatioGraph(signalCon, dyHist, 120, 7000,title="S+B / B Con",yMin=0.5,yMax=1.5,ndivisions=10,color=signalCon.GetLineColor(),adaptiveBinning=0.25)
	ratioCon.draw(gPad,True,False,True,chi2Pos=0.7)
	ratioDes = ratios.RatioGraph(signalDes, dyHist, 120, 7000,title="S+B / B Des",yMin=0.5,yMax=1.5,ndivisions=10,color=signalDes.GetLineColor(),adaptiveBinning=0.25)
	ratioDes.draw(gPad,True,False,True,chi2Pos=0.7)

	# save graphs
	if resolution:	
		if isMuon:
			canv.Print("rawDataPlots/MassHist_LambdaT%d_Muon.pdf"%(lambdaT))
		else:	
			canv.Print("rawDataPlots/MassHist_LambdaT%d_Electron.pdf"%(lambdaT))
	else:
		canv.Print("rawDataPlots/MassHist_LambdaT%d.pdf"%(lambdaT))

		
def main():
    
	# for each lambdaT, plot a single graph for it
	lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
	# lambdas = [4000]
	for lambdaT in lambdas:
		plotsingle(lambdaT)


if __name__ == "__main__":
    main()
