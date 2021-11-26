Strategy  :
Moving average strategy is momentum strategy  based on generating buy and sell signal based on moving average  of two different time horizon.

Trading Signal :

Condition 1 : T1 ( Time Horizon ) > T2 ( Time Horizon )
    if MA(T1 ) >  MA(T2)  --> buy stock if below condition fullfill :
    A. total portfolio qty <   max stock allowed
    B. Total portfolio value <  max portfolio amount

Condition 2 : T1 > T2
    if MA(T1 ) >  MA(T2)  --> sell stock if below condition full-fill :
    A. total portfolio qty <   max stock allowed

Condition 3 : Liquidate position if  P <  (1 - Delta ) * previous price  & P >  (1 + Delta ) * previous price for long and short position respectively.

Variables:
file="SPY.csv",T1= 10,T2=30, field="Close",returnshift= 1,totalcash=10000000,delta=0.02,maxstocks =50)

assumptions
1. Moving Average :  SMA
2. Buying of stock on Opening price
3. MTM of stock on Closing price
4. PNL calcualtion is based on average pricing.  We can also use FIFO if needed.

Constraints:
1. sell / buy socks on long / short position if portfolio position goes above maxstocks
2. Alert if totalcash position goes above totalcash defined

Observation
1. With maxstock =20, this stragery makes loss whereas with maxstocks =30,50  we have profit

FurtherWork:
1. Normilaztion can be performed on data.
2. instead of using SMA we can also explore other options ( ewa or kernel regression ) as in SMA weight is equaly distributed.
3. we can consider market volatility.
