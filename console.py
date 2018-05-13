import cmd, json, time
import threading
from configparser import SafeConfigParser, NoSectionError
import asyncio
import sys
import ccxt
from CryptoGladiator.broker import Broker
from CryptoGladiator.errors import BrokerError
import logging
from ccxt import ExchangeError

log = logging.getLogger('Broker')
log.setLevel(logging.DEBUG)
logging.info("start logging")

quit_requested = False
mycounter = 0

# dict(config.items("Bitstamp"))
class CryptoGladiator(cmd.Cmd) :
    '''
    CryptoGladiator command line
    '''
    version = 'v0.01 beta'
    intro = "CryptoGladiator %s. I'm waiting for you command."%version
    prompt =  "G> "
    ruler = '-'
    start_time = 0
    tick = 0
    broker = None
    exchange = None # default exchange object

    def __init__(self):
        self.broker = Broker()
        super().__init__()

    def preloop(self):
        self.start_time = time.time()
        config = SafeConfigParser()
        config.read("CryptoGladiator.conf")
        exlist = config.get("Main", "exchanges")
        mngr = self.broker.manager
        for exname in [x.strip() for x in exlist.split(',')]:
            xchgconfig = dict(config.items(exname))
            self.exchange = mngr.get_exchange(exname, xchgconfig)

    def postloop(self):
        self.broker.manager.stop()

    def do_use(self, arg):
        "Change default exchange. use <exchange>"
        try:
            self.exchange = self.broker.manager.get_exchange(arg.strip())
        except BrokerError as e:
            print(e)

    def do_status(self, arg):
        'Report status information'
        td = time.time() - self.start_time
        days, secs = divmod(td, 60*60*24)
        hours,secs = divmod(secs, 60*60)
        minutes,secs = divmod(secs, 60)
        print(
                'Running time: {0:.0f} day {1:.0f} hours {2:.0f} mins {3:.1f} secs'
            .format(days,hours,minutes, secs)
        )
        print (f"Default exchange: {self.exchange.name}")

    def do_jobs(self,arg):
        'list active jobs'
        print(self.broker.manager.list_jobs())

    def do_symbols(self,arg):
        result = self.exchange.symbols
        print(result)

    def do_quit(self,arg):
        print("Weapons down. Peace.")
        return True

    def do_markets(self,arg):
        '''Get Trading pairs '''
        print(self.exchange.markets)
        #print( "{name:>8} {url_symbol:>8} {description}".format(**p) )

    def do_ticker(self,arg):
        '''Get ticker '''
        ticker = arg.strip()
        try:
            self.report(self.exchange.call("fetch_ticker",ticker))
        except ExchangeError as e:
            print(e)
        #print( "{name:>8} {url_symbol:>8} {description}".format(**p) )

    def do_balance(self,arg):
        "Active balance of the account"
        print("balance")

    def do_transactions(self,arg):
        "Show my transactions"
        print("transactions")

    def do_orders(self,arg):
        "Show Orders"
        print("orders")

    def do_order(self,arg):
        '''Report single order '''
        print("orders")

    def do_bids(self,arg):
        print("bids")

    def report(self,d):
        for k,v in d.items():
            print( "{key:>16}:{value!s:>16}".format(key=k,value=v))

    def table(self,table):
        if len(table) == 0 :
            print ("none")
            return

        keys = table[0].keys()
        header = "\t".join( keys )
        rowtemplate = "\t".join( [ '{'+k+'}' for k in keys] )

        print(header)
        for row in table :
            print( rowtemplate.format(**row) )


if __name__ == '__main__':
    CryptoGladiator().cmdloop()
