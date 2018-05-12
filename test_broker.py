from CryptoGladiator.broker import Broker
import asyncio
import time
import threading
import ccxt.async as ccxt
from ccxt.base.errors import ExchangeError

async def proba():
    await asyncio.sleep(1)
    print ("job thread:",threading.current_thread().getName())

print ("main:",threading.current_thread().getName())

async def longwait():
    await asyncio.sleep(10)

async def poloniex_ticker():
    poloniex = ccxt.kraken()

    print(await poloniex.fetch_ticker('ETH/BTC'))
    await poloniex.close()
    raise Exception("Bakker 23423")
    print("miért nincs exception?")
    return "kaka"

with Broker() as b:
    print("register job")
    b.exchange_open("kraken")

    try:
        print("exchange list:",b.exchange_list())
        r = b.exchange_call("kraken","fetch_ticker","ETH/BTC")
        print("this is r: " ,r)
        print("queued")
        print(r.result())
        print("result got")

        #print("processor returns:", b.run_on_job_processor(poloniex_ticker()))
        time.sleep(4)

    #TODO: hogyan fogjuk el ezt? :ccxt.base.errors.ExchangeNotAvailable as e:
    # ccxt melyik modulja?
    except ExchangeError as e:
        print(type(e))
        print ("!!!!!!!!!!!! - gotcha. this was an exception.: " , str(e))

#with Broker() as broker:
#    broker.exchange_open("bitstamp")
#    print("ex list", broker.exchange_list())
#    print("ticker:",broker.ticker("bitstamp"))
