
import ccxt.async as ccxt
import asyncio


e = ccxt.bitstamp()

l = asyncio.get_event_loop()
res = l.run_until_complete(e.fetch_ticker('BTC/USD'))
l.run_until_complete(e.close())
print (res)
#print (e.markets)
#print (e.fetch_balance())
