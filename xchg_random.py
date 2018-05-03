from copy import copy
from random import gauss
from uuid import uuid4 as uuid
from datetime import datetime 

from order import OrderStatus, MarketSellOrder, MarketBuyOrder, LimitSellOrder, LimitBuyOrder
from balance import Balance
from exchange import Exchange, OrderError 
from tradingpair import TradingPair

BTCUSD = TradingPair('btc/usd')

class RandomExchange(Exchange):
    ''' Randomized buy/sell. Simulate exchange behavior for testing purposes. '''

    def __init__(self, starting_balance, lag_time=0, max_volume=1.0, price=8000.0):
        '''bootstrapping random exchange'''
        self.balance = starting_balance
        self.lag_time=lag_time
        self._supported_pairs = { BTCUSD }
        self.__current_price = price
        self.__last_price = price
        self.max_volume = max_volume
        self.orders = {}
            
    def _update_market(self):
        """update orders (buy and sell) and simulated market"""
        for o in self.orders.values():

            if o.status != OrderStatus.Open: continue
            
            print("u:",self.__current_price, o)
            t = type(o)
            if t is LimitBuyOrder and self.__current_price <= o.price:
                needed = o.volume - o.filled
                bought = min([needed, self.max_volume])
                o.filled += bought

            if t is LimitSellOrder and self.__current_price >= o.price:
                needed = o.volume - o.filled
                sold = min([needed, self.max_volume])
                o.filled += sold
                print("sell:",o)
            
            if o.filled == o.volume: 
                o.status = OrderStatus.Closed

    def change_price(self, amount=None):
        """change price manually or randomly"""
        self.__last_price = self.__current_price
        if amount is None:
            self.__current_price += gauss(0, 10)
        else:
            self.__current_price += amount
        self._update_market()

    def dump(self):
        """dump internal state"""
        print ("Price: ", self.__current_price)
        print ("Last: ", self.__last_price)
        print ("Maxlimit: ", self.max_volume)
        for o in self.orders.values():
            print(o)

    ### API interface implementation ###

    def get_balance(self):
        return self.balance

    def execute_order(self, order):
        if order.pair not in self._supported_pairs:
            raise OrderError("Unsupported Pair: " + str(order.pair))

        # check cover 
        typ = type(order)
        
        if order.order_id in self.orders:
            raise OrderError("Order already executed.")

        if typ is LimitSellOrder:
            bbal = self.balance[order.pair.base] 
            if bbal < order.volume:
                raise OrderError('Not enough money.')
            order.status = OrderStatus.Open

        elif typ is LimitBuyOrder:
            qbal = self.balance[order.pair.quote] 
            if qbal < order.volume * order.price:
                raise OrderError('Not enough money.')
            order.status = OrderStatus.Open

        elif typ is MarketSellOrder:
            self.balance[order.pair.base] -= order.volume
            self.balance[order.pair.base] += order.volume * self.__current_price
            order.close(self.__current_price)

        elif typ is MarketBuyOrder:
            self.balance[order.pair.base] += order.volume
            self.balance[order.pair.base] -= order.volume * self.__current_price
            order.close(self.__current_price)

        else:
            raise OrderError("Order Type not supported.")
            
        order.order_id = uuid()
        self.orders[order.order_id] = copy(order)
        return order

    def ticker( self, pair):
        return {
                'last': self.__last_price,
                'bid':  self.__current_price,
                'ask':  self.__current_price,
                }

    def update_order(self, order):
        try:
            xorder = self.orders[order.order_id]
            order.status = xorder.status
            order.price = xorder.price
            if type(order) in [LimitSellOrder, LimitBuyOrder]:
                order.filled = xorder.filled
        except KeyError:
            raise OrderError('Order not found.')
        return order

    def supported_pairs(self):
        return self._supported_pairs

    def cancel_order(self, order):
        try:
            del self.orders[order.order_id] 
        except KeyError:
            raise OrderError('No such order.')

    def get_comissions(self):
        return {TradingPair('btc/usd') : 0}


if __name__ == "__main__":
    x = RandomExchange(Balance({'BTC':5}), max_volume=1.0, price=8000.0)
    assert x.ticker('btc/usd')['last'] == 8000.0
    
    # test price change
    x.change_price(-1) 
    ret = x.ticker('btc/usd')
    assert ret['bid'] == 7999.0
    assert ret['last'] == 8000.0

    # test limitorder handling
    o1 = x.execute_order(LimitSellOrder("btc/usd",2.0,8012.6))
    assert x.update_order(o1).price == 8012.6
    assert x.update_order(o1).status == OrderStatus.Open

    # Exchange should fill and close Limit orders if possible
    x.change_price(100) # boom time :)
    ro = x.update_order(o1)
    assert ro.filled == 1.0
    assert ro.status == OrderStatus.Open
    x.change_price(0) # max_quantity can be used again 
    ro = x.update_order(o1)
    assert ro.filled == 2.0
    assert ro.status == OrderStatus.Closed

    # test marketorder handling
    o2 = x.execute_order(MarketSellOrder("btc/usd",1))
    assert x.update_order(o2).status == OrderStatus.Closed
    
    assert len(x.orders) == 2



