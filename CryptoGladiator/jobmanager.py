"""
ccxt exchange threading proxy implementation.
keeps running ccxt object in separate thread.
"""
from  logging import getLogger
import threading
import asyncio
import ccxt.async as ccxt
from .errors import BrokerError

log = getLogger('Broker')

class Exchange():
    """ccxt exchange wrapper"""

    name = ""
    # job manager
    manager = None
    exchange = None # ccxt exchange object

    def __init__(self, jobmanager, xchg_name, config={}):
        """Create ccxt exchange on job thread."""
        # job_processor shutdown event
        self.manager = jobmanager
        self.name = xchg_name
        self.config = config
        # run __init__ exchange on the new event loop
        try:
            async def initxchg():
                xchg = getattr(ccxt, self.name)(self.config)
                asyncio.ensure_future(xchg.load_markets())
                return xchg
            self.exchange = self.manager.run(initxchg()).result()

        except AttributeError as e:
            raise BrokerError("Unknown exchange: "+ str(self.name))

    def call(self, function_name, *args, **kwargs):
        ''' Call ccxt method syncronously. Returns value. '''
        return self.acall(function_name, *args, *kwargs).result()

    def acall(self, function_name, *args, **kwargs):
        '''
        Call ccxt method asyncronously, returns a Promise
        Schedule function call for an exchange in a thread loop
        '''
        try:
            corofn = getattr(self.exchange, function_name)
            log.debug("called function: %s", corofn)
            return self.manager.run(corofn(*args, **kwargs))

        except TypeError as e:
            raise BrokerError("Invalid ccxt method name: " + str(function_name))

class JobManager():
    """
    Async loop manager.
    Runs jobs in separate thread, provides async ccxt exchanges.
    Use context manager to cleanly shut down exchanges and pending jobs.
    """

    job_loop = None     # job processor async loop
    exchanges = {}      # open exchanges
    jobs = []           # list of active jobs

    def __init__(self):
        """Create new job queue in separate thread."""
        # job_processor shutdown event
        self.stopped = threading.Event()
        self.stopped.set()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def start(self):
        '''Start job processor in seaparate thread'''
        self.thread = threading.Thread(
            target=self.__job_processor,
            name="JobManagManager"
            )
        self.thread.start()
        self.stopped.clear()

        # wait (block) for loop start
        while not self.job_loop:
            pass

    def stop(self):
        '''stop job processor'''
        if self.stopped.is_set():
            log.warning("Jobmanager is not running, cannot be stopped.")

        log.debug("Setting shutdown signal.")
        # ask for shut down job loop (async.Event.set is not threadsafe)
        self.job_loop.call_soon_threadsafe(self.shutdown.set)

    def __job_processor(self):
        '''
        Thread function to process background jobs
        All ccxt market query must be called from
        this thread loop, including __init__.
        '''
        async def main():
            # wait for shutdown
            log.debug("Job processor is running.")
            await self.shutdown.wait()
            log.debug("Job processor got shutdown signal.")

        async def cleanup():
            # cancel all pending job
            for t in self.jobs: t.cancel()

            # close all exchanges
            xs = [
                x.exchange.close() for x in self.exchanges.values()
                if x.exchange is not None]
            log.debug("Waiting for exchanges to close.")
            await asyncio.gather(*xs)
            log.debug("Exchanges are closed.")

        self.job_loop = asyncio.new_event_loop()
        self.shutdown = asyncio.Event(loop=self.job_loop)
        asyncio.set_event_loop(self.job_loop)
        log.debug("Jobprocessor started.")
        try:
            self.job_loop.run_until_complete(main())

        except Exception as e:
            log.info("Jobthread exception catched: %s", e )

        finally:
            self.job_loop.run_until_complete(cleanup())
            self.job_loop.close()
            self.stopped.set()
            log.debug("Jobprocessor stopped.")

    def list_jobs(self):
        joblist = []
        for t in self.jobs:
            log.debug("job %s",t)
            job = {}
            job['error'] = t.exception()
            job['task'] = t
            joblist.append(job)
        return joblist

    def run(self, func):
        '''
        Async run. Schedule async function in a thread loop.
        Returns a Promise
        '''

        if not self.job_loop:
            raise RuntimeError("JobProcessor is not started.")

        try:
            future = asyncio.run_coroutine_threadsafe(func, self.job_loop)
            self.jobs.append(future)
            return future

        except Exception as e:
            log.error('Run exception captured: %s',e)

    def get_exchange(self,xchg_name, config={}):
        if xchg_name not in self.exchanges:
            self.exchanges[xchg_name] = Exchange(self, xchg_name, config)
        return self.exchanges[xchg_name]

    def list_exchanges(self):
        return list(self.exchanges.keys())
