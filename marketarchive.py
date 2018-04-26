#
# Market Archive
#

from tradingpair import TradingPair
import time, datetime
import numpy as np
import pandas as pd 

class MarketException(Exception):
    pass

class MarketArchive(object) :
    
    archives = {}
    persistent = "./data/archive.h5"

    @staticmethod
    def _make_market_id(pair, exchange):
        return exchange.lower() + "_" + pair.ticker()

    @staticmethod
    def init(pair, exchange):
        """Factory method returning new or existing market archive"""
        marketid = MarketArchive._make_market_id(pair,exchange)
        if marketid in MarketArchive.archives: 
            return MarketArchive.archives[marketid]
        else: 
            return MarketArchive(pair,exchange)

    def __init__(self, pair, exchange):
        """Initialize archive from default file or create it empty"""
        if type(pair) is not TradingPair : 
            raise MarketException('Archive must be created for some TradingPair.')
        self.pair = pair
        self.exchange =  exchange
        try :
            self.load()
        except KeyError:
            self.archive = pd.DataFrame(columns=['price','volume','uid'], dtype=['f','f64','int64'])
            ix = pd.to_datetime(self.archive.index)
            ix.name = "ts"
            ix.freq = "S"
            self.archive.index = ix
        MarketArchive.archives[self.marketid] = self

    def marketid(self): 
        """Returns readable unique id for the market archive"""
        return MarketArchive._make_market_id(self.pair, self.exchange)

    def loadtxt(self,fn ):
        """ load text in the format of
        unixts,  price, volume
        1315922016,5.800000000000,1.000000000000
        """
        print("loading:",fn)
        self.archive = pd.read_csv(fn, 
                names=['ts', 'price', 'volume'] , 
                index_col=0, engine='c', 
                header=None
        )
        self.archive.index = pd.to_datetime(self.archive.index, unit='s')
        self.archive.index.freq=pd.tseries.offsets.Second(1) # set 1 sec freq
        self.archive['uid'] = np.nan # set uniq id column

        
    def load(self,fn=None):
        if fn == None : fn = self.persistent 
        self.archive = pd.read_hdf( fn, self.marketid() )

    def save(self,fn=None):
        fn = self.persistent if fn == None else fn
        self.archive.to_hdf(fn, self.marketid(), mode='w', complib='blosc')

    def timerange(self, start=0 , end=time.time()):
        return self.archive['ts'][-10:]
        
    def concat(self, df):
        """ append time data """
        # drop unneccessary data
        df = df[self.archive.index[-1]:].iloc[1]
        # alternatíva:
        # df = df[df.index > self.archive.index[-1]]
        return pd.concat( [self.archive, df] )

    def append(self, price, volume, time="now", uid=None):
        """Add one new line of data to the archive."""
        if uid is not None and uid in self.archive['uid'].values:
            return
        newline = [price, volume, uid]
        self.archive.loc[pd.Timestamp(time)] = newline

# TODO: TEST IT
    def last_update(self):
        """timestamp of the most recent available data"""
        return self.archive['ts'][-1:]

        
    ##### Archive indicators #####

    def raw(self):
        """ return the raw pandas timestamp indexed DataFrame. Ordered, multiple indexes.
        dataframe value axis: "price", "volume" 
        """
        return self.archive;

    def resample(self, freq='5T', start=0, end=None):
        """ minutes dataframe: OHLC+volume format """
        s = market.archive[start:end].resample(freq)
        low     = s["price"].min()
        high    = s["price"].max()
        close   = s["price"].last()
        open_   = s["price"].first()
        volume  = s["volume"].sum()
        m = pd.concat({'low':low,'high':high,'close':close,'open':open_,'volume':volume}, axis=1)
        return m 

# teszt
if __name__ == "__main__" :
    print("teszting...")
    from test_currencies import *

    market = MarketArchive.init(TradingPair(BTC,USD), "bitstamp")
    empty = MarketArchive.init(TradingPair(BTC,USD), "masik")
#    market.loadtxt("./data/bitstampUSD.csv")
#    market.save()



    


    
