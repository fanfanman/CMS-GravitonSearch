from readData import getMassDistroSignal

name = "test"
model = "ADD"
lambdaT = 8000
helicity = ""

hist = getMassDistroSignal(name, model, lambdaT, helicity, False)
print hist.Integral(hist.FindBin(2400), hist.GetSize()-1)
