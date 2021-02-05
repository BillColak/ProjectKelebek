
# ASYNCHRONOUS MULTITHREADING RECURSIVE GENERATORS. YUP.
# https://github.com/mikeckennedy/async-await-jetbrains-webcast/blob/master/code/web_scraping/async_scrape/program.py
# https://github.com/tecladocode/complete-python-course/blob/master/course_contents/13_async_development/projects/async_scraping/app.py
# https://github.com/codingforentrepreneurs/30-Days-of-Python/blob/master/tutorial-reference/Day%2027/ascrape_sema.py
# ASYNCIO Overview: https://realpython.com/async-io-python/#the-10000-foot-view-of-async-io

# https://stackoverflow.com/questions/8991840/recursion-using-yield
# https://stackoverflow.com/questions/8991840/recursion-using-yield?noredirect=1&lq=1
# https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do?page=2&tab=oldest#tab-top
# https://docs.python.org/3/library/itertools.html#itertools.chain.from_iterable
# https://hackernoon.com/threaded-asynchronous-magic-and-how-to-wield-it-bba9ed602c32
# async generators from TRIO: https://github.com/python-trio/async_generator

# TODO asyncio.Semaphore(10), asyncio.ensure_future, asyncio.Queue, run_coroutine_threadsafe()
#  for coro in as_completed(aws):, earliest_result = await coro, call_later, call_soon,

# Note: can make pagination more intelligent by predicting upcoming pages and asyncranously requesting the predictions.
# if exception is raised retry with new request/headers/cookies.
# it can return/yield one of the given parameter.
# can use partial to input parameters in a pipeline like manner.

# callbacks: A subroutine function which is passed as an argument to be executed at some point in the future.
# gather groups given tasks and allows for cancellation, wait gives a "promise"

# see for thread_safe: https://hackernoon.com/threaded-asynchronous-magic-and-how-to-wield-it-bba9ed602c32

# asyncio.run(main()) instead of run_until_complete? the difference is " run_until_complete allows
# loop.is_running().is_closed() and scheduling callbacks with loop.call_later()"
# loop.run_until_comp is faster than asyncio.run(main())
# ^ https://docs.python.org/3/library/asyncio-eventloop.html#asyncio-example-lowlevel-helloworld in this example
# their literally using the recursive pagination that I am using but they do another example with a while loop.

# resp.raise_for_status(), fetch_html() is a wrapper around a GET request to make the request and decode the
# resulting page HTML. It makes the request, awaits the response, and raises right away in the case of a non-200 status:
# Notably, there is no exception handling done in this function.
# The logic is to propagate that exception to the caller and let it be handled there: the 10000 foot overview
# of async has error handling for parsing absolute urls as well.
# Remember: any line within a given coroutine will block other coroutines unless that line uses yield, await, or return.
# and If the parsing was a more intensive process, you might want to consider running this portion in its own process
# with loop.run_in_executor().
# related pages: https://docs.python.org/3/library/asyncio-eventloop.html#asyncio-example-lowlevel-helloworld,
# https://docs.python.org/3/library/asyncio-task.html#asyncio-example-sleep
# apparently you can check if a recursive crawler has requested the
#
# asyncio.as_completed() requires create_tasks and its some sort of an itirator of these tasks?

# TODO https://github.com/talkpython/async-techniques-python-course

# JARGON: Parallelism = computation/multiprocessing(math), concurrency = broader than parallelism, is the ability to
# run in overlapping manner. multithreading = GIL, threads take turns in exec. IO-bound tasks.
# Parallelism is a specific type (subset) of concurrency.
# The asyncio.create_task() function to run coroutines concurrently as asyncio Tasks. ***runs coroutines***
# There are three main types of awaitable objects: coroutines, Tasks, and Futures.
# Finally, when you use await f(), it’s required that f() be an object that is awaitable.

#         async def nested():
#             return 42
#
#         async def main():
#             # Schedule nested() to run soon concurrently
#             # with "main()".
#             task = asyncio.create_task(nested())
#
#             # **** "task" can now be used to cancel "nested()", or ****
#             # **** can simply be awaited to wait until it is complete: ****
#             await task

# yielding the results/tasks if it is connected to the socket. else gather tasks.
# Note apparently semaphores are not thread safe
# should not go same url more than once, if fails should retry max 5 times.
# if asyncio.run(main()) then can't run_until_comp, or as completed?

# TODO: Design issues. The multi_link function can just provide the url or the response.
#  depending on delegating the responsibility. Problem is item nodes very to make requests that would be very slow.

# loop.call_soon(functools.partial(print, "Hello World", flush=True))
# TO use key word args such as flush=True, have to use partial.
# if you dont have kwargs then, loop.call_soon(print, "Hello World") is fine.
# https://docs.python.org/3/library/asyncio-eventloop.html#examples
# https: // docs.python.org / 3 / library / asyncio - eventloop.html  # display-the-current-date-with-call-later
# loop.call_soon_threadsafe()
# loop.call_later() returns timehandler object to cancel the callback, loop.time()

