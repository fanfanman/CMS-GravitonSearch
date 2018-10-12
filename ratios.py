#=======================================================
# Project: LocalAnalysis
#			  SUSY Same Sign Dilepton Analysis
#
# File: ratios.py
#
# Author: Daniel Sprenger
#		 daniel.sprenger@cern.ch
#=======================================================

from tools import myColors
import ROOT

from array import array
import math
from messageLogger import messageLogger as log


class Ratio:
	def __init__(self, numerator, denominator, numeratorSquaredError, denominatorSquaredError, xPos, width):
		self.numerators = [numerator]
		self.denominators = [denominator]
		self.numeratorSquaredErrors = [numeratorSquaredError]
		self.denominatorSquaredErrors = [denominatorSquaredError]
		self.xPos = [xPos]
		self.width = width
		self.chi2 = 0.
		self.nDF = 0

	@property
	def isValid(self):
		return (self.sumDenominator > 0)

	@property
	def ratio(self):
		value = -1.0
		if (self.isValid):
			value = self.sumNumerator / self.sumDenominator
		return value

	@property
	def sumNumerator(self):
		value = 0.0
		for num in self.numerators:
			value += num
		return value

	@property
	def sumDenominator(self):
		value = 0.0
		for den in self.denominators:
			value += den
		return value

	@property
	def sumNumeratorSquaredErrors(self):
		value = 0.0
		for numError in self.numeratorSquaredErrors:
			value += numError
		return value

	@property
	def sumDenominatorSquaredErrors(self):
		value = 0.0
		for denError in self.denominatorSquaredErrors:
			value += denError
		return value

	@property
	def errorX(self):
		return 0.5 * self.width

	@property
	def errorY(self):
		value = 0.0
		if (self.isValid and self.sumNumerator > 0):
			value = self.ratio * math.sqrt(self.sumNumeratorSquaredErrors / math.pow(self.sumNumerator, 2.0) + self.sumDenominatorSquaredErrors / math.pow(self.sumDenominator, 2.0))
		return value

	@property
	def xCenter(self):
		value = 0.0
		for x in self.xPos:
			value += x / len(self.xPos)
		return value

	def isFullEnough(self, rebinErrorBoundary):
		#if (self.sumNumerator > 0):
		#	log.logDebug("Rel Eror: %f" % (math.sqrt(self.sumNumeratorSquaredErrors) / self.sumNumerator))
		return (self.sumNumerator > 0 and math.sqrt(self.sumNumeratorSquaredErrors) / self.sumNumerator <= rebinErrorBoundary)

	def addRatio(self, ratio):
		self.numerators.extend(ratio.numerators)
		self.denominators.extend(ratio.denominators)
		self.numeratorSquaredErrors.extend(ratio.numeratorSquaredErrors)
		self.denominatorSquaredErrors.extend(ratio.denominatorSquaredErrors)
		self.xPos.extend(ratio.xPos)
		self.width += ratio.width


