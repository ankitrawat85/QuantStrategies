# Coding Exercise - Yield Curve Model
For this exercise you will implement a simple yield curve model.

---
## Tasks
### 1 - Parse input data
The input data contains historical prices for various zero-coupon bonds and is split into two files. One file contains 
the identifiers and maturities. The other file contains the price time series. You should parse this data into a data 
structure that is suitable for the next tasks. The zero-coupon bonds pay 100 at maturity.

### 2 - Calculate zero rates
A (zero-coupon) yield curve maps maturities to zero rates. Calculate the zero rate (sometimes also known as the continuously compounded yield to maturity in the case of zero coupon bonds) for each bond and date and output them to a file.

### 3 - Fit yield curve model
For each date, fit the Nelson and Siegel (1987) model to the yield curve that was calculated in the previous task:

   y(&tau;) = &beta;<sub>1</sub> + (&beta;<sub>2</sub> + &beta;<sub>3</sub>) (1 - e<sup>&lambda; &tau;</sup>) / (&lambda; &tau;) - &beta;<sub>3</sub> e<sup>&lambda; &tau;</sup> = a + b (1 - e<sup>&lambda; &tau;</sup>) / (&lambda; &tau;) - c e<sup>&lambda; &tau;</sup>

Since you were provided zero-coupon bonds, you could calibrate a, b and c via ordinary least squares if &lambda; were 
known. This leads to a grid search algorithm:
1. For &lambda; in a reasonable grid, calculate a, b and c via linear regression as well as the corresponding R<sup>2</sup>.
2. Pick &lambda;, a, b and c (and therefore, &lambda;, &beta;<sub>1</sub>, &beta;<sub>2</sub> and &beta;<sub>3</sub>) with the highest R<sup>2</sup>.

Output the estimates to a file. Additionally, calculate and output some statistics on how well the calibrated model re-prices the provided bonds.

### 4 - Simulate prices of artificial bonds
Provide a function that takes as input 

* the calibrated model 
* bond characteristics (maturity, coupon frequency, coupon rate)

and outputs the price of such a bond.

### 5 - Bonus
1. Do you spot any issues with the approach in 3 (which may depend what the model is used for)?
2. Given a history of calibrated yield curve models, sketch how you would calculate risk measures such as VaR of (portfolios of) bonds 

## General information
* Submit your solution in Python
* Document, structure and test your solution like you would a production system
* Feel free to make some reasonable simplifying assumptions, but please document them
