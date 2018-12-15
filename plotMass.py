from ROOT import * 
from setTDRStyle import setTDRStyle
from copy import deepcopy
import ratios
import sys

# Parameter setting
model = ""
resolution = True
isMuon = False
from readData import getMassDistroDY, getMassDistro
from readData import getMassDistroSignal


# plot invariant mass spectrum for a single lambdaT, with different helicity
def plotsingle(model, heli, lambdaT):

	# read in histograms
	signalHists = getMassDistro(model, heli, lambdaT, isMuon)
	for histi in signalHists:
		histi.Scale(0.02)

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
		sigHist.SetLineColor(i+2)
		sigHist.Draw("histsame")
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
		leg.AddEntry(dyHist,"Drell-Yan smeared (#Lambda = %d)"%lambdaT,"l")
		for (i, helicity) in enumerate(heli):
			leg.AddEntry(signalHists[i],"Drell-Yan x %s%s smeared (#Lambda = %d)"%(model, helicity, lambdaT),"l")
		#leg.AddEntry(signalHists[1],"Drell-Yan x %s Des smeared (#Lambda = %d)"%(model, lambdaT),"l")
	else:
		leg.AddEntry(dyHist,"Drell-Yan (#Lambda = %d)"%lambdaT,"l")
		for (i, helicity) in enumerate(heli):
			leg.AddEntry(signalHists[i],"Drell-Yan x %s%s (#Lambda = %d)"%(model, helicity, lambdaT),"l")
		#leg.AddEntry(signalHists[1],"Drell-Yan x %s Des (#Lambda = %d)"%(model, lambdaT),"l")
	leg.Draw("same")
	
	# draw ratio pad
	ratioPad.cd()
	if model == "ADD":
		ratio = ratios.RatioGraph(signalHists[0], signalHists[1], 120, 7000,title="S+B Con / S+B Des",
			yMin=0.5,yMax=2.0,ndivisions=10,color=signalHists[0].GetLineColor(),adaptiveBinning=0.25)
		ratio.draw(gPad,True,False,True,chi2Pos=0.7)
	else: # model == "CI":
		ratio = ratios.RatioGraph(signalHists[0], signalHists[3], 120, 7000,title="ConLL / DesLL",
			yMin=0.5,yMax=2.0,ndivisions=10,color=signalHists[0].GetLineColor(),adaptiveBinning=0.25)
                ratio.draw(gPad,True,False,True,chi2Pos=0.7)

	# save graphs
	if resolution:	
		if isMuon:
			canv.Print("rawDataPlots/%s_MassHist_LambdaT%d_Muon.pdf"%(model, lambdaT))
		else:	
			canv.Print("rawDataPlots/%s_MassHist_LambdaT%d_Electron.pdf"%(model, lambdaT))
	else:
		canv.Print("rawDataPlots/%s_MassHist_LambdaT%d.pdf"%(model, lambdaT))


# plot a spectrum for a single helicity, with different lambdas
def plotcombine(model, lambdas, helicity):

	signalHists = []
        # read in histograms
        for lambdaT in lambdas:
                signalHist = getMassDistroSignal(model+helicity, model, lambdaT, helicity, isMuon)
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
        leg = TLegend(0.41, 0.57, 0.94, 0.92,"","brNDC")
        leg.SetFillColor(10)
        leg.SetFillStyle(0)
        leg.SetLineColor(10)
        leg.SetShadowColor(0)
        leg.SetBorderSize(1)
	
	if resolution:
		leg.AddEntry(dyHist, "Drell-Yan smeared", "l")
                for (i, histi) in enumerate(signalHists):
                        leg.AddEntry(histi,"Drell-Yan x %s%s smeared (#Lambda = %d)"%(model, helicity, lambdas[i]),"l")
        else:
		leg.AddEntry(dyHist, "Dreall-Yan", "l")
                for (i, histi) in enumerate(signalHists):
                        leg.AddEntry(histi,"Drell-Yan x %s%s (#Lambda = %d)"%(model, helicity, lambdas[i]),"l")
        leg.Draw("same")

        # save graphs
        if resolution:
                if isMuon:
                        canv.Print("rawDataPlots/%s_MassHist%s_Muon.pdf"%(model, helicity))
                else:
                        canv.Print("rawDataPlots/%s_MassHist%s_Electron.pdf"%(model, helicity))
        else:
                canv.Print("rawDataPlots/%s_MassHist%s.pdf"%(model, helicity))


		
def main(argv):
    
	model = argv[0]
	
	if model == "ADD": 
		lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
		#heli = ["_Con", "_Des"]
		heli = [""]
	else: 
		#lambdas = [16, 22, 28, 32, 40]
		lambdas = [16]
		heli = ["_ConLL", "_ConLR", "_ConRR", "_DesLL", "_DesLR", "_DesRR"]

	# plot spectrum for each single lambda
	for lambdaT in lambdas:
		plotsingle(model, heli, lambdaT)

	# plot spectrum for each single helicity
	#for helicity in heli:
	#	plotcombine(model, lambdas, helicity)


if __name__ == "__main__":
    main(sys.argv[1:])
