import ROOT
#from ROOT import TFile, TTree, TCanvas, TGraph, TMultiGraph, TGraphErrors, TLegend, TPad
from ROOT import *
import CMS_lumi, tdrstyle, sys
import ratios
import subprocess # to execute shell command
from setTDRStyle import setTDRStyle
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


def getLimitsMCMC(file_name):

    file = TFile(file_name)
    tree = file.Get("limit")

    limits = []
    for quantile in tree:
        if tree.limit > 0 and tree.limit < 100:
            limits.append(tree.limit)
        # print ">>>   %.2f" % limits[-1]

    return sum(limits)*1.0/len(limits)



# calculate limit +- 1,2 sigma
def getCross(Mmin, model, lambdas, helicity, tag):

    limits = []

    for lambdaT in lambdas:
        templimit = getLimits("./%s%sCards/ee_limit_min%d%s/higgsCombineTest.AsymptoticLimits.mH%d.root"%(model, tag, Mmin, helicity, lambdaT))
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


def getCrossMCMC(Mmin, model, lambdas, helicity, tag):

    limits = [0.0]
    if model == "ADD": thislambdas = [5000 + i * 1000 for i in range(6)]
    else: thislambdas = lambdas

    for lambdaT in thislambdas:
        templimit = getLimitsMCMC("./%s%sCards/ee_limit_min%d%s/higgsCombine%d.MarkovChainMC.mH%d.root"%(model, tag, Mmin, helicity, lambdaT, lambdaT))
        limits.append(templimit)
    #print limits

    if model == "ADD": lambdas = [i / 1000 for i in lambdas]
    cross = 0.0

    if limits[0] >= 1.0 and limits[1] >= 1.0:
        y2 = limits[1]
        y1 = limits[0]
        x2 = lambdas[1]
        x1 = lambdas[0]
        a = (y2 - y1)*1.0 / (x2 - x1)
        b = y2 - a * x2
        cross = (1.0 - b) / a
        return cross

    # y1 = a x1 + b, y2 = a x2 + b
    for k in range(len(lambdas)-1):
        if limits[k] <= 1.0 and limits[k+1] >= 1.0:
            y2 = limits[k+1]
            y1 = limits[k]
            x2 = lambdas[k+1]
            x1 = lambdas[k]
            a = (y2 - y1)*1.0 / (x2 - x1)
            b = y2 - a * x2
            cross = (1.0 - b) / a
            return cross

    y2 = limits[-1]
    y1 = limits[-2]
    x2 = lambdas[-1]
    x1 = lambdas[-2]
    a = (y2 - y1)*1.0 / (x2 - x1)
    b = y2 - a * x2
    cross = (1.0 - b) / a
    return cross



def plotLimitSingle(model, lambdas, helicity, Mmin): 

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
    legend.AddEntry(median, "Shape-based CL_{s} expected %s%s"%(model, helicity),'L')
    legend.AddEntry(green, "#pm 1 std. deviation",'f')
    legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    legend.Draw()

    if XSec:
        c.SaveAs("%slimits/%sLimit_ee_XsecVSLambdaTMin%d%s.png"%(model, model, Mmin, helicity))
    else:
        c.SaveAs("%slimits/%sLimit_ee_ShapeMin%d%s.png"%(model, model, Mmin, helicity))
    c.Close()



