from .currency import Currency

class _CurrencyContainer:
    def __init__(self, currencies=None):
        self._container = {}

        if currencies is None : return
        if type(currencies) is not dict:
            raise Exception('must be created from dict')

        for c,v in currencies.items() :
            self._container[Currency(c)] = v

    def copy(self):
        return self.__class__(self._container)

    def __getitem__(self, index):
        index = Currency(index)
        if index not in self._container :
            return 0
        return self._container[index]

    def __setitem__(self, index, value):
        index = Currency(index)
        self._container[index] = value

    def __eq__(self, other):
        a = { k:v for k,v in other._container.items() if v > 0 }
        b = { k:v for k,v in self._container.items() if v > 0 }

        if len(a) != len(b) : return False
        for k,v in a.items():
            if v != b[k] : return False

        return True

    def __repr__(self):
        return " | ".join( c.ticker + ":" + str(v) for c,v in self._container.items() )

    def __mul__(self,n):
        return BalanceDelta({c:n*v for c,v in self._container.items()})


class BalanceDelta(_CurrencyContainer):
    """Balance delta. Currency quantities can be negative."""

    pass

class Balance(_CurrencyContainer):

    """Currency balance.
    one or more currency and its quantity.
    quantity can not be <0
    """

    def split(self, req):
        """split the wallet based on BalanceDelta"""
        if isinstance(req, BalanceDelta) : req = req._container
        a,b = self.copy(), Balance()
        aw, bw = a._container, b._container
        for k,val in req.items():
            if k not in aw:
                bw[k] = 0
            elif aw[k] >= val:
                bw[k] = val
                aw[k] -= val
            else:
                bw[k] = aw[k]
                aw[k] = 0
        return (b, a)

    def __add__(self, other):
        res = self.copy()
        w = res._container
        if type(other) is Balance:
            for k,val in other._container.items():
                w[k] = val + w[k] if k in w else val
            return res
        elif type(other) is BalanceDelta:
            for c,x in other._container.items():
                w[c] = w[c] + x if c in w else x
                if w[c]<0 : raise ValueError("Balance can not be negative.")
            return res
        else:
            raise TypeError("Only Balance or BalanceDelta can be added")


    def __sub__(self, other):
        """ subtract balance or delta from balance.
        balance - balance -> delta
        balance - delta -> balance
        """
        if type(other) is Balance:
            w = {}
            a , b = self._container , other._container
            for x,v in a.items():
                if x in b: w[x] = v - b[x]
                else: w[x] = v
            for x,v in b.items():
                if x not in a: w[x] = -v
            return BalanceDelta(w)
        elif type(other) is BalanceDelta:
            return self + other*-1
        else:
            raise TypeError("Only Balance or BalanceDelta can be subtracted.")

    def add(self, currency, volume):
        self = self + Balance({currency:volume})
        return self
