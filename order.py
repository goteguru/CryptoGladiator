import uuid
from datetime import datetime
from tradingpair import TradingPair

"""
broker order class

"""

class Order():
    def market_buy(*p,**args):
        return MarketOrder("buy",*p, **args)
    def market_sell(*p,**args):
        return MarketOrder("sell",*p, **args)
    def limit_buy(*p,**args):
        return LimitOrder("buy",*p, **args)
    def limit_sell(*p,**args):
        return LimitOrder("buy",*p,**args)

    def __init__(self, otype, tradingpair,  volume):
        self.type = otype
        self.volume = volume
        self.filled = 0
        print(type(tradingpair))
        self.pair = TradingPair(tradingpair)
        self.status = "Pending"
        self.orderid = uuid.uuid4()
        self.timestamps = { "create":datetime.now() }
        # action callbacks
        self.on_close = None
        self.on_cancel = None
        self.on_partial = None

    def _ts(self,key):
        self.timestamps[key] = datetime.now()


    def cancel(self):
        """ broker calls this method when the order has been cancelled. """
        if self.on_cancel is not None: self.on_cancel(self)
        self.status = "Cancelled"
        self._ts('cancel')

    def __eq__(self, other):    return self.orderid == other.orderid
    def __hash__(self):         return self.orderid.__hash__()
    def __repr__(self):         
        return "<{type} {volume} {to} @ {price} {what}>".format(
                type=self.type,
                volume=self.volume,
                price = self.price,
                what = self.pair.second,
                to = self.pair.first,
                )

class LimitOrder(Order):
    def __init__(self, otype, tradingpair,  volume, price):
        super().__init__(otype, tradingpair, volume)
        self.filled = 0
        self.price = price

    def on_broker(self,orderid):
        """broker calls this method when the remote broker accepts the order"""
        self.status = "Untouched"
        self.orderid = orderid

    def fill(self,filled_volume):
        """ broker calls this method when the order is filled. """
        self.status = "Partial"
        self.filled = filled_volume
        self._ts('filled')
        if (self.filled < self.volume) :
            if self.on_partial is not None: self.on_partial(self)
        else:
            if not self.on_close is None: self.on_close(self)
            self.status = "Closed"

class MarketOrder(Order):
    def __init__(self, otype, tradingpair,  volume):
        super().__init__(otype, tradingpair, volume)

    def close(self,price):
        """ broker calls this method when the order is filled. """
        self.status="Closed"
        self.price = price
        if not self.on_close is None: self.on_close(self)


if __name__ == "__main__" :
    o1 = Order.limit_buy("btc/usd", 100, 2)
    o2 = Order.limit_sell("btc/usd", 100, 2)
    o3 = Order.market_buy("eth/BTC", volume=1)

    assert(o1 != o2)
    
    o1.fill(20)
    assert(o1.status == "Partial")
    
    o1.fill(100)
    assert(o1.status == "Closed")

    o2.cancel()
    assert(o2.status == "Cancelled")

    o3.close(234)
    assert o3.price == 234

    teszt = []
    def t(o): 
        global teszt
        teszt.append(o)
    o3.on_close = t

    o3.close(234)
    assert o3.price == 234
    assert teszt[0] is o3


