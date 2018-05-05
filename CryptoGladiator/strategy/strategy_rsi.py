import strategy

class Strategy_RSI(Strategy):
    def __init__(self, limit1, limit2, *p):
        self._l1 = limit1
        self._l2 = limit2
        self.orderid = None
        super().__init__(*p)

    def action(self):
        pair=self.default_pair
        if ( self.archive.rsi(pair,"10m") > self._l1 ) :
            price = self.api.price(pair) * 0.99
            volume = self.balance[pair] * 0.2
            self.orderid = self.api.sell(pair, volume) 
            self.when(
                    self.rsi_under, (self._l2,),
                    self.api.buy,   (volume,)
                    )

    def rsi_under(self, limit):
        return self.self.archive.rsi(pair,"10m") < limit
            

    def buyback(self, volume, ):

             
        



class Trigger():
    """ Runs action with actionparams, when test returns True.

    The first parameter of both function will be the api.
    """

    def __init__(self, test, testparams, action, actionparams):
        self._test = test
        self._action = action
        self._tparams = testparams
        self._aparams = actionparams

    def run(self,api):
        if (self.teszt(api,*self._tparams):
            self.action(api, *self._aparams)



     

