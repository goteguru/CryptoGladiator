from .order import OrderStatus, Order
from .balance import Balance
from .exchange import Exchange, NotConnectedError, OrderError

class TestExchange(Exchange):
    ''' simulate exchange behavior '''
    lag_time = 0

    def __init__(self, starting_balance, market, start_date=0):
        '''bootstrap exchange with starting balance and market'''
        self.balance = starting_balance
        self.supported_pairs = {
                TradingPair('btc/usd'),
                TradingPair('eth/usd'),
                }

    def execute_order ( self, order ):
        base = order.base.url_form()
        quote = order.quote.url_form()
        typ = type(order)

        if typ is LimitSellOrder:
            pass

        elif typ is LimitBuyOrder:
            pass

        elif typ is MarketBuyOrder:
            pass

        elif typ is MarketBuyOrder:
            pass

        else:
            raise OrderError("Order Type not supported.")

        raise NotImplementedError("to be implemented")



    def current_price( self, base, quote):
        raise NotImplementedError("Must be implemented")

    def update_order(self, order):
        raise NotImplementedError("Must be implemented")

    def supported_pairs(self):
        raise NotImplementedError("Must be implemented")

    def get_balance(self):
        raise NotImplementedError("Must be implemented")

    def update_comissions(self):
        raise NotImplementedError("Should be implemented.")
