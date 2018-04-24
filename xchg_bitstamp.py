from bitstamp import client 
from .broker import RealBroker, Broker
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
        if 'username'   not in auth: raise Broker.ConfigError("username is mandatory.")
        if 'key'        not in auth: raise Broker.ConfigError("key is mandatory.")
        if 'secret'     not in auth: raise Broker.ConfigError("secret is mandatory.")
        self.bitstamp = client.Trading(**auth)
        self._get_supported_pairs()

    def _get_supported_pairs(self):
        '''Load trading pairs'''
        pairs = filter(lambda r: r['trading'] == "Enabled", self.bitstamp.trading_pairs_info())
        self.trading_pairs = { TradingPair(p['name']) for p in pairs }

    def supported_pairs(self):
        '''Return trading pairs'''
        return  self.trading_pairs

    def transactions(self, ):
        '''returns recent transactions'''
        raw = self.bitstamp.user_transactions()
        return [ s for s in raw if s['type']=='2' ]

    def update_balance(self):
        '''Update balance info from the server'''
        response = self.bitstamp.account_balance(base=None, quote=None)
        fx = "_balance"
        self.balance = Balance({l[:-fx]:v for l,v in response.items() if l.endswith(fx)})
                

    
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
            trans = {
                'In Queue': OrderStatus.Pending,
                'Open':     OrderStatus.Open,
                'Finished': OrderStatus.Closed,
            }
            order.extra = result.transactions
            order.status = trans[result.status]

            # sum of base transactions
            base = order.pair.base.url_form()
            order.filled = sum [x[base] for x in result.transactions]
        return order    



class TestBitstamp(TestBroker,Bitstamp):
    pass
