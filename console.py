import cmd, json, time
from configparser import SafeConfigParser, NoSectionError
import asyncio
import sys
import ccxt
from CryptoGladiator.broker import Broker
from CryptoGladiator.errors import BrokerError
import logging
from ccxt import ExchangeError, NetworkError
import os

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
        try:
            config.read("CryptoGladiator.conf")
            exlist = config.get("Main", "exchanges")
            mngr = self.broker.manager
            for exname in [x.strip() for x in exlist.split(',')]:
                xchgconfig = dict(config.items(exname))
                self.exchange = mngr.get_exchange(exname, xchgconfig)
        except NoSectionError:
            log.error("No main config section. See example file.")

    def postloop(self):
        self.broker.manager.stop()

    def do_use(self, arg):
        """
        use <exchange>
        Change default exchange.
        """
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
        print (f"Active exchange: {self.exchange.name}")
        xlist = ", ".join(self.broker.manager.exchanges.keys())
        print (f"Loaded exchanges: {xlist}")

    def do_jobs(self,arg):
        'list active jobs'
        jobs = self.broker.manager.list_jobs()
        for j in jobs:
            if j['error'] is not None:
                print ("!", j['task'], str(j['error'])[:50])
            else:
                print(" ", j['task'])

    def do_symbols(self,arg):
        result = self.exchange.exchange.symbols
        print(result)

    def do_currencies(self,arg):
        '''
        Report available currencies.
        '''
        curlist = ",".join(self.exchange.exchange.currencies.keys())
        print("currencies:", curlist)

    def do_quit(self,arg):
        print("Weapons down. Peace.")
        return True

    def do_reload(self,arg):
        '''
        Force reload default exchange (market info + currencies)
        '''
        try:
            print (self.exchange.call("load_markets", True))
        except ExchangeError as e:
            print(e)
        #print( "{name:>8} {url_symbol:>8} {description}".format(**p) )

    def do_markets(self,arg):
        '''Get Trading pairs '''
        try:
            for m in self.exchange.call("fetch_markets"):
                self.report({k:v for k,v in m.items() if k is not 'info'})
        except ExchangeError as e:
            print(e)
        #print( "{name:>8} {url_symbol:>8} {description}".format(**p) )

    def do_ticker(self,arg):
        '''Get ticker '''
        ticker = arg.strip().upper()
        try:
            self.report(self.exchange.call("fetch_ticker",ticker))
        except (ExchangeError, NetworkError) as e:
            print(e)
        #print( "{name:>8} {url_symbol:>8} {description}".format(**p) )

    def do_balance(self,arg):
        '''
        balance [free|used|total]
        Active, reserved and total balance of the account.
        '''
        if arg not in ("free", "used", "total"):
            arg = "free"

        try:
            result = self.exchange.call("fetch_balance")
        except ExchangeError as e:
            print(e)
        else:
            print(arg," balance:")
            self.report(result[arg])


    def do_transactions(self,arg):
        "Show my transactions"
        print("transactions")

    def do_orders(self,arg):
        '''
        orders [open]
        Show (open) orders.
        '''
        try:
            result = self.exchange.call("fetch_open_orders")
        except (ExchangeError, NetworkError) as e:
            log.error(e)
        else:
            self.table(result, without=["info","fee","average","timestamp"])

    def do_order(self,arg):
        '''
        order <orderid>
        Report single order
        '''
        oid = arg.strip()
        try:
            result = self.exchange.call("fetch_open_order", oid)
        except (ExchangeError, NetworkError) as e:
            log.error(e)
        else:
            self.report(result)

    def report(self,d):
        for k,v in d.items():
            print( "{key:>16}:{value!s:>16}".format(key=k,value=v))

    def table(self, table, without=[]):
        """Display list of dicts
        :table:     - list of dictionaries
        :without:   - list of masked (unneeded) keys
        """
        if len(table) == 0 :
            print ("No result")
            return

        # detect terminal size
        trows, tcolumns = map(int, os.popen('stty size', 'r').read().split())
        fields = [f for f in table[0].keys() if f not in without]

        # detect column widths
        widths = {k:0 for k in fields}
        for row in table:
            for key in fields:
                l = len(str(row[key]))
                if widths[key] < l:
                    widths[key] = min(30,l)
        log.debug("widths:%s", widths)
        log.debug("term:%s sumwidth:%s", tcolumns, sum(widths.values()))

        # normalise widths
        maxw = sum(widths.values()) + len(fields)
        if maxw > tcolumns:
            widths = {k: int(v/maxw*tcolumns) for k,v in widths.items()}

        log.debug("term:%s sumwidth:%s", tcolumns, sum(widths.values()))

        # display
        rowtemplate = "|".join(['{'+k+'!s:>'+str(w)+'.'+str(w)+'}' for k,w in widths.items()])
        log.debug("rowtemplate:%s", rowtemplate)
        print(rowtemplate.format(**{f:f for f in fields}))
        for row in table :
            print(rowtemplate.format(**row))

if __name__ == '__main__':
    CryptoGladiator().cmdloop()
