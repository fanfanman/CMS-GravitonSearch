import ROOT
from ROOT import TFile, TTree, TCanvas, TGraph, TMultiGraph, TGraphErrors, TLegend, TPaveText
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


# get limit from crossing mu=1
# for each TGraph
def getCross(graph):
    
    for j in range(6):
        i = j + 4
        if graph.Eval(i) < 1.0 and graph.Eval(i+1) >1.0:
            x1 = i
            x2 = i+1
            y1 = graph.Eval(i)
            y2 = graph.Eval(i+1)
            a = (y2-y1)*1.0/(x2-x1)
            b = y2 - a * x2
            return (1-b)/a

 
def compareMethod(model, lambdas, helicity):

    N = len(lambdas)
    median0 = TGraph(N) # single bin counting
    median1 = TGraph(N) # linear bin, bw = 400

    for i in range(N):
        f0 = "./%sdataCards/ee_limit_multibin_paper/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, lambdas[i])
        f1 = "./%sdataCards/ee_limit_multibin_paper/higgsCombineTest.BayesianSimple.mH%d.123456.root"%(model, lambdas[i])
        limit0 = getLimits(f0)
        limit1 = getLimits(f1)
        if model == "ADD":
            median0.SetPoint(i, lambdas[i]/1000, limit0[2])
            median1.SetPoint(i, lambdas[i]/1000, limit1[2])
        else:
            median0.SetPoint(i, lambdas[i], limit0[2])
            median1.SetPoint(i, lambdas[i], limit1[2]) # median
        print "Lambda = %d, Median = %f"%(lambdas[i], limit0[2])
        print "Lambda = %d, Median = %f"%(lambdas[i], limit1[2])

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
    frame.GetYaxis().SetTitle("95% upper limit on #sigma / #sigma_{SM}")
    if model == "ADD": frame.GetXaxis().SetTitle("#Lambda_{T} [GWM]")
    else: frame.GetXaxis().SetTitle("#Lambda [CI]")
    frame.SetMinimum(0)

    median0.SetLineColor(1)
    median0.SetLineWidth(2)
    median0.SetLineStyle(2)
    median0.Draw('Lsame') # paper AS

    median1.SetLineColor(2)
    median1.SetLineWidth(2)
    median1.SetLineStyle(2)
    median1.Draw('Lsame') # paper BS

    CMS_lumi.CMS_lumi(c,13,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')

    x1 = 0.15
    x2 = x1 + 0.33
    y2 = 0.84
    y1 = 0.76
    legend = TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    #legend.SetHeader("mean expected limit of %s"%model)
    legend.AddEntry(median0, "linear bw=400, AsymptoticLimits", 'L')
    legend.AddEntry(median1, "linear bw=400, BayesianSimple", "L")
    legend.Draw()

    # Here print out the limits for a graph
    n0 = getCross(median0)
    n1 = getCross(median1)
    print n0, n1

    c.SaveAs("%slimits/%sLimit_ee_MultibinCompareMethod.png"%(model, model))
    c.Close()


# PLOT upper limits
def compareBinning(model, lambdas, helicity):
 
    N = len(lambdas)
    median0 = TGraph(N) # single bin counting
    median1 = TGraph(N) # linear bin, bw = 400
    median2 = TGraph(N) # geometric bin, bw = 100, 200, 400...
    median3 = TGraph(N) # linear bin, bw = 1000
    median4 = TGraph(N) # linear bin, bw = 200
    median5 = TGraph(N) # linear bin, bw = 100
    
    for i in range(N):
        f0 = "./%sdataCards/ee_limit_min1800/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, lambdas[i])
        f1 = "./%sdataCards/ee_limit_multibin_paper/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, lambdas[i])
        f2 = "./%sdataCards/ee_limit_multibin_geo/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, lambdas[i])
        f3 = "./%sdataCards/ee_limit_multibin_bw1000/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, lambdas[i])
        f4 = "./%sdataCards/ee_limit_multibin_bw200/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, lambdas[i])
        f5 = "./%sdataCards/ee_limit_multibin_bw100/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, lambdas[i])
        limit0 = getLimits(f0)
        limit1 = getLimits(f1)
        limit2 = getLimits(f2)
        limit3 = getLimits(f3)
        limit4 = getLimits(f4)
        limit5 = getLimits(f5)
        if model == "ADD": 
            median0.SetPoint(i, lambdas[i]/1000, limit0[2])
            median1.SetPoint(i, lambdas[i]/1000, limit1[2])
            median2.SetPoint(i, lambdas[i]/1000, limit2[2])
            median3.SetPoint(i, lambdas[i]/1000, limit3[2])
            median4.SetPoint(i, lambdas[i]/1000, limit4[2])
            median5.SetPoint(i, lambdas[i]/1000, limit5[2])
        else: 
            median0.SetPoint(i, lambdas[i], limit0[2])
            median1.SetPoint(i, lambdas[i], limit1[2]) # median
            median2.SetPoint(i, lambdas[i], limit2[2])
            median3.SetPoint(i, lambdas[i], limit3[2])
            median4.SetPoint(i, lambdas[i], limit4[2])
            median5.SetPoint(i, lambdas[i], limit5[2])
        print "Lambda = %d, Median = %f"%(lambdas[i], limit0[2])
        print "Lambda = %d, Median = %f"%(lambdas[i], limit1[2])
        print "Lambda = %d, Median = %f"%(lambdas[i], limit2[2])
        print "Lambda = %d, Median = %f"%(lambdas[i], limit3[2])
        print "Lambda = %d, Median = %f"%(lambdas[i], limit4[2])
        print "Lambda = %d, Median = %f"%(lambdas[i], limit5[2])

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
    frame.GetYaxis().SetTitle("95% upper limit on #sigma / #sigma_{SM}")
    if model == "ADD": frame.GetXaxis().SetTitle("#Lambda_{T} [GWM]")
    else: frame.GetXaxis().SetTitle("#Lambda [CI]")
    frame.SetMinimum(0)
 
    '''yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')
 
    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')'''
 
    median0.SetLineColor(1)
    median0.SetLineWidth(2)
    median0.SetLineStyle(2)
    median0.Draw('Lsame') # single bin counting

    median1.SetLineColor(2)
    median1.SetLineWidth(2)
    median1.SetLineStyle(2)
    median1.Draw('Lsame') # paper

    median2.SetLineColor(3)
    median2.SetLineWidth(2)
    median2.SetLineStyle(2)
    median2.Draw('Lsame') # geometric

    median3.SetLineColor(4)
    median3.SetLineWidth(2)
    median3.SetLineStyle(2)
    median3.Draw('Lsame') # bw1000
 
    median4.SetLineColor(6)
    median4.SetLineWidth(2)
    median4.SetLineStyle(2)
    median4.Draw('Lsame') # bw200

    median5.SetLineColor(7)
    median5.SetLineWidth(2)
    median5.SetLineStyle(2)
    median5.Draw('Lsame') # bw100

    CMS_lumi.CMS_lumi(c,13,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')
 
    x1 = 0.15
    x2 = x1 + 0.43
    y2 = 0.84
    y1 = 0.56
    legend = TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.SetHeader("mean expected limit of %s"%model)
    #legend.AddEntry(median1, "paper's binning", 'L')
    legend.AddEntry(median2, "geometric binning", 'L')
    legend.AddEntry(median0, "linear bw=8200 (singlebin)", "L")
    legend.AddEntry(median3, "linear bw=1000", 'L')
    legend.AddEntry(median1, "linear bw=400 (paper)", "L")
    legend.AddEntry(median4, "linear bw=200", "L")
    legend.AddEntry(median5, "linear bw=100", "L")
    legend.Draw()

    # Here print out the limits for a graph
    n0 = getCross(median0)
    n1 = getCross(median1)
    n2 = getCross(median2)
    n3 = getCross(median3)
    n4 = getCross(median4)
    n5 = getCross(median5)
    print n2, n0, n3, n1, n4, n5

    c.SaveAs("%slimits/%sLimit_ee_MultibinCompareBin.png"%(model, model))
    c.Close()

 
# MAIN
def main(argv):

    model = argv[0]

    if model == "ADD":
        lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
        # heli = ["_Con", "_Des"]
	heli = [""]
    else:
        lambdas = [16, 22, 28, 32, 40]
        heli = ["_ConLL", "_ConLR", "_ConRR", "_DesLL", "_DesLR", "_DesRR"]
    

    for helicity in heli:
        compareBinning(model, lambdas, helicity)
        #compareMethod(model, lambdas, helicity)
 
 
if __name__ == '__main__':
    main(sys.argv[1:])
