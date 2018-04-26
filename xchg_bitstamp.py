from bitstamp import client, BitstampError
from requests import HTTPError
from .order import OrderStatus, Order
from .balance import Balance
from .exchange import Exchange, NotConnectedError, OrderError

"""
Bitstamp exchange Broker implementation
"""

class Bitstamp(Exchange):
    name = "Bitstamp"
    max_requests_per_frame = 600
    request_timeframe = 60 # sec

    def __init__(self, **auth):
        self.trading_pairs = set()
        self.connect(**auth)

    def connect(self, **auth):
        """ auth_params =
            {
            username:<username>,
            key:<apikey>,
            secret:<apisecret>
            }
        """

        self.connected = False
        try:
            if 'username'   not in auth: raise AuthError("Username is mandatory.")
            if 'key'        not in auth: raise AuthError("Key is mandatory.")
            if 'secret'     not in auth: raise AuthError("Secret is mandatory.")
            self.api = client.Trading(**auth)
            self._get_supported_pairs()
            self.connected = True
        except ValueError, BitstampError, HTTPError as e:
            self.status = str(e)

    def _get_supported_pairs(self):
        '''Load trading pairs'''

        if not self.connected: raise NotConnectedError
        pairs = filter(lambda r: r['trading'] == "Enabled", self.api.trading_pairs_info())
        self.trading_pairs = { TradingPair(p['name']) for p in pairs }

    def supported_pairs(self):
        '''Return trading pairs'''
        return  self.trading_pairs

    def transactions(self, ):
        '''returns recent transactions'''
        raw = self.api.user_transactions()
        return [ s for s in raw if s['type']=='2' ]

    def get_balances(self):
        '''Return balance info from the server'''
        if not self.connected: raise NotConnectedError
        response = self.api.account_balance(base=None, quote=None)
        fx = "_available"
        rawbal = {l[:-len(fx)]:v for l,v in response.items() if l.endswith(fx)}
        return Balance(rawbal)

    def update_order(self, order):
        '''Sync order info with bitstamp'''
        if not self.connected: raise NotConnectedError
        try:
            order_id = order.order_id
        except KeyError:
            raise OrderError('Invalid Order')

        try:
            result = self.api.order_status(order_id)
        except BitstampError as e:
            order.status = OrderStatus.Removed
            return order

        translate = {
            'In Queue': OrderStatus.Pending,
            'Open':     OrderStatus.Open,
            'Finished': OrderStatus.Closed,
        }
        order.extra = result.transactions
        try:
            order.status = translate[result.status]
        except KeyErrror:
            order.status = OrderStatus.Unknown

        # sum of base transactions
        base = order.pair.base.url_form()
        order.filled = sum [x[base] for x in result.transactions]
        return order


    def execute_order(self, order):
        """Submit (and execute) order to exchange """
        base = order.base.url_form()
        quote = order.quote.url_form()
        typ = type(order)

        try:
            if typ is LimitSellOrder:
                resp = self.api.sell_limit_order(order.volume, order.price, base, quote)

            elif typ is LimitBuyOrder:
                resp = self.api.buy_limit_order(order.volume, order.price, base, quote)

            elif typ is MarketBuyOrder:
                resp = self.api.buy_market_order(order.volume, base, quote)
                order.close(resp['price'])

            elif typ is MarketBuyOrder:
                resp = self.api.buy_market_order(order.volume, base, quote)
                order.close(resp['price'])

            else:
                raise OrderError("Order Type not supported.")
            
            order.order_id = resp['id']
            order.timestamps['submitted'] = resp['datetime']
            order.price = resp['price']
            order.volume = resp['amount']
            return order

        except BitstampError as e:
            raise OrderError(str(e))



