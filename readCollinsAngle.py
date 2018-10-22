from ROOT import *
from math import *

def calcCosThetaCS(v_dil, v_mum, v_mup): 
	### Function to return value of cos(theta*) in Collins-Soper frame
	### takes as input 4-vector of dilepton in lab frame, and 4-vectors of mu+
	### and mu- in dilepton CM frame.

	### Get pz and E components of mu+ and mu- in lab frame.
	pz_mum = v_mum.Pz()
	e_mum  = v_mum.E()
	pz_mup = v_mup.Pz()
	e_mup  = v_mup.E()

	## Get mass and pt of dilepton in lab frame
	pt_dil   = v_dil.Pt()
	pl_dil   = v_dil.Pz()
	mass_dil = v_dil.M()
	cos_theta_cs = calcCosThetaCSAnal(pz_mum, e_mum, pz_mup, e_mup, pt_dil, pl_dil, mass_dil)
	return cos_theta_cs


def calcCosThetaCSAnal(pz_mum, e_mum, pz_mup, e_mup, pt_dil, pl_dil, mass_dil):
	## Analytical calculation of Collins-Soper cos(theta).  Uses pz, e of mu+
	## and mu-, and pt, pl, and mass of dilepton in lab frame.
	## debug = false;

	mum_minus = (1./sqrt(2.))*(e_mum - pz_mum)
	mum_plus  = (1./sqrt(2.))*(e_mum + pz_mum)
	mup_minus = (1./sqrt(2.))*(e_mup - pz_mup)
	mup_plus  = (1./sqrt(2.))*(e_mup + pz_mup)

	#~ print mass_dil, pt_dil
	dil_term  = 2./(mass_dil*sqrt((mass_dil*mass_dil) + (pt_dil*pt_dil)))
	mu_term   = (mum_plus*mup_minus) - (mum_minus*mup_plus)
	cos_cs    = dil_term*mu_term

	## The above calculation assumed dilepton pL > 0. Flip the sign of
	## cos_cs if this isn't true.
	if (pl_dil < 0.):
		cos_cs *= -1.

	return cos_cs


if __name__ == "__main__":
    main()

