from currency import Currency

class TradingPair(object):

    """Trading Pair implementation"""
    
    base = ''
    quote = ''
    uniqid = ''

    def __init__ (self, base, quote=None ):
        if quote is None: 
            if isinstance(base,TradingPair) :
                self.base = base.base
                self.quote = base.quote
            elif isinstance(base,str) : 
                self.from_ticker(base)
            else:
                raise ValueError( "Must be currency pair or str")
        else: 
            if type(base) is str : base = Currency(base)
            if type(quote) is str : quote = Currency(quote)
            if not isinstance( base, Currency) or not isinstance(quote,Currency): 
                raise TypeError("Pair member must be Currency or str not (%s,%s)"%(type(base),type(quote)))
            self.base = base
            self.quote = quote

        self.uniqid = self.ticker()

    def ticker(self):
        return self.base.ticker + "/" + self.quote.ticker

    def from_ticker(self,s):
        if "/" not in s : raise ValueError("Invalid pair format.")
        a,b = s.upper().split("/")
        self.base = Currency(a)
        self.quote = Currency(b)

    def url_form(self):
        return (self.base.url_form() + self.quote.url_form()).lower()
    
    def __repr__(self): return self.ticker()
    def __str__(self): return self.__repr__()
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


