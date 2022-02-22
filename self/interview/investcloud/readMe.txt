'''
## It contains the details about logic implemented, assumptions and references used
'''
1. Nelson Seigal
----------------------------
1.Nelson Siegel model is widely used in the financial market for fixed income products.
2. One drawback,unable to handle change in slope and curvature in curve along the tenors.
3. Nelson‐Siegel model, has slope and curvature factors which help to construct yield curve
4. Factors : long term bond  (β1), short term bond  (β2) and medium term bond  (β3), respectively. λ ( In code, variable 'Shape' is assgined to λ ),
as a decay decay factor.The value of λ affects the fitting power of the model for different segments of the curve.
it determines both the steepness of the slope factor and the location of the maximum (resp. minimum)
5. Grid Search for  λ values ranging from 0.05 to 3 . The estimates with the highest R2 were then chosen as the optimal parameter set.


Assumption:
1.  Bond Portfolio is maximum of two bonds.

Issues :
1. In practice, it is well known that grid search based OLS leads to parameter instability in the time series of estimates.
2. Along with OLS we can also try to WLS.
3. in formula, y(τ) = β1 + (β2 + β3) (1 - eλ τ) / (λ τ) - β3 eλ τ = a + b (1 - eλ τ) / (λ τ) - c eλ τ  ->  seems incorrect after I referred couple of documents, it seems we should have
exp(e-λτ). I mentioned documents below for reference. It migth be my ignorance  I have not referred more documents on this.

otherPoints:
1. File Generated  ( /investcloud/result ):  investcloud_NS_paramters.csv, investcloud_NS_predicted_spot.csv, investcloud_NSActualPreredictedStatsComp.csv,ActaulVsNSYieldCurve.png, bond_pricing.csv
2. all varaibles are inside params(Enum) class

Reference
1.https://dspace.cuni.cz/bitstream/handle/20.500.11956/71966/BPTX_2013_2_11230_0_387924_0_151485.pdf?sequence=1&isAllowed=y
2. https://www.ccilindia.com/RiskManagement/Documents/Indian%20Sovereign%20Yield%20Curve%20using%20Nelson-Siegel-Svensson%20Model/CCIL-469-22102005115800.pdf
3. Books-  Fixed-income securities and derivatives handbook - Moorad Choudhry
4. Book - Bruce Tuckman, Angel Serrat - Fixed Income Securities_ Tools for Today's Markets-Wiley (2011) (1)