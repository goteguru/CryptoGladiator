from currency import Currency

class TradingPair(object):

    """Trading Pair implementation"""
    
    first = ''
    second = ''
    uniqid = ''

    def __init__ (self, first, second=None ):
        if second is None: 
            if isinstance(first,TradingPair) :
                self.first = first.first
                self.second = first.second
            elif isinstance(first,str) : 
                self.from_ticker(first)
            else:
                raise ValueError( "Must be currency pair or str")
        else: 
            if type(first) is str : first = Currency(first)
            if type(second) is str : second = Currency(second)
            if not isinstance( first, Currency) or not isinstance(second,Currency): 
                raise TypeError("Pair member must be Currency or str not (%s,%s)"%(type(first),type(second)))
            self.first = first
            self.second = second

        self.uniqid = self.ticker()

    def ticker(self):
        return self.first.ticker + "/" + self.second.ticker

    def from_ticker(self,s):
        if "/" not in s : raise ValueError("Invalid pair format.")
        a,b = s.upper().split("/")
        self.first = Currency(a)
        self.second = Currency(b)

    def url_form(self):
        return (self.first.url_form() + self.second.url_form()).lower()
    
    def __repr__(self): return self.ticker()
    def __str__(self): return self.__repr__(self)
    def __eq__(self,other): return self.uniqid == other.uniqid
    def __hash__(self): return self.uniqid.__hash__()


if __name__== "__main__":

    t = TradingPair("BtC/uSD")
    assert t.ticker() == "BTC/USD" 
    assert t.url_form() == "btcusd" 

    assert TradingPair('btc','eth').url_form() == "btceth"

    a = TradingPair(Currency('btc'), Currency('Eth'))
    assert a.url_form() == "btceth" 

    b = TradingPair('btc', 'Eth')
    assert b.url_form() == "btceth" 

    assert TradingPair('BTC','Eth') == TradingPair(Currency('btc'), Currency('EtH'))

    assert TradingPair("BTC/USD") in {TradingPair('btc', 'usd')}
    print ("test passed")