# https://github.com/josnin/django-whatsapp-web-clone whatsapp clone


import asyncio
from asyncio import AbstractEventLoop, Semaphore
from aiohttp import ClientSession
from colorama import Fore
import time
from lxml import html as lxml_html
from urllib.parse import urljoin
import requests


multi_title_path = '//h3/a/@href'
title_path = '//h1/text()'
page_url = 'http://books.toscrape.com/'
pagination_path = '//a[text()="next"]/@href'
#
# price_full_path = '/html/body/div/div/div[2]/div[2]/article/div[1]/div[2]/p[1]'
# attribute = {"class": "price_color"}
#
price_path = '//div[1]/div[2]/p[normalize-space(@class)="price_color"]/text()'


def xpath_root(page_source: str or bytes, base_url=None, parser=None) -> lxml_html.HtmlElement:
    return lxml_html.fromstring(html=page_source, base_url=base_url, parser=parser)


def get_first(list_elements):
    try:
        return list_elements.pop(0)
    except:
        return ''


def single_item(attributes: dict or None, path: str) -> str:
    """USE THIS SHIT IF YOU HAVE FULL XPATH"""
    xpath_ = get_string_item(path)
    if attributes:
        attrib_xpath = [f'normalize-space(@{key})="{value.strip()}"' for key, value in attributes.items() if
                        key != 'style']
        if len(attrib_xpath) > 0:
            return f'//{xpath_}[' + ' and '.join(attrib_xpath) + ']/text()'
        else:
            return f'//{xpath_}' + '/text()'
    else:
        return f'//{xpath_}' + '/text()'


def get_string_item(value) -> str:
    path = str(value).split('/')
    if [i for i in ['table', 'tbody', 'tr', 'td'] if i in path]:
        return "/".join(path[-3:])
    else:
        return "/".join(path[-3:-1]) + '/' + path[-1].split('[')[0]


def get_item(resp: str or bytes, path: str) -> str:
    return get_first(xpath_root(resp).xpath(path))


def adriatique(url: str, path: str) -> requests.Response:
    with requests.Session() as client:
        for response in fast_paginator(client, url, path):
            yield response
        client.close()


def fast_paginator(session: requests.Session, url: str, path: str)->requests.Response:
    resp = session.get(url)
    yield resp
    link = get_item(resp.content, path)
    if len(link) > 0:
        absolute_url = urljoin(url, link)
        yield from fast_paginator(session, absolute_url, path)


def main():
    loop = asyncio.get_event_loop()
    gen = adriatique(page_url, pagination_path)
    x = loop.run_until_complete(multi_link(loop, gen, multi_title_path))
    # print(x)
    for i in x:
        price = get_item(i, price_path)
        title = get_item(i, title_path)
        print(Fore.WHITE + f"BOOKS PRICE: {price} {title}", flush=True)


async def multi_link(loop: AbstractEventLoop, gen, path: str):
    tasks = []
    async with ClientSession(loop=loop) as session:
        for i, j in enumerate(gen):
            print(Fore.MAGENTA, f'Page-{i + 1}: ', j.url, flush=True)
            urls = [urljoin(j.url, link) for link in xpath_root(j.content).xpath(path)]
            for url in urls:
                tasks.append(loop.create_task(fetch(session, url)))

        return await asyncio.gather(*tasks)
        # for task in asyncio.as_completed(tasks):
        #     earliest_result = await task
        #     return earliest_result
            # price = get_item(earliest_result, price_path)
            # title = get_item(earliest_result, title_path)
            # print(Fore.WHITE + f"BOOKS PRICE: {price} {title}", flush=True)


async def fetch(session: ClientSession, url):
    print(Fore.CYAN + f"FETCHING PAGES: {url}", flush=True)
    async with session.get(url) as response:
        response.raise_for_status()
        html_body = await response.text()
        return html_body


if __name__ == '__main__':
    start_time = time.time()
    main()
    print(Fore.MAGENTA + 'Time: ', time.time() - start_time)


# page = requests.get(page_url)
# links = [urljoin(page_url, link) for link in xpath_root(page.content).xpath(multi_title_path)]
# print(Fore.CYAN + "RETRIEVED LINKS", flush=True)


# NOT DONE
# async def async_paginator(session: ClientSession, url: str, path: str):
#     async with session.get(url) as resp:
#         resp.raise_for_status()
#         html_body = await resp.text()
#         link = get_item(html_body, path)
#         if len(link) > 0:
#             absolute_url = urljoin(url, link)
#             print("ASYNC PAGINATOR: ", absolute_url)
#             yield resp
#             yield async_paginator(session, absolute_url, path)


