from ROOT import * 
from numpy import array as ar
from array import array
from setTDRStyle import setTDRStyle
from copy import deepcopy
import ratios
import sys

isMuon = False
resolution = True

from readData import getKinematicsSignal, getKinematicsDY

# read in info of pairs of muons: mu1, mu2, dy1, dy2
# avoid reading twice
def readHisto(model, lambdas, helicity):

	pt1 = []
	pt2 = []
	eta1 = []
	eta2 = []
	for lambdaT in lambdas:
		s1, s2, s3, s4 = getKinematicsSignal(model+helicity, model, lambdaT, helicity, isMuon)
		pt1.append(s1)
		pt2.append(s2)
		eta1.append(s3)
		eta2.append(s4)
		print ">>> Finished reading lambdaT = %d"%lambdaT

	return pt1, pt2, eta1, eta2


# plot pt distribution vs lambdaT, for different helicity
def plotPtCombine(signalHists, dyHist, model, lambdas, helicity, label):

	# set up canvas
	canv = TCanvas("c1","c1",800,800)
	plotPad = TPad("plotPad","plotPad",0,0.03,1,1)
	style = setTDRStyle()
	gStyle.SetOptStat(0)
	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()
	plotPad.SetLogy()
	plotPad.DrawFrame(120,2e-8,7000,2.5e3,";Pt [GeV] (%s);Events / 50 GeV"%label)

	# plotting
	for (i, histi) in enumerate(signalHists):
		histi.SetLineColor(i+2)
		histi.Scale(0.02)
		histi.Draw("histsame")
	dyHist.Scale(0.02)
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
	latex.DrawLatex(0.95, 0.96, "36.3 fb^{-1} (13 TeV, %s)"%latexCMSlepton)
	cmsExtra = "#splitline{Private Work}{Simulation}"
	latexCMS.DrawLatex(0.19,0.88,"CMS")
	if "Simulation" in cmsExtra:
		yLabelPos = 0.81	
	else:
		yLabelPos = 0.84	
	latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))				

	# draw legend
	leg = TLegend(0.4, 0.71, 0.89, 0.92,"","brNDC")
	leg.SetFillColor(10)
	leg.SetFillStyle(0)
	leg.SetLineColor(10)
	leg.SetShadowColor(0)
	leg.SetBorderSize(1)		

	if resolution:
		leg.AddEntry(dyHist,"Drell-Yan smeared","l")
		for (i, histi) in enumerate(signalHists):
			leg.AddEntry(histi,"Drell-Yan x %s%s smeared (#Lambda = %s)"%(model, helicity, lambdas[i]),"l")
	else:
		leg.AddEntry(dyHist,"Drell-Yan","l")
		for (i, histi) in enumerate(signalHists):
			leg.AddEntry(histi,"Drell-Yan x %s%s (#Lambda = %s)"%(model, helicity, lambdas[i]),"l")

	leg.Draw("same")

	# save graphs
	if resolution:	
		if isMuon:
			canv.Print("rawDataPlots/%s_PtHist%s_%sMuon.pdf"%(model, helicity, label))
		else:	
			canv.Print("rawDataPlots/%s_PtHist%s_%sElectron.pdf"%(model, helicity, label))
	else:
		canv.Print("rawDataPlots/%s_PtHist%s_%s.pdf"%(model, helicity, label))
	
	
# plot eta distrubtion vs lambdas, for each helicity
def plotEtaCombine(signalHists, dyHist, model, lambdas, helicity, label):

        canv = TCanvas("c1","c1",800,800)
        plotPad = TPad("plotPad","plotPad",0,0.03,1,1)
        style = setTDRStyle()
        gStyle.SetOptStat(0)
        plotPad.UseCurrentStyle()
        plotPad.Draw()
        plotPad.cd()
        plotPad.SetLogy()
        plotPad.DrawFrame(-2.4,1.0e4,2.4,1.0e5,";Eta (%s);Events / 0.1"%label)

        # plotting
	for (i, histi) in enumerate(signalHists):
        	histi.SetLineColor(i+2)
		histi.Scale(10)
        	histi.Draw("histsame")
	dyHist.Scale(10)
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
        latex.DrawLatex(0.95, 0.96, "36.3 fb^{-1} (13 TeV, %s)"%latexCMSlepton)
        cmsExtra = "#splitline{Private Work}{Simulation}"
        latexCMS.DrawLatex(0.19,0.88,"CMS")
        if "Simulation" in cmsExtra:
                yLabelPos = 0.81
        else:
                yLabelPos = 0.84
        latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))

        # draw legend
        leg = TLegend(0.35, 0.72, 0.94, 0.92,"","brNDC")
	leg.SetFillColor(10)
        leg.SetFillStyle(0)
        leg.SetLineColor(10)
        leg.SetShadowColor(0)
        leg.SetBorderSize(1)

        if resolution:
                leg.AddEntry(dyHist,"Drell-Yan smeared","l")
                for (i, histi) in enumerate(signalHists):
                        leg.AddEntry(histi,"Drell-Yan x %s%s smeared (#Lambda = %s)"%(model, helicity, lambdas[i]),"l")
        else:
                leg.AddEntry(dyHist,"Drell-Yan","l")
                for (i, histi) in enumerate(signalHists):
                        leg.AddEntry(histi,"Drell-Yan x %s%s (#Lambda = %s)"%(model, helicity, lambdas[i]),"l")

        leg.Draw("same")

        # save graphs
        if resolution:
                if isMuon:
                        canv.Print("rawDataPlots/%s_EtaHist%s_%sMuon.pdf"%(model, helicity, label))
                else:
                        canv.Print("rawDataPlots/%s_EtaHist%s_%sElectron.pdf"%(model, helicity, label))
        else:
                canv.Print("rawDataPlots/%s_EtaHist%s_%s.pdf"%(model, helicity, label))



# Main function	
def main(argv):
    
        model = argv[0]

        if model == "ADD":
                lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
                heli = ["_Con", "_Des"]
        else:
                lambdas = [16, 22, 28, 32, 40]
                heli = ["_ConLL", "_ConLR", "_ConRR", "_DesLL", "_DesLR", "_DesRR"]

        # plot spectrum for each single lambdaT
	#for lambdaT in lambdas:
	#	plotsingle(model, heli, lambdaT)

        # plot spectrum for each single helicity
        for helicity in heli:
		pt1, pt2, eta1, eta2 = readHisto(model, lambdas, helicity)
		dy1, dy2, dy3, dy4 = getKinematicsDY(isMuon)
		
                plotPtCombine(pt1, dy1, model, lambdas, helicity, "leading")
		#plotPtCombine(pt2, dy2, model, lambdas, helicity, "trailing")
		plotEtaCombine(eta1, dy3, model, lambdas, helicity, "leading")
		#plotEtaCombine(eta2, dy4, model, lambdas, helicity, "trailing")


if __name__ == "__main__":
    main(sys.argv[1:])
