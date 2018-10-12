import ROOT
from ROOT import TFile, TTree, TCanvas, TGraph, TMultiGraph, TGraphErrors, TLegend, TChain
import CMS_lumi, tdrstyle
import subprocess # to execute shell command
ROOT.gROOT.SetBatch(ROOT.kTRUE)
 
# CMS style
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()
 

# GET limits from root file
def getLimits(file_name):

    f = TFile(file_name, "OPEN")
    tree = TChain()
    tree.Add(file_name + "/limit")
 
    limits = []
    tot = 0.0
    num = 0
    for ev in tree:
        tot += tree.GetLeaf("limit").GetValue()
	num += 1
    limits.append(tot/num)

    return limits

 
# PLOT upper limits
def plotUpperLimits():
 
    lambdas = [4000, 5000, 6000, 7000, 8000, 9000, 10000]
    N = len(lambdas)
    #yellow = TGraph(2*N)    # yellow band
    #green = TGraph(2*N)     # green band
    #median = TGraph(N)      # median line
 
    Mmin = [1200 + i*100 for i in range(25)]
    graphs = []
    for i in range(N):
        thislam = TGraph(len(Mmin))
        thislimit = []
	for mm in range(len(Mmin)):
        	file_name = "./dataCards/ee_singlebin/higgsCombine%d.Significance.mH%d.123456.root"%(Mmin[mm], lambdas[i])
        	limit = getLimits(file_name)
		thislam.SetPoint(mm, Mmin[mm], limit[0])
		thislam.SetLineColor(i+2)
                thislam.SetLineWidth(2)
                thislimit.append(limit[0])
        graphs.append(thislam.Clone())
        print "this minimum mass cut is %d"%Mmin[mm]
	print thislimit

        #yellow.SetPoint(    i,    values[i], limit[4] ) # + 2 sigma
        #green.SetPoint(     i,    values[i], limit[3] ) # + 1 sigma
        #median.SetPoint(    i,    labels[i], limit[0] ) # median
        #green.SetPoint(  2*N-1-i, values[i], limit[1] ) # - 1 sigma
        #yellow.SetPoint( 2*N-1-i, values[i], limit[0] ) # - 2 sigma
 
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
    frame = c.DrawFrame(1000,0.18,3500, 0.5)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    frame.GetYaxis().SetTitle("Significance")
    frame.GetXaxis().SetTitle("M_{min} [GeV]")
    frame.SetMinimum(0)
    #frame.SetMaximum(max(up2s)*1.05)
    #frame.GetXaxis().SetLimits(min(values),max(values))
    
    for gf in graphs:
        gf.Draw('Lsame')

    '''
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
    median.Draw('Lsame')'''
 
    CMS_lumi.CMS_lumi(c,13,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')
 
    x1 = 0.15
    x2 = x1 + 0.24
    y2 = 0.46
    y1 = 0.20
    legend = TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    for i in range(N):
        legend.AddEntry(graphs[i], "#Lambda = %d"%(1000*(i+4)), 'l')
    #legend.AddEntry(median, "Asymptotic CL_{s} expected",'L')
    #legend.AddEntry(green, "#pm 1 std. deviation",'f')
    #legend.AddEntry(green, "Asymptotic CL_{s} #pm 1 std. deviation",'f')
    #legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    #legend.AddEntry(green, "Asymptotic CL_{s} #pm 2 std. deviation",'f')
    legend.Draw()
 
    print " "
    c.SaveAs("CombineSamplePlot.png")
    c.Close()
 

# MAIN
def main():
 
    plotUpperLimits()
 
 
if __name__ == '__main__':
    main()
