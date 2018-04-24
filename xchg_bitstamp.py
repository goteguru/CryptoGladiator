from bitstamp import client, BitstampError 
from requests import HTTPError
from .broker import RealBroker, NotConnectedError, OrderNotFoundError
from .order import OrderStatus, Order
from .balance import Balance

""" 
Bitstamp exchange Broker implementation
"""

class Bitstamp():
    name = "Bitstamp"
    
    
class RealBitstamp(RealBroker,Bitstamp):
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
            self.bitstamp = client.Trading(**auth)
            self._get_supported_pairs()
            self.connected = True
        except ValueError, BitstampError, HTTPError as e:
            self.status = str(e)

    def _get_supported_pairs(self):
        '''Load trading pairs'''

        if not self.connected: raise NotConnectedError
        pairs = filter(lambda r: r['trading'] == "Enabled", self.bitstamp.trading_pairs_info())
        self.trading_pairs = { TradingPair(p['name']) for p in pairs }

    def supported_pairs(self):
        '''Return trading pairs'''
        return  self.trading_pairs

    def transactions(self):
        '''Show my transactions'''
        raw = self.bitstamp.user_transactions()
        transactions = [ s for s in raw if s['type']=='2' ]
        for l in transactions : 
            print(l)

    def update_balance(self):
        '''Update balance info from server'''
        if not self.connected: raise NotConnectedError
        self.balance = Balance()
        raw = self.bitstamp.account_balance(base=None, quote=None)

        self.report(balance)
    
    def update_order(self, order):
        '''update order'''
        if not self.connected: raise NotConnectedError

        if type(order) is str :
            try:
                order = self.orders[order]
            except:
                raise ValueError("Order not found.")

        try:
            result = self.bitstamp.order_status(order_id)
        except client.BitstampError as e:
            order.status = OrderStatus.Removed
        else:
            order.extra = result.transactions
            if result.status is 'In Queue':
                order.status = OrderStatus.Pending
            elif result.status is 'Open':
                order.status = OrderStatus.Open
            elif result.status is 'Finished':
                order.status = OrderStatus.Closed
            #TODO: összeadni a transaction mező elemeit


class TestBitstamp(TestBroker,Bitstamp):
    pass
