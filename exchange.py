from broker import NotConnectedError, OrderError
from order import OrderStatus, Order
from balance import Balance

"""
Error classes
-----------------
"""
class ExchangeError(Exception):
    pass

class AuthError(ExchangeError):
    pass

class OrderError(ExchangeError):
    pass

class NotConnectedError(ExchangeError):
    pass

class ExchangeError(ExchangeError):
    pass

class Exchange:
    """ Abstract (interface) base class for specific exchange engines """
    supported_pairs = set()

    def execute_order ( self, order ):
        raise NotImplementedError("Must be implemented")

    def current_price( self, base, quote):
        raise NotImplementedError("Must be implemented")

    def update_order(self, order):
        raise NotImplementedError("Must be implemented")

    def supported_pairs(self):
        raise NotImplementedError("Must be implemented")

    def get_balance(self):
        raise NotImplementedError("Must be implemented")

    def update_comissions(self):
        raise NotImplementedError("Please implement")
