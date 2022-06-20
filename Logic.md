

# Logic:

## Parabolic Stop & Reverse (PSAR) & 200 Days Simple Moving Average Strategy

### Buy

- If Stock price > 200 Day Simple Moving Avergae & PSAR Dot below candle, buy.
- If Stock price > 200 Day Simple Moving Avergae & PSAR Dot above candle, exit buy position (Not a signal to sell short).

### Sell

- If Stock price < 200 Day Simple Moving Avergae & PSAR Dot above candle, short sell.
- If Stock price < 200 Day Simple Moving Avergae & PSAR Dot below candle, exit short position (Not a signal to buy).
 
 
## What is PSAR (Parabolic Stop & Reverse)?
The Parabolic SAR indicator, is used to determine trend of a stock and potential reversals in price. The indicator uses a trailing stop and reverse method , to identify suitable exit and entry points. The parabolic SAR indicator appears on a chart as a series of dots, either above or below an asset's price, depending on the direction the price is moving. A dot is placed below the price when it is trending upward, and above the price when it is trending downward. The dots above the candle act as dynamic moving resistance price points while the dots above the candle act as dynamic moving support. An Accelaration factor is also used in the calculation of the PSAR which starts at 0.02 and increases by 0.02 up to a maximum of 0.2 

RPSAR=Prior PSAR + [Prior AF(Prior EP-Prior PSAR)]
FPSAR=Prior PSAR − [Prior AF(Prior PSAR-Prior EP)]
where:
RPSAR = Rising PSAR
AF = Acceleration Factor, it starts at 0.02 and increases by 0.02, up to a maximum of 0.2, each time the extreme point makes a new low (falling SAR) or high(rising SAR)
FPSAR = Falling PSAR
EP = Extreme Point, the lowest low in the current downtrend(falling SAR)or the highest high in the current uptrend(rising SAR)


## References:
- <a id="1">[1]</a>Organisational for Economic Co-Operation and Development. "Stochastic." 
  - https://stats.oecd.org/glossary/detail.asp?ID=3848
- <a id="2">[2]</a>CMC Markets. "Stochastic Indicator."
  - https://www.cmcmarkets.com/en/trading-guides/what-is-a-stochastic-indicator
- <a id="3">[3]</a>Technical Analysis, Inc. "Lane's Stochastics," Page 2.
  - https://www.forexfactory.com/attachment/file/3499852
 
 ## What is RSI (Relative Strength Index)?
 RSI (Relative Strength Index) is a momentum indicator which identifys overbought & oversold condtions and provides buy & sell signals. RSI below 20% indicates extremely oversold conditions and serves as a signal to buy the security. RSI above 70% indicates extremely overbought conditions and serves as a signal to buy the security. RSI divergences serve as a good indicator to spot discrepancies between the price & momentum. When price is advancing on declining momentum, it;s a siganl to sell while when price is declining on increasing momentum, it's a signal to buy.  

RSI  =100−[100/1+Average Gains/Average Loss]


### How Can I Use Stochastics in Trading?
The stochastic indicator establishes a range with values indexed between 0 and 100. A reading of 80+ points to a security being overbought, and is a sell signal. Readings 20 or lower are considered oversold and indicate a buy.<sup>[\[3\]](#3)</sup>

### What Are Stochastics?
In technical analysis, stochastics refer to a group of oscillator indicators that point to buying or selling opportunities based on momentum. In statistics, the word stochastic refers to something that is subject to a probability distribution, such as a random variable.<sup>[\[1\]](#1)</sup> In trading, the use of this term is meant to indicate that the current price of a security can be related to a range of possible outcomes, or relative to its price range over some time period.<sup>[\[2\]](#2)</sup>
