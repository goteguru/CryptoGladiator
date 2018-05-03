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

class Exchange:
    """ Abstract (interface) base class for specific exchange engines """
    supported_pairs = set()

    def execute_order(self, order):
        raise NotImplementedError("Must be implemented")

    def cancel_order(self, order):
        raise NotImplementedError("Must be implemented")

    def ticker( self, pair):
        """return most recent price of the pair
        return {last: 100, bid: 100, ask: 101} """
        raise NotImplementedError("Must be implemented")

    def update_order(self, order):
        raise NotImplementedError("Must be implemented")

    def supported_pairs(self):
        raise NotImplementedError("Must be implemented")

    def get_balance(self):
        raise NotImplementedError("Must be implemented")

    def get_comissions(self):
        raise NotImplementedError("Please implement")
