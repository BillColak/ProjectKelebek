import asyncio
from asyncio import AbstractEventLoop
from aiohttp import ClientSession
import requests
from requests import Session
from lxml import html as lxml_html
from urllib.parse import urljoin
from colorama import Fore
import re

# TODO the functions in this file need a make over and optimization.


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


def get_item(resp: str or bytes, path, attributes: dict = None) -> str:
    """This gets the first item"""
    path = refactor_path_single_item(path, attributes)
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


async def multi_link(loop: AbstractEventLoop, gen, path: str):
    asyncio.set_event_loop(loop)  # TODO double check is this is the right thing to do with new_event_loops
    tasks = []
    # currently dont have to to this because nothing gets passed over until threads are done.
    # if isinstance(gen, ConcurrentFuture):
    #     gen = await wait_for(wrap_future(gen), None)

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


def get_numbers(value) -> float:
    if value:
        number = re.search(r'\d+\.\d+', value)
        return float(number.group())


def get_string(value) -> str:
    path = str(value).split('/')
    if [i for i in ['table', 'tbody', 'tr', 'td'] if i in path]:
        return "/".join(path[1:][-2:])
    else:
        if re.findall('\W', path[-1]):
            return path[-2] + '/' + str(re.findall(r"\b[a-zA-Z]+\b", path[-1])[0])
        else:
            return '/'.join([i.split('[')[0] for i in path[-2:]])


def get_string_item(value) -> str:
    path = str(value).split('/')
    if [i for i in ['table', 'tbody', 'tr', 'td'] if i in path]:
        return "/".join(path[-3:])
    else:
        return "/".join(path[-3:-1]) + '/' + path[-1].split('[')[0]


def refactor_path_single_item(path: str, attributes: dict = None) -> str:
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


def refactor_path_multi_item(path: str, attributes: dict = None) -> str:
    xpath_ = get_string(path)
    if attributes:
        attrib_xpath = [f'@{key}' for key in attributes.keys() if key != 'style']
        if len(attrib_xpath) > 0:
            return f'//{xpath_}[' + ' and '.join(attrib_xpath) + ']/text()'
        else:
            return f'//{xpath_}' + '/text()'
    else:
        return f'//{xpath_}' + '/text()'


def refactor_path_single_link(path: str, attributes: dict = None) -> str:
    xpath_ = get_string_item(path)
    if attributes:
        attrib_xpath = [f'normalize-space(@{key})="{value.strip()}"' for key, value in attributes.items() if
                        key != 'style']
        if len(attrib_xpath) > 0:
            return f'//{xpath_}[' + ' and '.join(attrib_xpath) + ']/@href'
        else:
            return f'//{xpath_}' + '/@href'
    else:
        return f'//{xpath_}' + '/@href'


def refactor_path_multi_link(path: str, attributes: dict = None) -> str:
    xpath_ = get_string(path)
    if attributes:
        attrib_xpath = [f'@{key}' for key in attributes.keys() if key != 'href' and key != 'style']
        if len(attrib_xpath) > 0:
            return f'//{xpath_}[' + ' and '.join(attrib_xpath) + ']/@href'
        else:
            return f'//{xpath_}' + ' and '.join(attrib_xpath) + '/@href'
    else:
        return f'//{xpath_}' + '/@href'


def refactor_path_pagination_xpath(text_value: str, path: str, attributes: dict = None) -> str:
    xpath_ = get_string(path)
    if attributes:
        attrib_xpath = [f'normalize-space(@{key})="{value.strip()}"' for key, value in attributes.items() if
                        key != 'href' and key != 'style']
        if len(attrib_xpath) > 0:
            return f'//{xpath_}[' + ' and '.join(attrib_xpath) + f' and normalize-space(text())="{text_value}"]/@href'
        else:
            return f'//{xpath_}[normalize-space(text())="{text_value}"]/@href'
    else:
        return f'//{xpath_}[normalize-space(text())="{text_value}"]/@href'
