import ROOT
from ROOT import TFile, TTree, TCanvas, TGraph, TMultiGraph, TGraphErrors, TLegend
import CMS_lumi, tdrstyle, sys
import subprocess # to execute shell command
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


# calculate limit +- 1,2 sigma
def getCross(Mmin, model, lambdas, helicity):
 
    limits = []
    for lambdaT in lambdas:
        templimit = getLimits("./%sdataCards/ee_limit_min%d%s/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, Mmin, helicity, lambdaT))
        limits.append(templimit)

    # limits = [lim4, lim5, lim6...]
    cross = [0.0]*5
    if model == "ADD":
        lambdas = [i/1000 for i in lambdas]

    for j in range(5):
        crossed = False
        if limits[0][j] >= 1.0 and limits[1][j] >= 1.0:
            y2 = limits[1][j]
            y1 = limits[0][j]
            x2 = lambdas[1]
            x1 = lambdas[0]
            a = (y2 - y1)*1.0 / (x2 - x1)
            b = y2 - a * x2
            cross[j] = (1.0 - b) / a
            crossed = True
            continue

        #crossed = False
        # y1 = a x1 + b, y2 = a x2 + b
        for k in range(len(lambdas)-1):
            if not crossed and limits[k][j] <= 1.0 and limits[k+1][j] >= 1.0:
                y2 = limits[k+1][j]
                y1 = limits[k][j]
                x2 = lambdas[k+1]
                x1 = lambdas[k]
                a = (y2 - y1)*1.0 / (x2 - x1)
                b = y2 - a * x2
                cross[j] = (1.0 - b) / a
                crossed = True
                continue
        if not crossed:
            y2 = limits[-1][j]
            y1 = limits[-2][j]
            x2 = lambdas[-1]
            x1 = lambdas[-2]
            a = (y2 - y1)*1.0 / (x2 - x1)
            b = y2 - a * x2
            cross[j] = (1.0 - b) / a

    return cross


# plot limit vs Mmin
def plotLimits(model, lambdas, helicity):

    Mmin = [400 + i * 100 for i in range(29)]
    if model == "CI": Mmin = [800 + i * 100 for i in range(25)]

    N = len(Mmin)
    yellow = TGraph(2*N)    # yellow band
    green = TGraph(2*N)     # green band
    median = TGraph(N)      # median
    
    for i in range(N):
        limit = getCross(Mmin[i], model, lambdas, helicity)
        print Mmin[i], limit[0], limit[1], limit[2], limit[3], limit[4]
        yellow.SetPoint(    i,    Mmin[i], limit[4]) # + 2 sigma
        green.SetPoint(     i,    Mmin[i], limit[3]) # + 1 sigma
        median.SetPoint(    i,    Mmin[i], limit[2]) # median
        green.SetPoint(  2*N-1-i, Mmin[i], limit[1]) # - 1 sigma
        yellow.SetPoint( 2*N-1-i, Mmin[i], limit[0]) # - 2 sigma
    
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
    if model == "ADD":
        frame = c.DrawFrame(Mmin[0], 2, Mmin[-1], 10)
    else:
        frame = c.DrawFrame(Mmin[0], 2, Mmin[-1], 50)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    frame.GetYaxis().SetTitle("95% limit of #Lambda_{T}")
    if model == "CI": frame.GetYaxis().SetTitle("95% limit of #Lambda")
    frame.GetXaxis().SetTitle("M_{#font[12]{l}#font[12]{l}}^{min} (GeV)")
    #frame.SetMinimum(0)
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
 
    x1 = 0.42
    x2 = x1 + 0.24
    y2 = 0.86
    y1 = 0.70
    legend = TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.AddEntry(median, "Asymptotic CL_{s} expected of %s%s"%(model, helicity),'L')
    legend.AddEntry(green, "#pm 1 std. deviation",'f')
    legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    legend.Draw()

    c.SaveAs("%slimits/%sLimit_ee_LimitVsMmin%s.png"%(model, model, helicity))
    c.Close()

 
# MAIN
def main(argv):
    
    model = argv[0]
    if model == "ADD":
        lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
        heli = [""]
    else:
        lambdas = [16, 22, 28, 32, 40]
        heli = ["_ConLL", "_ConLR", "_ConRR"] #, "_DesLL", "_DesLR", "_DesRR"]

    for helicity in heli:
        plotLimits(model, lambdas, helicity)
 
if __name__ == '__main__':
    main(sys.argv[1:])
