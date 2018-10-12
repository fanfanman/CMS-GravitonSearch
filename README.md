## CMS Non-resonant search ADD model
- The non-resonance excess search in dilepton mass spectrum in the CMS detector
- ADD (virtual graviton) and CI (virtual preon) models

### Organization
- Programs starting with "plot" are used to plot graphs
- Programs starting with "compute" are used to compute significance or limit
- Source DY and ADD mass spectra are stored in `/rootfiles`
- Data Cards for Combine are stored in `/dataCards`
- Plots of source data distributions are stored in `/plots`

### Limit study
Commands to measure the limit of ADD signal:
```
python computeLimit.py
python plotlimit.py
```
Where `computeLimit.py` will read source data, calculate the integrals (event yield) from Mmin (2.8 TeV) to Mmax (\Lambda), and write datacards as signal = ADD - DY, and background = DY. The limits are calculated by `combine -M AsymptoticLimits <datacard> -m lambdaT` in the `computeLimit.py` automatically. And the `plotlimit.py` program will read measured limits for each lambda value, and plot a result.

### Significance study
- Still under development

### Some notes:
1. Mass histograms need to be scaled by:
- Scale(1/total event number), to get a event yield histogram
- Scale(36300\*XSec), which is luminosity \* cross section
- Scale(1/BinWidth), so the height of histograms will not change with bin width
2. Current focus is placed on dielectron channel
3. There's a no-match in low pt histograms, need to check later!
4. Systematic errors in datacards only consist of luminosity, need to add more later!
