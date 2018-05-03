from balance import Balance
from tradingpair import TradingPair
# from marketarchive import MarketArchive as Archive
from order import LimitSellOrder, LimitBuyOrder,\
                  MarketSellOrder, MarketBuyOrder
from order import OrderStatus
from exchange import Exchange

'''
Broker
-----------------

- handles balances and transactions,
- handles strategies
- connect and sync to exchange
- exports BrokerApi

BrokerAPI
------------

Exchange agnostic standard set of API functions

'''


class BrokerAPI:
    """ Public Broker API wrapper, exposed to Strategies """

    def __init__(self, broker):
        """export broker public api"""
        self.sell = broker.sell
        self.buy = broker.buy
        self.market_buy = broker.market_buy
        self.market_sell = broker.market_sell
        self.ticker = broker.ticker
        self.orders = broker.orders


class Broker:
    """Main broker object with balance management and exchange tracking"""
    market = None   # Market archive

    def __init__(self, exchange):
        """Create new broker"""
        self.trading_pairs = set()
        self.default_pair = TradingPair("btc/usd")
        # balance available for trading
        self.free_balance = Balance()
        # Orders dictionary {orderid: Order}
        self.orders = {}
        # Default strategy :: Strategy
        self.strategy = None
        # exchange agent
        self.exchange = exchange

    def API(self):
        """Export Public API functions"""
        return BrokerAPI(self)

    def register_order(self, order):
        """Register new order to broker"""
        order = self.exchange.execute_order(order)
        self.orders[order.order_id] = order
        return order

    def sell(self, volume, price, pair=None):
        """ Limit Sell <volume> of <crypto> at <price>."""
        if pair is None: pair = self.default_pair
        order = LimitSellOrder(pair, volume, price)
        return self.register_order(order)

    def buy(self, volume, price, pair=None):
        """ Limit Buy <volume> of <crypto> at <price>."""
        if pair is None: pair = self.default_pair
        order = LimitBuyOrder(pair, volume, price)
        return self.register_order(order)

    def market_sell(self, volume, pair=None):
        """ Market (immediate) sell <volume> of <crypto> around <price>."""
        if pair is None: pair = self.default_pair
        order = MarketSellOrder(pair, volume)
        return self.register_order(order)

    def market_buy(self, volume, pair=None):
        """ Market (immediate) buy <volume> of <crypto> around <price>."""
        if pair is None: pair = self.default_pair
        order = MarketBuyOrder(pair, volume)
        return self.register_order(order)

    def current_price(self, pair=None):
        if pair is None: pair = self.default_pair
        return self.current_price[pair]

    def get_orders(self):
        """Return Orders object"""
        return self.orders

    def get_supported_pairs(self):
        """ Returns set of supported pairs """
        return self.exchange.supported_pairs

    def get_free_balance(self):
        """Get current available (free) balance"""
        return self.balance

    def get_balance(self):
        """Get current managed balance"""
        return self.balance

    ### Background tasks ###

    def sync(self):
        # sync orders
        for o in self.orders:
            if o.status in [OrderStatus.Failed, OrderStatus.Pending]:
                self.exchange.update_order(self, o)

        # sync balance
        self.balance = self.exchange.get_balance()


if __name__ == "__main__":
    from xchg_test import TestExchange
    t = Broker(TestExchange())
    t.sell(123, volume=10000)
    t.buy(800000, volume=1)
    t.market_sell(23)
