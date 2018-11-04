## CMS Non-resonant search ADD model
- The non-resonance excess search in dilepton mass spectrum in the CMS detector
- ADD (virtual graviton) and CI (virtual preon) models

### Organization
- Programs starting with "plot" are used to plot graphs
- Programs starting with "compute" are used to compute significance or limit
- `ADDdata/` and `CIdata/` store source DY and ADD mass spectra (which are too large so I didn't commit them)
- `ADDdataCards/` and `CIdataCards/` store datacards for Combine
- `ADDlimits/` and `CIlimits/` store measurements of limits and significances for each model
- `rawDataPlots/` stores raw data distributions, including event kinematics

### Limit study
Commands to measure the limit of ADD signal: (for CI, replace ADD with CI in cmd)
```
python computeLimit.py ADD 2800
python plotLimit.py ADD 2800
```
Where `computeLimit.py` will read source data, calculate the integrals (event yield) from Mmin (2.8 TeV, or replace it with other values) to Mmax (\Lambda for ADD and 10000 for CI), and write datacards as signal = ADD - DY, and background = DY. The limits are calculated by `combine -M AsymptoticLimits <datacard> -m lambdaT` in the `computeLimit.py` automatically. And the `plotLimit.py` program will read measured limits for each lambda value, and plot a result.

### Significance study
Commands to measure the significance of ADD signal:
```
python computeSignificance.py ADD
python plotSignificance.py ADD
```
The programs will read source data, calculate significances by `combine -M Significance <datacard> -t -1 -m lambda -n Mmin --expectSignal=1` automatically for a range of minimum cuts from 1200 to 3200, and plot significance Vs Mmin for each helicity.

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
- Plotted Significance Vs. Mmin for ADD. The significance of signals with Lambda = 7~10 are almost the same.

### Update Oct 24th
- Adapted most of the codes to include both CI and ADD files
- Currently inclusive programs are computeLimit.py, computeSignificance.py, plotMassSingle.py, plotLimit.py, plotSignificance.py, will need to adapt the others

### Update Oct 28th
- Computed limit for CI model. Matches with Jan's result.
- Adapted all codes to be able to study on both models.
- Plotted Significance Vs. Mmin for CI, will need further interpretation about the stats.

### Update Nov 3rd
- Updated the function to calculate the parameter which lets limit = 1 (when f(lambda)=1).
- Updated function to plot Limit Vs. Mmin, to adapt to two models
- Found one issue with simulated sample xsec, which makes some event yield larger than expected, but which luckily is not affecting the limit calculation.
