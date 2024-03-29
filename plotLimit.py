import ROOT
from ROOT import TFile, TTree, TCanvas, TGraph, TMultiGraph, TGraphErrors, TLegend
import CMS_lumi, tdrstyle
import subprocess # to execute shell command
import sys
ROOT.gROOT.SetBatch(ROOT.kTRUE)
 
# CMS style
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()
 
# scale by xsec or not
XSec = False
 
# GET limits from root file
def getLimits(file_name):
 
    file = TFile(file_name)
    tree = file.Get("limit")
 
    limits = [ ]
    for quantile in tree:
        limits.append(tree.limit)
        # print ">>>   %.2f" % limits[-1]
 
    return limits[:6]

 
# PLOT upper limits
def plotUpperLimits(model, lambdas, helicity, Mmin):
 
    N = len(lambdas)
    yellow = TGraph(2*N)    # yellow band
    green = TGraph(2*N)     # green band
    median = TGraph(N)      # median line
 
    up2s = [ ]
    xseclist = [1.0]*N
    
    for i in range(N):
        file_name = "./%sshapeCards/ee_limit_min%d%s/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, Mmin, helicity, lambdas[i])
        limit = getLimits(file_name)
        up2s.append(limit[4])
        if model == "ADD":
            yellow.SetPoint(    i,    lambdas[i]/1000, limit[4] * xseclist[i]) # + 2 sigma
            green.SetPoint(     i,    lambdas[i]/1000, limit[3] * xseclist[i]) # + 1 sigma
            median.SetPoint(    i,    lambdas[i]/1000, limit[2] * xseclist[i]) # median
            green.SetPoint(  2*N-1-i, lambdas[i]/1000, limit[1] * xseclist[i]) # - 1 sigma
            yellow.SetPoint( 2*N-1-i, lambdas[i]/1000, limit[0] * xseclist[i]) # - 2 sigma
        else:
            yellow.SetPoint(    i,    lambdas[i], limit[4] * xseclist[i]) # + 2 sigma
            green.SetPoint(     i,    lambdas[i], limit[3] * xseclist[i]) # + 1 sigma
            median.SetPoint(    i,    lambdas[i], limit[2] * xseclist[i]) # median
            green.SetPoint(  2*N-1-i, lambdas[i], limit[1] * xseclist[i]) # - 1 sigma
            yellow.SetPoint( 2*N-1-i, lambdas[i], limit[0] * xseclist[i]) # - 2 sigma
        print "Lambda = %d, Median = %f"%(lambdas[i], limit[2])

    W = 800
    H  = 600
    T = 0.08*H
    B = 0.12*H
    L = 0.12*W
    R = 0.04*W
    c = TCanvas("c","c",100,100,W,H)
    c.SetFillColor(0)
    c.SetBorderMode(0)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.SetLeftMargin( L/W )
    c.SetRightMargin( R/W )
    c.SetTopMargin( T/H )
    c.SetBottomMargin( B/H )
    c.SetTickx(0)
    c.SetTicky(0)
    c.SetGrid()
    c.cd()
    if model == "ADD": frame = c.DrawFrame(4, 0.01, 10, 10)
    else: frame = c.DrawFrame(16, 0.1, 40, 8)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    #frame.GetYaxis().SetTitle("95% upper limit on #sigma / #sigma_{}")
    if model == "ADD": 
        frame.GetYaxis().SetTitle("95% CL limit on #sigma / #sigma_{ADD}")
        frame.GetXaxis().SetTitle("#Lambda_{T} [ADD]")
    else: 
        frame.GetYaxis().SetTitle("95% CL limit on #sigma / #sigma_{CI}")
        frame.GetXaxis().SetTitle("#Lambda [CI]")
    frame.SetMinimum(0)
    #frame.SetMaximum(max(up2s)*1.05)
    #frame.GetXaxis().SetLimits(min(values),max(values))
 
    yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')
 
    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')
 
    median.SetLineColor(1)
    median.SetLineWidth(2)
    median.SetLineStyle(2)
    median.Draw('Lsame')
 
    CMS_lumi.CMS_lumi(c,13,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')
 
    x1 = 0.15
    x2 = x1 + 0.24
    y2 = 0.76
    y1 = 0.60
    legend = TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.AddEntry(median, "Asymptotic CL_{s} expected %s%s"%(model, helicity),'L')
    legend.AddEntry(green, "#pm 1 std. deviation",'f')
    legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    legend.Draw()

    c.SaveAs("%slimits/%sLimit_ee_ShapeMin%d%s_201678.png"%(model, model, Mmin, helicity))
    c.Close()

 
# MAIN
def main(argv):

    model = argv[0]
    Mmin = int(argv[1])

    if model == "ADD":
        lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
        # heli = ["_Con", "_Des"]
	heli = [""]
    else:
        lambdas = [16, 22, 28, 32, 40]
        heli = ["_ConLL", "_ConLR", "_ConRR", "_DesLL", "_DesLR", "_DesRR"]

    for helicity in heli:
        plotUpperLimits(model, lambdas, helicity, Mmin)
 
 
if __name__ == '__main__':
    main(sys.argv[1:])
