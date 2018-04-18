from bitstamp import client 
from .broker import RealBroker
from .order import OrderStatus, Order

""" 
Bitstamp exchange Broker implementation
"""

class Bitstamp():
    name = "Bitstamp"
    
    
class RealBitstamp(RealBroker,Bitstamp):
    def __init__(self, **auth):
        self.connected = True
        self.trading_pairs = set()
        try:
            self.connect(**auth)
        except:
            self.connected = False
        
    def connect(self, **auth):
        """ auth_params = {username:<username>, key:<apikey>, secret:<apisecret>}"""
        if 'username'   not in auth: raise broker.ConfigError("username is mandatory.")
        if 'key'        not in auth: raise broker.ConfigError("key is mandatory.")
        if 'secret'     not in auth: raise broker.ConfigError("secret is mandatory.")
        self.bitstamp = client.Trading(**auth)
        self._get_supported_pairs()

    def _get_supported_pairs(self):
        '''Load trading pairs'''
        pairs = filter(lambda r: r['trading'] == "Enabled", self.bitstamp.trading_pairs_info())
        self.trading_pairs = { TradingPair(p['name']) for p in pairs }

    def supported_pairs(self):
        '''Return trading pairs'''
        return  self.trading_pairs

    def transactions(self):
        '''Show my transactions'''
        raw = self.bitstamp.user_transactions()
        transactions = [ s for s in raw if s['type']=='2' ]
        #self.table(transactions)
        for l in transactions : 
            print(l)

    def update_balance(self):
        '''Update balance info from server'''
        self.balance = Balance(
        balance = self.bitstamp.account_balance(base=None, quote=None)
        self.report(balance)
    
    def update_order(self, order):
        '''update order'''

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
