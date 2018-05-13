import logging
from CryptoGladiator.exchangeproxy import ExchangeProxy
import asyncio
import time
import threading
import ccxt.async as ccxt
from ccxt.base.errors import ExchangeError

log = logging.getLogger('Broker')
log.setLevel(logging.DEBUG)
logging.info("start logging")

async def proba():
    await asyncio.sleep(2)
    log.debug ("slow proba at job thread: %s", threading.current_thread().getName())

log.debug ("main: %s",threading.current_thread().getName())

async def longwait():
    await asyncio.sleep(10)

with ExchangeProxy("bittrex") as xchg:
    log.debug("register job")

    try:
        xchg.arun(proba())

        # async method call
        ax = xchg.acall("fetch_ticker","ETH/BTC")

        # syncronous method call
        x = xchg.call("fetch_ticker","ETH/BTC")

        log.debug("sync: %s" , str(x))
        log.debug("async: %s" , str(ax.result()))

        xchg.arun(longwait())
        log.debug("3 sec timout")
        time.sleep(3)
        log.debug("3 sec timout is over")

    except ExchangeError as e:
        log.debug("Exception type:%s", type(e))
