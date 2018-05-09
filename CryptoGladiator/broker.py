"""
Broker modul
---------------

The broker modul connects strategies to (real) exchanges. It's purpose is to start, stop, schedule strategies and run backtests.
- handles balances and transactions,
- handles strategies
- connect and sync to exchange
- exports BrokerApi
"""

import asyncio
import threading
import time
from functools import partial
import ccxt.async as ccxt

from .balance import Balance
from .tradingpair import TradingPair
# from marketarchive import MarketArchive as Archive
from .order import (
        LimitSellOrder,
        LimitBuyOrder,
        MarketSellOrder,
        MarketBuyOrder
)
from .order import OrderStatus

class BrokerError(Exception):
    pass

'''
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
    archive = None  # Market archive
    exchanges = {}  # ccxt exchanges {'exchgname': exch_object}
    job_loop = None     # job processor async loop

    def __init__(self):
        """Create new broker"""

        self.free_balance = Balance()
        # Orders dictionary {orderid: Order}
        self.orders = {}
        # Default strategy :: Strategy
        self.strategy = None
        # job_processor shutdown event
        self.shutdown = threading.Event()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
        # TODO: close exchanges

    def start(self):
        '''start job processor'''
        self.job_thread = threading.Thread(
            target=self.__job_processor,
            name="job_processor"
            )
        self.job_thread.start()
        while not self.job_loop:
            pass # block while loop start

    def stop(self):
        '''stop job processor'''
        self.shutdown.set()

    def __job_processor(self):
        '''
        Thread function to process background jobs
        All ccxt market query must be called from
        this thread loop.
        TODO: separate thread for each exchanges.
        '''
        self.job_loop = asyncio.new_event_loop()
        print("jobprocessor started.")
        asyncio.set_event_loop(self.job_loop)
        async def quit():
            while not self.shutdown.is_set():
                await asyncio.sleep(1)
                print("jobprocessor is running.")
            self.job_loop.stop()

        self.job_loop.run_until_complete(quit())

        print("jobprocessor stopped.")
        self.job_loop.close()
        self.shutdown.set()

    def run_on_job_processor(self, func):
        '''schedule function exchange in a thread loop'''
        if not self.job_loop:
            raise RuntimeError("Job processor is not started.")

        future = asyncio.run_coroutine_threadsafe(func, self.job_loop)
        return future

    def exchange_list(self):
        return self.exchanges.keys()

    def exchange_open(self, xchg_name, config = {}):
        try:
            self.exchanges[xchg_name] = getattr(ccxt, xchg_name)(config)
        except AttributeError as e:
            raise BrokerError("Unknown exchange: ", str(xchg_name))

    def exchange_call(self, xchg_name, function_name, *args, **kwargs):
        '''schedule function call for an exchange in a thread loop'''

        try:
            coro = getattr(self.exchanges[xchg_name], function_name)(*args, **kwargs)
            return self.run_in_job_processor(coro)
        except AttributeError as e:
            raise BrokerError("Invalid ccxt method name: " + str(function_name))

    def ticker(self,xchg_name):
        self.exchange_call(xchg_name, "fetch_ticker", 'ETH/BTC')

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
    from xchg_test import RandomExchange
    mybalance = Balance({'btc':100})
    xchg = RandomExchange(mybalance)
    t = Broker(xchg)
    t.sell(123, volume=10000)
    t.buy(800000, volume=1)
    t.market_sell(23)
