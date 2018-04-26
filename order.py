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
    Unknown = "Unknown" # Unknown status (possible exchange error?)

class Order():
    """ Order object.
    Properties :
    - status :: OrderStatus
    - volume ->  maximum volume 
    - filled ->  filled volume
    - pair :: TradingPair
    - orderid -> uniq identifier
    - timestamps = dictionary of timestamp log { "create":<datetime>,... }
    callbacks:
    - on_close 
    - on_partial 
    """

    def __init__(self, otype, tradingpair,  volume, order_id = None):
        self.type = otype
        self.volume = volume
        self.pair = TradingPair(tradingpair)
        self.status = OrderStatus.Pending
        self.timestamps = { "create":datetime.now() }
        if order_id is None:
            self.order_id = uuid.uuid4()
        else:
            self.order_id = order_id
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
    def __init__(self, tradingpair,  volume, price):
        super().__init__(otype, tradingpair, volume)
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
    def __init__(self, tradingpair,  volume):
        self.price = None
        super().__init__(otype, tradingpair, volume)

    def close(self,price):
        """ broker calls this method when the order is filled. """
        self.status = OrderStatus.Closed
        self.price = price
        if not self.on_close is None: self.on_close(self)


class LimitBuyOrder(LimitOrder): pass
class LimitSellOrder(LimitOrder): pass
class MarketBuyOrder(MarketOrder): pass
class MarketSellOrder(MarketOrder): pass

if __name__ == "__main__" :
    o1 = LimitBuyOrder("btc/usd", 100, 2)
    o2 = LimitSellOrder("btc/usd", 100, 2)
    o3 = MarketBuyOrder("eth/BTC", volume=1)

    assert o1 != o2
    
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


