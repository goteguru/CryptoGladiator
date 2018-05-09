from CryptoGladiator.broker import Broker
import asyncio
import time
import threading
import ccxt.async as ccxt

async def proba():
    await asyncio.sleep(1)
    print ("job thread:",threading.current_thread().getName())
    return "ok"

print ("main:",threading.current_thread())

async def poloniex_ticker():
    poloniex = ccxt.poloniex()
    print(await poloniex.fetch_ticker('ETH/BTC'))
    await poloniex.close()

with Broker() as b:
    print("register job")
    r = b.run_on_job_processor(proba())
    print("queued")
    print(r.result())
    print("result got")

    print( b.run_on_job_processor(poloniex_ticker()))


#with Broker() as broker:
#    broker.exchange_open("bitstamp")
#    print("ex list", broker.exchange_list())
#    print("ticker:",broker.ticker("bitstamp"))
