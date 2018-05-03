import uuid
from datetime import datetime
from tradingpair import TradingPair

"""
Smart Order class implementation with event callbacks
"""

class OrderStatus:
    Pending = "Pending" # Order submitted but not (yet) accepted by the broker
    Open    = "Open"    # Order accepted by the broker and active
    Closed  = "Closed"  # Order has been closed
    Failed  = "Failed"  # Order was not accepted by the broker
    Removed = "Removed" # Order has been removed without effect (cancelled)
    Unknown = "Unknown" # Unknown status (possible exchange error?)

class OrderError(RuntimeError):
    pass

class Order():
    """ Order object.
    Properties :
    - status :: OrderStatus
    - volume ->  maximum volume 
    - filled ->  filled volume
    - pair :: TradingPair
    - order_id -> uniq identifier
    - history = dictionary of timestamp log { "create":<datetime>,... }
    callbacks:
    - on_close 
    - on_partial 
    """

    next_order_id = 1

    def __init__(self, tradingpair,  volume):
        self.__status = OrderStatus.Unknown
        self.history = []
        self.volume = volume
        self.pair = TradingPair(tradingpair)
        self.status = OrderStatus.Pending
        self.order_id = Order.next_order_id
        Order.next_order_id += 1
        self.price = None

        # action callbacks
        self.on_close = None
        self.on_partial = None
        self.on_cancel = None
        self._ts("Created")

    def cancel(self):
        '''Cancel order'''
        self.status = OrderStatus.Removed
        if self.status is OrderStatus.Closed:
            raise OrderError('Closed Order can not be cancelled.')

        if self.on_cancel is not None:
            self.on_cancel(order)

    def _ts(self,txt):
        self.history.append((datetime.now(),txt))

    def __hash__(self):         return self.order_id.__hash__()
    def __repr__(self):         
        return "<[{id}] {type} {volume} {base} @ {price} {quote} {status}>".format(
                type = type(self).__name__,
                volume = self.volume,
                price = "?" if self.price is None else self.price,
                base = self.pair.base,
                quote = self.pair.quote,
                id = "-" if self.order_id is None else self.order_id,
                status = self.status,
                )

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self,s):
        if self.__status == s : return 
        self._ts('Status change: ' + str(s))
        self.__status = s
        try:
            if s is OrderStatus.Closed: self.on_close(self)
        except TypeError:
            pass

    

class LimitOrder(Order):
    def __init__(self, tradingpair,  volume, price):
        super().__init__(tradingpair, volume)
        self.__filled = 0
        self.on_fill = None
        self.price = price

    @property
    def filled(self):
        return self.__filled

    @filled.setter
    def filled(self, amount):
        if self.__filled != amount :
            self._ts('Filled: ' + str(amount))
            try:
                self.on_fill(self)
            except TypeError:
                pass
        if self.volume < amount:
            raise OrderError('Fill amount can not exceed order quantity.')

        self.__filled = amount

    def __repr__(self):         
        return "<[{id}] {type} {volume} {base} @ {price} {quote} {status} filled:{filled}>".format(
                type = type(self).__name__,
                volume = self.volume,
                filled = self.filled,
                price = "?" if self.price is None else self.price,
                base = self.pair.base,
                quote = self.pair.quote,
                id = "-" if self.order_id is None else self.order_id,
                status = self.status,
                )




class MarketOrder(Order):
    def close(self, price):
        self.status = OrderStatus.Closed
        self.price = price

class LimitBuyOrder(LimitOrder): pass
class LimitSellOrder(LimitOrder): pass
class MarketBuyOrder(MarketOrder): pass
class MarketSellOrder(MarketOrder): pass

if __name__ == "__main__" :
    l1 = LimitBuyOrder("btc/usd", 1, 5000)
    l2 = LimitSellOrder("btc/usd", 1, 5000)

    assert l1 != l2
    assert l1.status == OrderStatus.Pending

    l1.status = OrderStatus.Open
    assert l1.status == OrderStatus.Open

    l1.filled = 0.5
    assert l1.status == OrderStatus.Open 
    assert l1.filled == 0.5
    l1.filled = 1

    teszt = []
    def t(o): 
        teszt.append(o)
    l1.on_close = t

    l1.status = OrderStatus.Closed
    assert teszt[0] is l1

    m1 = MarketBuyOrder("eth/BTC", volume=1)
    assert m1.status == OrderStatus.Pending
    m1.close(5555)
    assert m1.status == OrderStatus.Closed




