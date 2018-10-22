## CMS Non-resonant search ADD model
- The non-resonance excess search in dilepton mass spectrum in the CMS detector
- ADD (virtual graviton) and CI (virtual preon) models

### Organization
- Programs starting with "plot" are used to plot graphs
- Programs starting with "compute" are used to compute significance or limit
- Source DY and ADD mass spectra are stored in `ADDdata/` and `CIdata/` (which are too large so I didn't commit them)
- Data Cards for Combine are stored in `dataCards/`
- Plots of source data distributions are stored in `rawDataPlots/`
- Measurement plots of limits are stored in `limits/`

### Limit study
Commands to measure the limit of ADD signal:
```
python computeLimit.py
python plotLimit.py
```
Where `computeLimit.py` will read source data, calculate the integrals (event yield) from Mmin (2.8 TeV) to Mmax (\Lambda), and write datacards as signal = ADD - DY, and background = DY. The limits are calculated by `combine -M AsymptoticLimits <datacard> -m lambdaT` in the `computeLimit.py` automatically. And the `plotLimit.py` program will read measured limits for each lambda value, and plot a result.

### Significance study
Commands to measure the significance of ADD signal:
```
python computeSignificance.py
python plotSignificance.py
```

### Some notes:
1. Mass histograms need to be scaled by:
- Scale(1/total event number), to get a event yield histogram (default 100000)
- Scale(36300\*XSec), which is luminosity \* cross section
- Scale(1/BinWidth), so the height of histograms will not change with bin width (only in raw data plotting)
2. Current focus is placed on dielectron channel
3. There's a no-match in low pt histograms, need to check later!
4. Systematic errors in datacards only consist of luminosity, need to add more later!

### Update Oct 20th
- Updated raw data plotting to include both constructive and destructive
- Updated limit measurement for either constructive or destructive
- Current signal = (ADD+DY) - DY, not including interference term

### Update Oct 21st
- Computed Collins-Angle for DY and DY+ADD. But Collins-Angle for ADD is nan because there's phi = 0 for each bosonP4
- Plotted limit Vs. Mmin. The effect of choices of Mmin is negligible
- Plotted Significance Vs. Mmin. The significance of signals with Lambda = 7~10 are almost the same.
