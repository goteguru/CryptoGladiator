import logging
from CryptoGladiator.jobmanager import JobManager
import asyncio
import time
import threading
import ccxt.async as ccxt
from ccxt.base.errors import ExchangeError

log = logging.getLogger('Broker')
log.setLevel(logging.DEBUG)
logging.info("start logging")

async def mini():
    await asyncio.sleep(0.2)
    return "mini"

async def proba():
    await asyncio.sleep(2)
    log.info ("Slow proba at job thread: %s", threading.current_thread().getName())
    raise Exception("bakkerError")
    log.debug ("slow proba at job thread: %s", threading.current_thread().getName())
    return "haha"

log.debug ("main: %s",threading.current_thread().getName())

async def longwait():
    await asyncio.sleep(10)

with JobManager() as manager:
    log.debug("register job")

    try:
        xchg = manager.get_exchange("kraken")
        print(manager.run(mini()).result())
        print(manager.run(mini()).result())
        print(manager.run(mini()).result())
        try:
            res = manager.run(proba())
            print(res.result())
        except Exception as e:
            log.debug("Test catched: %s", e)

        time.sleep(1)
        # async method call
        ax = xchg.acall("fetch_ticker","ETH/BTC")

        # syncronous method call
        x = xchg.call("fetch_ticker","ETH/BTC")

        log.debug("sync: %s" , str(x))
        log.debug("async: %s" , str(ax.result()))

        manager.run(longwait())
        log.debug("3 sec timout")
        time.sleep(3)
        log.debug("3 sec timout is over")

    except ExchangeError as e:
        log.debug("Exception type:%s", type(e))
        print(manager.list_jobs())
