import asyncio
from asyncio import AbstractEventLoop
from aiohttp import ClientSession
import requests
from requests import Session
from lxml import html as lxml_html
from urllib.parse import urljoin

from colorama import Fore


def coroutine(fn):
    def inner(*args, **kwargs):
        g = fn(*args, **kwargs)
        next(g)
        return g
    return inner


@coroutine
def broadcast(targets):
    while True:
        data_row = yield
        for target in targets:
            target.send(data_row)


def xpath_root(page_source: str or bytes, base_url=None, parser=None) -> lxml_html.HtmlElement:
    return lxml_html.fromstring(html=page_source, base_url=base_url, parser=parser)


def get_first(list_elements):
    try:
        return list_elements.pop(0)
    except:
        return ''


def get_item(resp: str or bytes, path) -> str:
    """This gets the first item"""
    if isinstance(resp, requests.models.Response):
        return get_first(xpath_root(resp.content).xpath(path))
    else:
        return get_first(xpath_root(resp).xpath(path))

    # if isinstance(resp, requests.models.Response):
    #     yield get_first(xpath_root(resp.content).xpath(path))
    # else:
    #     yield get_first(xpath_root(resp).xpath(path))


def get_all(resp: str or bytes, path) -> list:
    """This gets the all items"""
    if isinstance(resp, requests.models.Response):
        return xpath_root(resp.content).xpath(path)
    else:
        return xpath_root(resp).xpath(path)

    # if isinstance(resp, requests.models.Response):
    #     yield xpath_root(resp.content).xpath(path)
    # else:
    #     yield xpath_root(resp).xpath(path)


def single_item(attributes: dict or None, path: str) -> str:
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


async def multi_link(loop: AbstractEventLoop, gen, path: str):
    tasks = []
    async with ClientSession(loop=loop) as session:
        for i, j in enumerate(gen):
            # print(Fore.MAGENTA, f'Page-{i + 1}: ', j.url, flush=True)
            urls = [urljoin(j.url, link) for link in xpath_root(j.content).xpath(path)]
            for url in urls:
                tasks.append(loop.create_task(fetch(session, url)))

        return await asyncio.gather(*tasks)

        # for task in asyncio.as_completed(tasks):
        #     earliest_result = await task
        #     yield earliest_result


async def fetch(session: ClientSession, url):
    print(Fore.CYAN + f"FETCHING PAGES: {url}", flush=True)
    async with session.get(url) as response:
        response.raise_for_status()
        html_body = await response.text()
        return html_body


def paginator(session: Session, url: str, path: str, output: list):
    resp = session.get(url)
    link = get_item(resp.content, path)
    output.append(resp)
    # link = next(link)  # turned getItem into gen for singleItem node

    yield resp
    if len(link) > 0:
        absolute_url = urljoin(url, link)
        print(Fore.GREEN, 'LINK:', absolute_url)
        yield from paginator(session, absolute_url, path, output)


# def paginator(session: Session, url: str, path: str) -> requests.Response:
#     resp = session.get(url)
#     link = get_item(resp.content, path)
#     # link = next(link)  # turned getItem into gen for singleItem node
#     yield resp
#     # print(Fore.GREEN, 'LINK:', link)
#     if len(link) > 0:
#         absolute_url = urljoin(url, link)
#         yield from paginator(session, absolute_url, path)