# plot limit vs Mmin
def plotLimitsASShape(model, lambdas, helicity):

    Mmin = [600 + i * 100 for i in range(27)]
    if model == "CI": Mmin = [800 + i * 100 for i in range(25)]
    N = len(Mmin)
    green = TGraph(N)
    yellow = TGraph(N)
    shape = TGraph(N)      # median of shape analysis
    count = TGraph(N)	   # median of counting experiment
    
    for i in range(N):
        limit = getCross(Mmin[i], model, lambdas, helicity, "data")
        print Mmin[i], limit[0], limit[1], limit[2], limit[3], limit[4]
        yellow.SetPoint(    i,    Mmin[i], limit[4]) # + 2 sigma
        green.SetPoint(     i,    Mmin[i], limit[3]) # + 1 sigma
        count.SetPoint(    i,    Mmin[i], limit[2]) # median
        green.SetPoint(  2*N-1-i, Mmin[i], limit[1]) # - 1 sigma
        yellow.SetPoint( 2*N-1-i, Mmin[i], limit[0]) # - 2 sigma
        
    for i in range(N):
        limitmcmc = getCross(Mmin[i], model, lambdas, helicity, "shape")
        #limiterr = getCross(Mmin[i], model, lambdas, helicity, True)[2]
        #limitmcmcerr = getCrossMCMC(Mmin[i], model, lambdas, helicity, True)
        print Mmin[i], limitmcmc
        shape.SetPoint(i, Mmin[i], limitmcmc[2])
        #err_median.SetPoint(i, Mmin[i], limiterr)
        #err_mcmc.SetPoint(i, Mmin[i], limitmcmcerr)

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
        frame = c.DrawFrame(Mmin[0], 2.8, Mmin[-1], 8)
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
 
    '''yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')
 
    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')'''
 
    count.SetLineColor(1)
    count.SetLineWidth(2)
    count.SetLineStyle(2)
    count.Draw('Lsame')
 
    shape.SetLineColor(2)
    shape.SetLineWidth(2)
    shape.SetLineStyle(2)
    shape.Draw("Lsame")

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
    legend.AddEntry(count, "single-bin counting experiment",'L')
    #legend.AddEntry(green, "#pm 1 std. deviation",'f')
    #legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    legend.AddEntry(shape, "shape fitting experiment",'L')
    legend.Draw()

    c.SaveAs("%slimits/%sLimit_ee_LimitVsMmin%s_VSShape.png"%(model, model, helicity))
    c.Close()



# plot limit vs Mmin
def plotLimitMCMC(model, lambdas, helicity):

    Mmin = [600 + i * 100 for i in range(27)]
    if model == "CI": Mmin = [800 + i * 100 for i in range(25)]
    N = len(Mmin)
    green = TGraph(N)
    yellow = TGraph(N)
    shape = TGraph(N)      # median of shape analysis
    count = TGraph(N)      # median of counting experiment

    for i in range(N):
        limitmcmc = getCrossMCMC(Mmin[i], model, lambdas, helicity, "shape")
        #limiterr = getCross(Mmin[i], model, lambdas, helicity, True)[2]
        #limitmcmcerr = getCrossMCMC(Mmin[i], model, lambdas, helicity, True)
        print Mmin[i], limitmcmc
        shape.SetPoint(i, Mmin[i], limitmcmc)
        #err_median.SetPoint(i, Mmin[i], limiterr)
        #err_mcmc.SetPoint(i, Mmin[i], limitmcmcerr)

    for i in range(N):
        limit = getCross(Mmin[i], model, lambdas, helicity, "shape")
        count.SetPoint(i, Mmin[i], limit[2])
        print Mmin[i], limit[2]
 
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
        frame = c.DrawFrame(Mmin[0], 2.8, Mmin[-1], 8)
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

    '''yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')

    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')'''

    count.SetLineColor(1)
    count.SetLineWidth(2)
    count.SetLineStyle(2)
    count.Draw("Lsame")

    shape.SetLineColor(2)
    shape.SetLineWidth(2)
    shape.SetLineStyle(2)
    shape.Draw("Lsame")

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
    legend.AddEntry(count, "shape analysis, Asymptotic",'L')
    #legend.AddEntry(green, "#pm 1 std. deviation",'f')
    #legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    legend.AddEntry(shape, "shape analysis, MCMC",'L')
    legend.Draw()

    c.SaveAs("%slimits/%sLimit_ee_LimitVsMmin%s_VSShapeMCMC.png"%(model, model, helicity))
    c.Close()



# MAIN
def main(argv):
    
    model = argv[0]
    Mmin = int(argv[1])

    if model == "ADD":
        lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
        heli = [""]
    else:
        lambdas = [16, 22, 28, 32, 40]
        heli = ["_ConLL", "_ConLR", "_ConRR"] #, "_DesLL", "_DesLR", "_DesRR"]

    for helicity in heli:
        #plotLimitsASShape(model, lambdas, helicity)
        #plotLimitSingle(model, lambdas, helicity, Mmin)
        plotLimitMCMC(model, lambdas, helicity)
 
if __name__ == '__main__':
    main(sys.argv[1:])
