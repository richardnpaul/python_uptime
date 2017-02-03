# -*- coding: utf-8 -*-

import time
import asyncio
import uvloop
from aiohttp import ClientSession


websites = [
    'http://www.google.co.uk',
    'http://www.bing.co.uk',
    'https://uk.yahoo.com',
    'http://www.bbc.co.uk',
    'https://www.sky.com',
    'https://www.richardnpaul.co.uk/foo',
]


async def fetch(url, session):
    start = time.time()
    async with session.get(url) as response:
        trip = time.time() - start
        print("{0},{1},{2}".format(response.url, response.status, trip))
        #return await response.read()


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session)


async def run(urls):
    tasks = []
    # create instance of Semaphore and pass a request number limit
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we don't open a new connection
    # per each request.
    async with ClientSession() as session:
        for url in urls:
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, url, session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(websites))
loop.run_until_complete(future)

