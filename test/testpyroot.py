from ROOT import *

def main():
	outfile = TFile("filename.root", "NEW")
	#outfile.cd()
	h1 = TH1F("newhis", "newhis", 100, 0, 100)
	h1.Write()
	outfile.Close()
	print "DONE!"


if __name__ == "__main__":
	main()