class RatioGraph:
	def __init__(self, numerator, denominator, xMin, xMax,title, yMin, yMax,ndivisions,color,adaptiveBinning,labelSize=None):
		self.denominator = denominator
		self.numerator = numerator
		self.xMin = xMin
		self.xMax = xMax
		self.errors = []
		self.title = title
		self.yMin = yMin
		self.yMax = yMax
		self.ndivisions = ndivisions
		self.color=color
		self.adaptiveBinning = adaptiveBinning
		self.labelSize=labelSize
		self.binMerging = []
		return

	def addErrorBySize(self, name, size, color=None, fillStyle=None, add=True):
		error = RatioError(name, self.xMin, self.xMax,self.binMerging, size=size, add=add)
		if (color != None):
			error.color = color
		if (fillStyle != None):
			error.fillStyle = fillStyle
		self.errors.append(error)

	def addErrorByHistograms(self, name, denominatorUp, denominatorDown, color=None, fillStyle=None,add= False):
		error = RatioError(name, self.xMin, self.xMax,self.binMerging, denominator=self.denominator, denominatorUp=denominatorUp, denominatorDown=denominatorDown,add=add)
		if (color != None):
			error.color = color
		if (fillStyle != None):
			error.fillStyle = fillStyle
		else:
			error.fillStyle = 1001
		self.errors.append(error)

	def getGraph(self):
		ratios = []

		tempRatio = None
		for iBin in range(1, 1 + self.numerator.GetNbinsX()):
			num = self.numerator.GetBinContent(iBin)
			numError = self.numerator.GetBinError(iBin)
			den = self.denominator.GetBinContent(iBin)
			denError = self.denominator.GetBinError(iBin)
			x = self.numerator.GetBinCenter(iBin)
			width = self.numerator.GetBinWidth(iBin)
			
			#~ print "DEBUG RATIO: " 
			#~ print iBin
			#~ print num 
			#~ print numError
			#~ print den
			#~ print denError

			# assure that bin is in view range
			# ignore empty starting bins
			if (self.xMin < x and x < self.xMax
					and not (len(ratios) == 0 and tempRatio == None and den == 0)):

				#log.logDebug("num: %f +- %f" % (num, numError))
				#log.logDebug("den: %f +- %f" % (den, denError))

				if (tempRatio != None):
					ratio = Ratio(num, den, math.pow(numError, 2.0), math.pow(denError, 2.0), x, width)
					tempRatio.addRatio(ratio)
				else:
					tempRatio = Ratio(num, den, math.pow(numError, 2.0), math.pow(denError, 2.0), x, width)
					
				#~ if (self.adaptiveBinning):
					#~ print "test"
					#~ if (tempRatio.isFullEnough()):
						#~ print "test2"
						#~ ratios.append(tempRatio)
						#~ tempratio = None
				#~ else:
					#~ ratios.append(tempRatio)
					#~ tempratio = None
				if (tempRatio.isFullEnough(self.adaptiveBinning)):
					 
					self.binMerging.append(iBin)
					ratios.append(tempRatio)
					tempRatio = None

				
				

						

		if (tempRatio != None):
			ratios.append(tempRatio)

		xs = []
		ys = []
		yErrors = []
		widths = []
		for ratio in ratios:
			xs.append(ratio.xCenter)
			ys.append(ratio.ratio)
			yErrors.append(ratio.errorY)
			widths.append(ratio.errorX)


		#~ log.logDebug("xs = %s" % xs)
		#~ log.logDebug("ys = %s" % ys)
		#~ log.logDebug("yErrors = %s" % yErrors)
		#~ log.logDebug("widths = %s" % widths)

		graph = ROOT.TGraphAsymmErrors(len(xs), array("d", xs), array("d", ys), array("d", widths), array("d", widths), array("d", yErrors), array("d", yErrors))
		graph.SetLineColor(self.color)
		graph.SetMarkerColor(self.color)
		self.chi2 =  sum((y-1)**2 * (1./yErr if yErr != 0. else 0.)**2 for y, yErr in zip(ys, yErrors))
		self.nDF = len(ys)-1
		#graph = ROOT.TGraphAsymmErrors(self.numerator,self.denominator)
		
		return graph

	def getErrorGraphs(self):
		numErrorGraphs=0
		totalConstantUncertainty = 0
		errorGraphs = []
		for iError, error in enumerate(self.errors):

			if (error.size != None):
				if (error.add):
					log.logInfo("Quadractically adding error '%s' with size %f" % (error.name, error.size))
					totalConstantUncertainty = (totalConstantUncertainty**2+error.size**2)**0.5
					#~ xCenter = 0.5 * (error.xMin + error.xMax)
					#~ xWidth = 0.5 * (error.xMax - error.xMin)
					#~ graph = ROOT.TGraphErrors(1, array("d", [xCenter]), array("d", [1.0]), array("d", [xWidth]), array("d", [error.size]))
					#~ graph.SetFillColor(error.color)
					#~ errorGraphsToAdd.Add(graph)					
				else:

					log.logInfo("Adding error '%s' with size %f" % (error.name, error.size))
					xCenter = 0.5 * (error.xMin + error.xMax)
					xWidth = 0.5 * (error.xMax - error.xMin)
					graph = ROOT.TGraphErrors(1, array("d", [xCenter]), array("d", [1.0]), array("d", [xWidth]), array("d", [error.size]))
					graph.SetFillColor(error.color)
					graph.SetFillStyle(error.fillStyle)
					errorGraphs.append(graph)
			elif (error.hasHistograms):
				log.logInfo("Adding error '%s' given as histograms" % (error.name))

				errorsUp = error.errorsUp
				errorsDown = error.errorsDown

				xs = []
				ys = []
				widths = []
				upErrors = []
				downErrors = []
				for (errorUp, errorDown) in zip(errorsUp, errorsDown):
					if (errorUp.ratio >= 0.0 and errorDown.ratio >= 0.0):
						xs.append(errorUp.xCenter)
						ys.append(1.0)
						widths.append(errorUp.errorX)

						if (errorUp.ratio > 1.0):
							if (errorDown.ratio > 1.0):
								upErrors.append(max(errorUp.ratio - 1.0, errorDown.ratio - 1.0))
								downErrors.append(0.0)
							else:
								upErrors.append(errorUp.ratio - 1.0)
								downErrors.append(1.0 - errorDown.ratio)
						else:
							if (errorDown.ratio > 1.0):
								upErrors.append(errorDown.ratio - 1.0)
								downErrors.append(1.0 - errorUp.ratio)
							else:
								upErrors.append(0.0)
								downErrors.append(max(1.0 - errorUp.ratio, 1.0 - errorDown.ratio))

				#~ if (iError + 1 < len(self.errors) and self.errors[iError + 1].add):

				if (iError -1 is not -1  ):
					#~ print iError
					#~ if (self.errors[iError + 1].size != None):
					log.logHighlighted("Found uncertainty to be added. Will do so, now.")
					#~ size = self.errors[iError -1].size
					#~ upErrors = [math.sqrt(prev ** 2 + errorGraphs[numErrorGraphs-1].GetErrorYhigh(index) ** 2 + totalConstantUncertainty**2) for index, prev in enumerate(upErrors)]
					#~ downErrors = [math.sqrt(prev ** 2 + errorGraphs[numErrorGraphs-1].GetErrorYlow(index) ** 2 + totalConstantUncertainty**2) for index, prev in enumerate(downErrors)]
					upErrors = [math.sqrt(prev ** 2 + errorGraphs[numErrorGraphs-1].GetErrorYhigh(index) ** 2 + totalConstantUncertainty**2) for index, prev in enumerate(upErrors)]
					downErrors = [math.sqrt(prev ** 2 + errorGraphs[numErrorGraphs-1].GetErrorYlow(index) ** 2 + totalConstantUncertainty**2) for index, prev in enumerate(downErrors)]
					#~ else:
						#~ log.logError("Uncertainty to be added does not have fixed size. Adding not implemented, yet.")

				graph = ROOT.TGraphAsymmErrors(len(xs), array("d", xs), array("d", ys), array("d", widths), array("d", widths), array("d", downErrors), array("d", upErrors))
				graph.SetFillColor(error.color)
				graph.SetFillStyle(error.fillStyle)
				errorGraphs.append(graph)
				#~ print downErrors
				#~ print upErrors
				numErrorGraphs = numErrorGraphs+1
		
		#~ num = errorGraphs[-1].Merge(errorGraphsToAdd)
		#~ print num
		return errorGraphs

	def draw(self, pad,redrawAxis,drawAsHist=False,addChi2=False,chi2Pos =0.8):
		pad.cd()

		# axis
		nBinsX = 20
		nBinsY = 10
		self.hAxis = ROOT.TH2F("hAxis", "", nBinsX, self.xMin, self.xMax, nBinsY, self.yMin, self.yMax)
		if redrawAxis:
			self.hAxis.Draw("AXIS")
		#~ self.hAxis.GetYaxis().SetNdivisions(10, 10, self.ndivisions)
		
		self.hAxis.GetYaxis().SetNdivisions(408)
		self.hAxis.SetTitleOffset(0.4, "Y")
		self.hAxis.SetTitleSize(0.15, "Y")
		self.hAxis.SetYTitle(self.title)
		self.hAxis.GetXaxis().SetLabelSize(0.0)
		self.hAxis.GetYaxis().SetLabelSize(0.15)

		if self.labelSize is None:
			self.hAxis.SetTitleSize(0.15, "Y")
		else:
			self.hAxis.SetTitleSize(self.labelSize, "Y")
		self.graph = self.getGraph()
		self.binMerging.append(-1)
		self.errorGraphs = self.getErrorGraphs()
		self.errorGraphs.reverse()
		for errorGraph in self.errorGraphs:
			errorGraph.Draw("SAME02")

		self.oneLine = ROOT.TLine(self.xMin, 1.0, self.xMax, 1.0)
		self.oneLine.SetLineStyle(2)
		self.oneLine.Draw()
		self.oneLine2 = ROOT.TLine(self.xMin, 0.5, self.xMax, 0.5)
		self.oneLine2.SetLineStyle(2)
		self.oneLine2.Draw()
		self.oneLine3 = ROOT.TLine(self.xMin, 1.5, self.xMax, 1.5)
		self.oneLine3.SetLineStyle(2)
		self.oneLine3.Draw()
		#~ if redrawAxis:
		#~ self.hAxis.Draw("SAMEAXIS")

		
		
		if drawAsHist:
			self.graph.SetLineWidth(2)
			self.graph.Draw("SAMEhist")
		else:
			self.graph.Draw("SAMEpZ")

		
		

		#~ if addChi2:
			#~ 
			#~ from ROOT import TLatex
			#~ latex= TLatex()
			#~ latex.SetNDC()
			#~ latex.SetTextSize(0.1)
			#~ latex.SetTextColor(self.color)
			#~ latex.DrawLatex(0.2,chi2Pos, "#chi^{2}/nDF = %.1f/%.1d"%(self.chi2, self.nDF))	


		pad.Update()


