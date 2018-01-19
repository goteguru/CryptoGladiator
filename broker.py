import numpy
import uuid
from balance import Balance
from tradingpair import TradingPair 
from marketarchive import MarketArchive as Archive
from order import Order

"""
Exchange Broker 
"""

class BrokerAPI(object):
    """ Public Broker API """
    def __init__(self,broker):
        """export broker public api"""
        self.sell = broker.sell
        self.buy = broker.buy
        self.market_buy = broker.market_buy
        self.market_sell = broker.market_sell
        self.ticker = broker.ticker
        self.orders = broker.orders
    
class Broker (object) :
    """Base Broker API exposed to algos"""
    exchange = "unknown"
    market = None   # :: Archive
    comission = 0
    
    def __init__ ( self ):
        """Create new broker"""
        self.default_pair = TradingPair("btc/usd")
        self.balance = Balance()
        self.orders = []            # dictionary { c_pair, type, volume, price }
        self.transactions = []
        self.strategy = None            # :: Strategy
    

    ######## Public Broker API ########

    def start():
        """ start broker (new thread?) """
        return self

    def stop():
        """ stop running broker. """
        pass
    
    def sell ( self, price, volume, pair=None ):
        """ Sell :volume: of :crypto: at :price:."""
        if pair is None: pair = self.default_pair
        order = Order.limit_sell(pair, volume, price)
        order.orderid = uuid.uuid4()
        self.orders[order.orderid] = order
        return order

    def buy ( self, price, volume, pair=None ):
        """ Buy :volume: of :crypto: at :price:."""
        if pair is None: pair = self.default_pair
        order = Order.limit_buy(pair, volume, price)
        order.orderid = uuid.uuid4()
        self.orders[order.orderid] = order
        return order

    def market_sell ( self, volume, pair=None ):
        """ Market (immediate) sell :volume: of :crypto: around :price:."""
        if pair is None: pair = self.default_pair
        order = Order.market_sell(pair, volume)
        order.orderid = uuid.uuid4()
        self.orders[order.orderid] = order
        return order

    def market_buy ( self, volume, pair=None ):
        """ Market (immediate) buy :volume: of :crypto: around :price:."""
        if pair is None: pair = self.default_pair
        order = Order.market_buy(pair, volume)
        order.orderid = uuid.uuid4()
        self.orders[order.orderid] = order
        return order

    def ticker ( self, pair=None):
        pass

    def orders(self):
        return self.orders


class RealBroker( Broker ):

    def update_balance():
        pass

    def update_comission():
        pass

class TestBroker( Broker ):
    lag_time = 0


if __name__ == "__main__":

    t=TestBroker()
    t.sell(123,volume=10000)
    t.buy(800000,volume=1)
    t.market_sell(23)

    
    
