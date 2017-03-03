# -*- coding: utf-8 -*-

import time
import asyncio
import uvloop
import aiohttp
import async_timeout

from websites import website_list

async def fetch(w, session):
    with async_timeout.timeout(10):
        start = time.time()
        async with session.get('{0}://{1}.{2}/{3}'.format(w['scheme'],w['prefix'],w['domain'],w['suffix'])) as response:
            trip = time.time() - start
            print("{0},{1},{2}".format(response.url, response.status, trip))
            #return await response.read()


async def bound_fetch(sem, website, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(website, session)


async def fetch_websites(websites):
    tasks = []
    # create instance of Semaphore and pass a request number limit
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we don't open a new connection
    # per each request.
    async with aiohttp.ClientSession() as session:
        for website in websites:
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, website, session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(fetch_websites(website_list))
loop.run_until_complete(future)