class RatioError:
	def __init__(self, name, xMin, xMax,binMerging, size=None, denominator=None, denominatorUp=None, denominatorDown=None, add=False):
		self.name = name

		self.denominator = denominator
		self.denominatorUp = denominatorUp
		self.denominatorDown = denominatorDown
		self.binMerging = binMerging
		self.size = size
		self.xMin = xMin
		self.xMax = xMax
		self.rebinErrorBoundary = 0.1

		self.add = add

		self.__ratiosUp__ = []
		self.__ratiosDown__ = []
		self.__errorsUp__ = None
		self.__errorsDown__ = None

		self.color = ROOT.kGreen
		self.fillStyle = 1001

	@property
	def errorsUp(self):
		if (self.__errorsUp__ == None):
			if (len(self.__ratiosUp__) == 0):
				self._calculateRatios()

			self.__errorsUp__ = []
			for ratio in self.__ratiosUp__:
				self.__errorsUp__.append(ratio)

		return self.__errorsUp__

	@property
	def errorsDown(self):
		if (self.__errorsDown__ == None):
			if (len(self.__ratiosDown__) == 0):
				self._calculateRatios()

			self.__errorsDown__ = []
			for ratio in self.__ratiosDown__:
				self.__errorsDown__.append(ratio)

		return self.__errorsDown__

	@property
	def hasHistograms(self):
		return (self.denominator != None and self.denominatorUp != None and self.denominatorDown != None)

	def _calculateRatios(self):
		if (self.hasHistograms):
			tempRatioUp = None
			tempRatioDown = None
			nBin = 0
			for iBin in range(1, 1 + self.denominator.GetNbinsX()):
				den = self.denominator.GetBinContent(iBin)
				denError = self.denominator.GetBinError(iBin)
				denUp = self.denominatorUp.GetBinContent(iBin)
				denUpError = self.denominatorUp.GetBinError(iBin)
				denDown = self.denominatorDown.GetBinContent(iBin)
				denDownError = self.denominatorDown.GetBinError(iBin)
				#~ log.logDebug("den: %f +- %f" % (den, denError))
				#~ log.logDebug("denup: %f +- %f" % (denUp, denUpError))
				#~ log.logDebug("dendown: %f +- %f" % (denDown, denDownError))

				x = self.denominator.GetBinCenter(iBin)
				width = self.denominator.GetBinWidth(iBin)

				# assure that bin is in view range
				if (self.xMin < x and x < self.xMax):
					ratioUp = Ratio(denUp, den, math.pow(denUpError, 2.0), math.pow(denError, 2.0), x, width)
					ratioDown = Ratio(denDown, den, math.pow(denDownError, 2.0), math.pow(denError, 2.0), x, width)

					#~ log.logInfo("ratioUp: %f, ratioDown: %f" % (ratioUp.ratio, ratioDown.ratio))

					if (tempRatioUp != None):
						tempRatioUp.addRatio(ratioUp)
						tempRatioDown.addRatio(ratioDown)
					else:
						tempRatioUp = ratioUp
						tempRatioDown = ratioDown

					#~ if (tempRatioUp.isFullEnough(self.rebinErrorBoundary) and tempRatioDown.isFullEnough(self.rebinErrorBoundary)):
					if (iBin == self.binMerging[nBin]):
						nBin = nBin+1
						self.__ratiosUp__.append(tempRatioUp)
						self.__ratiosDown__.append(tempRatioDown)
						tempRatioUp = None
						tempRatioDown = None

			if (tempRatioUp != None):
				self.__ratiosUp__.append(tempRatioUp)
				self.__ratiosDown__.append(tempRatioDown)
		else:
			log.logError("Trying to calculate error ratios, but histograms not set!")



