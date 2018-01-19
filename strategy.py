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



