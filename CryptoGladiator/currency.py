class Currency(object):
    """Currency base class

    Get a currency using the form Currency('btc')
    Currencies are equal if their (case insensitive) tickers are the same.
    """

    _defaults = {}

    def __init__(self,ticker, description=None, symbol=None):
        if type(ticker) is Currency :
            ticker, description, symbol = ticker.ticker, ticker.description, ticker.symbol
        ticker = ticker.upper()
        if ticker in self._defaults :
            if description is None: description = self._defaults[ticker].description
            if symbol is None: symbol = self._defaults[ticker].symbol
        self.description = ticker if description is None else description
        self.symbol = symbol
        self.ticker = ticker

    def __str__(self): return self.ticker
    def __eq__(self,other): return self.ticker == other.ticker
    def __hash__(self): return self.ticker.__hash__()
    def __repr__(self): return "Currency('%s')"%self.ticker
    def url_form(self): return self.ticker.lower()

# instances


for ticker,desc,sym in [
    ("BTC", "Bitcoin", "Ƀ"),
    ("ETH", "Etherum", u"Ξ"),
    ("USD", "Dollar", u"$"),
    ("EUR", "Euro", u"€"),
    ("LTC", "Litecoin", u"Ł"),
    ]: Currency._defaults[ticker] = Currency(ticker,desc,sym)

BTC = Currency("BTC", "Bitcoin", "Ƀ")
ETH = Currency("ETH", "Etherum", u"Ξ")
USD = Currency("USD", "Dollar", u"$")
EUR = Currency("EUR", "Euro", u"€")
LTC = Currency("ltc")
GNT = Currency("GNT","Golem")
