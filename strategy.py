import tradingpair
"""
Trading Strategy Base Class
"""

class Strategy():
    default_pair = TradingPair('btc/usd') 

    def __init__(api):
        self.api = api 

    def when( trigger, tparam, action, aparam):
        """Execute action if trigger returns True.
        
        Simple wrapper for add_trigger
        """
        t =  Trigger( trigger, tparam, action, aparam)
        self.api.add_trigger(t)

    def 

# Simple strategies

class BuyImmediate(Strategy):
    ''' try to buy as soon as possible '''
    def __init__(self):
        api.buy()

class SellImmediate(Strategy):
    ''' try to sell as soon as possible '''
    def __init__(self):
        api.sell()

class SellAtRSI(Strategy):
    ''' try to sell as soon as RSI failure '''
    def __init__(self)
        pass

class Range(Strategy):
    def __init__(self, pair, low, high):
        '''Buy at low price, sell at high price'''
        # register callbacks...

