import asyncio
import threading
import time

async def worker(param):
    tn = threading.current_thread()
    for i in range(5):
        print ("i'm a worker number", tn, param, i)
        await asyncio.sleep(1)
    return "result:"+str(param)

def spawner(loop):
    """worker spawner """
    results = []
    for w in [worker(i) for i in range(3)]:
        results.append(asyncio.run_coroutine_threadsafe(w, loop))
        #results.append(loop.create_task(w))
    for i in range(8):
        print("i'm the spawner from:", threading.current_thread())
        time.sleep(1)
    return results

print("my thread:",threading.current_thread())
loop = asyncio.get_event_loop()
spawner_thread = loop.run_in_executor(None, spawner, loop)
print(spawner_thread)
print ([r.result() for r in loop.run_until_complete(spawner_thread)])
loop.close()
