import broker
""" 
Kraken exchange Broker implementation
"""

class Kraken():
    name = "Kraken"
    
    
class RealKraken(RealBroker,Kraken):
    pass


class TestKraken(TestBroker,Kraken):
    pass
