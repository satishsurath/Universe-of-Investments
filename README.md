# Universe-of-Investments
Fintech Project 2

## 1. Prerequsites

### 1.1 Sign up for an IBKR Paper Trading Account
[How to Sign Up for an Interactive Brokers Paper Trading Account](https://algotrading101.com/learn/interactive-brokers-paper-trading-demo/)



### 1.2 Configure IBKR Trade Workstation API
![IBKR TWS - Global Configration - API Settings](Images/IBKR-TWS-GlobalConfiguration-API-Settings.png)



### 1.3 Install the prerequsites in your Python / Conda Environment
```shell
pip install ibapi
pip install ib_insync
pip install nest_asyncio
```


## References:

- https://ib-insync.readthedocs.io/index.html
  - Library to make working with Interactive Broker TWS API easier using linear style of programming;
- https://github.com/erdewit/nest_asyncio
  - This fixes the "RuntimeError: This event loop is already running".