# def main():
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(multi_link(loop, links))
#
#
# async def multi_link(loop: AbstractEventLoop, urls: list):
#     tasks = []
#     async with ClientSession(loop=loop) as session:
#         for url in urls:
#             tasks.append(loop.create_task(fetch(session, url)))
#
#         for task in asyncio.as_completed(tasks):  # this yields the resp, so gathering in a list doesn't make sense.
#             earliest_result = await task
#             price = get_item(earliest_result, price_path)
#             print(Fore.WHITE + f"BOOKS PRICE: {price}", flush=True)
#             # return await asyncio.gather(*tasks)
#
#
# async def fetch(session: ClientSession, url):
#     print(Fore.CYAN + f"FETCHING PAGES: {url}", flush=True)
#     async with session.get(url) as response:
#         response.raise_for_status()
#         html_body = await response.text()
#         return html_body


# V1
# def adriatique():
#     with requests.Session() as client:
#         for i, j in enumerate(fast_paginator(client, page_url, pagination_path)):
#             print(Fore.MAGENTA, f'Page-{i+2}: ', j, flush=True)
#         client.close()
#
#
# def fast_paginator(session: requests.Session, url: str, path: str) -> str:
#     resp = session.get(url)
#     link = get_item(resp.content, path)
#     if len(link) > 0:
#         absolute_url = urljoin(url, link)
#         yield absolute_url
#         yield from fast_paginator(session, absolute_url, path)

# V2
# def adriatique():
#     with requests.Session() as client:  # this is gonna be async function
#         for i, j in enumerate(fast_paginator(client, page_url, pagination_path)):
#             print(Fore.MAGENTA, f'Page-{i+2}: ', j, flush=True)
#         client.close()
#
#
# def fast_paginator(session: requests.Session, url: str, path: str) -> str:
#     resp = session.get(url)  # can pass in tuple here with resp and url to capture the values
#     link = get_item(resp.content, path)
#     if len(link) > 0:
#         absolute_url = urljoin(url, link)
#         yield absolute_url
#         yield from fast_paginator(session, absolute_url, path)
#
# V3 FAIL
# # trying to use aiohttp sessions and accessing pagination responses at the same time.
#
# async def adriatique():
#     async with ClientSession() as client:
#         for i, j in enumerate(fast_paginator(client, page_url, pagination_path)):
#             print(Fore.MAGENTA, f'Page-{i+2}: ', j, flush=True)
#         # client.close()
#
#
# async def fast_paginator(session: ClientSession, url: str, path: str):  # -> str:
#     async with session.get(url) as response:
#         response.raise_for_status()
#         resp = await response.text()
#         for i in resp:  # for loop here to by pass the fuicking await
#             link = get_item(i, path)
#             if len(link) > 0:  # create tasks with ensured futures?
#                 absolute_url = urljoin(url, link)
#                 yield absolute_url
#                 yield await fast_paginator(session, absolute_url, path)  # for loop?
#             # for x in fast_paginator(session, absolute_url, path):
#             #     yield x
#
#
# async def pagination_callback(resp):
#     pass

# V4 Access from outside
# def adriatique():
#     with requests.Session() as client:
#         for j in fast_paginator(client, page_url, pagination_path):
#             yield j
#         client.close()
#
#
# def fast_paginator(session: requests.Session, url: str, path: str) -> str:
#     resp = session.get(url)
#     link = get_item(resp.content, path)
#     if len(link) > 0:
#         absolute_url = urljoin(url, link)
#         yield absolute_url
#         yield from fast_paginator(session, absolute_url, path)
#
# if __name__ == '__main__':
#     start_time = time.time()
#     # main()
#     for i, j in enumerate(adriatique()):
#         print(Fore.MAGENTA, f'Page-{i + 2}: ', j, flush=True)
#     print(Fore.MAGENTA + 'Time: ', time.time() - start_time)

# V5 GOOD SHIT
# def adriatique(url: str, path: str) -> tuple:
#     with requests.Session() as client:
#         for link, response in fast_paginator(client, url, path):
#             yield link, response
#         client.close()
#
#
# def fast_paginator(session: requests.Session, url: str, path: str) -> tuple:
#     resp = session.get(url)
#     html_body = resp.content
#     link = get_item(html_body, path)
#     if len(link) > 0:
#         absolute_url = urljoin(url, link)
#         yield absolute_url, html_body
#         yield from fast_paginator(session, absolute_url, path)
#
# if __name__ == '__main__':
#     start_time = time.time()
#     # main()
#     for i, j in enumerate(adriatique(page_url, pagination_path)):
#         print(Fore.MAGENTA, f'Page-{i + 2}: ', j[0], flush=True)
#     print(Fore.MAGENTA + 'Time: ', time.time() - start_time)
