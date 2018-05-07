import cmd, json, time
import threading
from bitstamp import client
from configparser import SafeConfigParser
import asincio

config = SafeConfigParser()
config.read("CryptoGladiator.conf")
api_key = config.get("Bitstamp", "api_key")
api_secret = config.get("Bitstamp", "api_secret")
user = config.get("Bitstamp", "user")

# dict(config.items("Bitstamp"))
class CryptoGladiator(cmd.Cmd) :
    version = 'v0.01 beta'
    intro = "CryptoBoxer %s. I'm waiting for you command."%version
    prompt =  "G> "
    ruler = '-'
    #api = client.Public()
    api = client.Trading(username=user, key=api_key, secret=api_secret)
    start_time = 0
    tick = 0

    def preloop(self):
        self._get_pairs()
        def timer_callback():
            self.tick += 1
            self._bgprocess = threading.Timer(2,timer_callback)
            self._bgprocess.start()
        timer_callback()
        self.start_time = time.time()

    def postloop(self):
        self._bgprocess.cancel()

    def do_info(self, arg):
        'Report status information'
        td = time.time() - self.start_time
        days, secs = divmod(td, 60*60*24)
        hours,secs = divmod(secs, 60*60)
        minutes,secs = divmod(secs, 60)
        print(
                'Running time: {0:.0f} day {1:.0f} hours {2:.0f} mins {3:.1f} secs'
            .format(days,hours,minutes, secs)
        )
        print("available trading pairs:", self.trading_pairs)

    def do_quit(self,arg):
        print("Weapons down. Peace.")
        return True

    def do_ticker(self,arg):
        '''Bitstamp ticker'''
        self.report( self.api.ticker() )

    def _get_pairs(self):
        '''Load trading pairs'''
        pairs = filter(lambda r: r['trading'] == "Enabled", self.api.trading_pairs_info())
        self.trading_pairs = [ p['url_symbol'] for p in pairs ]
        return pairs

    def do_pairs(self,arg):
        '''Get Trading pairs '''
        for p in self._get_pairs():
            print( "{name:>8} {url_symbol:>8} {description}".format(**p) )


    def do_balance(self,arg):
        "Active ballance of the account"
        balance = self.api.account_balance(base=None, quote=None)
        self.report(balance)

    def do_transactions(self,arg):
        "Show my transactions"
        raw = self.api.user_transactions()
        transactions = [ s for s in raw if s['type']=='2' ]
        #self.table(transactions)
        for l in transactions :
            print(l)

    def do_orders(self,arg):
        "Show Orders"
        base, quote = arg.strip().split("/")
        orders = self.api.open_orders(base, quote)
        self.table(orders)

    def do_order(self,arg):
        '''Report single order '''
        try:
            order = self.api.order_status(arg)
        except client.BitstampError as e :
            print(type(e),":",e)
        else:
            self.report(order)

    def do_bids(self,arg):
        "Show (relevant) bids"
        lastprice = float(self.api.ticker()['last'])
        allbids = self.api.order_book()['bids']
        okbids = [ b for b in allbids if abs( float(b[0])/lastprice - 1) < 0.01 ]
        print(okbids)

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

    loop = asincio.get_event_loop()


    CryptoGladiator().cmdloop()
