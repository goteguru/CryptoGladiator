import uuid
from datetime import datetime
from tradingpair import TradingPair

"""
Order class with event callbacks
"""

class OrderStatus:
    Pending = "Pending" # Order submitted but not (yet) accepted by the broker
    Open    = "Open"    # Order accepted by the broker and active
    Closed  = "Closed"  # Order has been closed
    Failed  = "Failed"  # Order was not accepted by the broker
    Removed = "Removed" # Order has been removed without effect (cancelled)

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
        self.pair = TradingPair(tradingpair)
        self.status = OrderStatus.Pending
        self.orderid = uuid.uuid4()
        self.timestamps = { "create":datetime.now() }
        # action callbacks
        self.on_close = None
        self.on_partial = None

    def _ts(self,key):
        self.timestamps[key] = datetime.now()

    def __eq__(self, other):    return self.orderid == other.orderid
    def __hash__(self):         return self.orderid.__hash__()
    def __repr__(self):         
        return "<{type} {volume} {to} @ {price} {what}>".format(
                type = self.type,
                volume = self.volume,
                price = self.price,
                what = self.pair.second,
                to = self.pair.first,
                )
    

class LimitOrder(Order):
    def __init__(self, otype, tradingpair,  volume, price):
        super(self).__init__(otype, tradingpair, volume)
        self.filled = 0
        self.price = price


    def fill(self,filled_volume):
        """ broker calls this method when the order is filled. """
        self.sub_status = "Partial"
        self.filled = filled_volume
        self._ts('filled')
        if (self.filled < self.volume) :
            if self.on_partial is not None: self.on_partial(self)
        else:
            if not self.on_close is None: self.on_close(self)
            self.sub_status = "Filled"
            self.status = "Closed"


class MarketOrder(Order):
    def __init__(self, otype, tradingpair,  volume):
        super().__init__(otype, tradingpair, volume)

    def close(self,price):
        """ broker calls this method when the order is filled. """
        self.status = OrderStatus.Closed
        self.price = price
        if not self.on_close is None: self.on_close(self)

if __name__ == "__main__" :
    o1 = Order.limit_buy("btc/usd", 100, 2)
    o2 = Order.limit_sell("btc/usd", 100, 2)
    o3 = Order.market_buy("eth/BTC", volume=1)

    assert(o1 != o2)
    
    o1.fill(20)
    assert(o1.status == OrderStatus.Open)
    
    o1.fill(100)
    assert(o1.status == OrderStatus.Closed )

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


