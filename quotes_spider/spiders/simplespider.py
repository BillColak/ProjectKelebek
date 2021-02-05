import scrapy
from scrapy.crawler import CrawlerProcess
from quotes_spider.items import SpiderItemLoader
from scrapy import Request
from scrapy.settings import Settings
from spider.scrape import pagination_xpath, single_item, multi_link, multi_item

# from scrapy.utils.project import get_project_settings
# from functools import partial


DEBUG = True


class SimpleSpider(scrapy.Spider):

    tree_dict = None

    def __init__(self, *args, **kwargs):
        super(SimpleSpider, self).__init__(*args, **kwargs)
        self.follow_all_links_path = None
        self.item_dict = dict()

    def parse(self, response, **kwargs):
        _pagination = None
        # follow_all_links_path = None
        # item_dict = dict()

        if self.tree_dict:
            for row in self.tree_dict:
                if row['comboIndex'] == 2 or row['comboIndex'] == str(2):
                    _pagination = pagination_xpath(row['value'], row['attributes'], row['xpath'])
                    if DEBUG: print('Pagination: ', _pagination)
                if row['comboIndex'] == 4 or row['comboIndex'] == str(4):
                    follow_all_links_id = row['unique_id']
                    self.follow_all_links_path = multi_link(row['attributes'], row['xpath'])
                    if DEBUG: print('follow_links: ', self.follow_all_links_path)
                    for _items in self.tree_dict:
                        if follow_all_links_id == _items['parent_id']:
                            singleItem = single_item(_items['attributes'], _items['xpath'])
                            if DEBUG: print('Single Item: ', singleItem)
                            self.item_dict[_items.get('column_name', None)] = singleItem
            if self.follow_all_links_path:
                for i in self.parse_link(response, follow_link=self.follow_all_links_path, **self.item_dict):
                    yield i

            if _pagination:
                yield self.pagination(response, page=_pagination)

    def parse_link(self, response, follow_link=None, **kwargs):
        if follow_link:
            urls = response.xpath(follow_link).getall()
            for url in urls:
                yield response.follow(
                    url=response.urljoin(url),
                    callback=self.parse_item,
                    meta=kwargs
                )

    @staticmethod
    def pagination(response, page=None):
        if page:
            next_page_url = response.xpath(page).extract_first()
            absolute_next_page_url = response.urljoin(next_page_url)
            return Request(absolute_next_page_url)

    @staticmethod
    def parse_item(response, **kwargs):
        meta_items = response.request.meta.items()
        loader = SpiderItemLoader(response=response)
        for column, value in meta_items:
            if column != 'depth' and column != 'download_timeout' and column != 'download_slot' and column != 'download_latency':
                loader.add_value(column, response.xpath(value).get())
        yield loader.load_item()
    #
    # @staticmethod
    # def pagination_xpath(text_value: str, attributes: dict or None, path: str) -> str:
    #     xpath_ = "/".join(str(path).split('/')[1:][-int(2):])
    #     if attributes:
    #         attrib_xpath = [f'normalize-space(@{key})="{value.strip()}"' for key, value in attributes.items() if key != 'href' and key != 'style']
    #         if len(attrib_xpath) > 0:
    #             return f'//{xpath_}[' + ' and '.join(attrib_xpath) + f' and normalize-space(text())="{text_value}"]/@href'
    #         else:
    #             return f'//{xpath_}[normalize-space(text())="{text_value}"]/@href'
    #     else:
    #         return f'//{xpath_}[normalize-space(text())="{text_value}"]/@href'
    #
    # @staticmethod
    # def single_item(attributes: dict or None, path: str) -> str:
    #     xpath_ = "/".join(str(path).split('/')[1:][-int(2):])
    #     if attributes:
    #         attrib_xpath = [f'normalize-space(@{key})="{value.strip()}"' for key, value in attributes.items() if key != 'style']
    #         if len(attrib_xpath) > 0:
    #             return f'//{xpath_}[' + ' and '.join(attrib_xpath) + ']/text()'
    #         else:
    #             return f'//{xpath_}' + '/text()'
    #     else:
    #         return f'//{xpath_}' + '/text()'
    #
    # @staticmethod
    # def multi_item(attributes: dict or None, path: str) -> str:
    #     xpath_ = "/".join(str(path).split('/')[1:][-int(2):])
    #     if attributes:
    #         attrib_xpath = [f'@{key}' for key in attributes.keys() if key != 'style']
    #         if len(attrib_xpath) > 0:
    #             return f'//{xpath_}/[' + ' and '.join(attrib_xpath) + ']/text()'
    #         else:
    #             return f'//{xpath_}' + '/text()'
    #     else:
    #         return f'//{xpath_}' + '/text()'
    #
    # @staticmethod
    # def multi_link(attributes: dict or None, path: str) -> str:
    #     xpath_ = "/".join(str(path).split('/')[1:][-int(2):])
    #     if attributes:
    #         attrib_xpath = [f'@{key}' for key in attributes.keys() if key != 'href' and key != 'style']
    #         if len(attrib_xpath) > 0:
    #             return f'//{xpath_}[' + ' and '.join(attrib_xpath) + ']/@href'
    #         else:
    #             return f'//{xpath_}' + ' and '.join(attrib_xpath) + '/@href'
    #     else:
    #         return f'//{xpath_}' + '/@href'
    #
    # @staticmethod
    # def get_numbers(value) -> float:
    #     if value:
    #         number = re.search(r'\d+\.\d+', value)
    #         return float(number.group())
    #
    # @staticmethod
    # def get_string(value) -> str:
    #     path = str(value).split('/')
    #     if [i for i in ['table', 'tbody', 'tr', 'td'] if i in path]:
    #         return "/".join(path[1:][-int(2):])
    #     else:
    #         regex = re.findall(r"(?i)\b[a-zA-Z]+\b", value)
    #         return "/".join(regex[1:][-int(2):])


class SpiderRunner(SimpleSpider):
    name = 'simple_spider'

    allowed_domains = []
    start_urls = []

    # custom_settings = {
    #     'FEED_FORMAT': 'json',
    #     'FEED_URI': 'test.json'
    # }

    def __init__(self, *args, **kwargs):
        super(SpiderRunner, self).__init__(*args, **kwargs)

    @staticmethod
    def run_spider(file_format: str or None, uri: str or None, url, domains, tree_dict):
        SpiderRunner.tree_dict = tree_dict
        SpiderRunner.start_urls.append(url)
        SpiderRunner.allowed_domains.append(domains)
        crawler = CrawlerProcess(Settings({'FEED_FORMAT': file_format, 'FEED_URI': uri}))
        crawler.crawl(SpiderRunner)
        crawler.start()

# if __name__ == '__main__':
#     process = CrawlerProcess()
#     process.crawl(SpiderRunner)
#     process.start()

# SpiderRunner.run_spider(file_format=None,
#                         uri=None,
#                         url='http://books.toscrape.com/',
#                         domains='books.toscrape.com',
#                         tree_dict=my_data_full_path)


# from urllib.parse import urlparse
#
# SpiderRunner.run_spider(file_format='csv',
#                         uri='craigslist_honda.csv',
#                         url=craigs_list[0].get('url_name'),
#                         domains=urlparse(craigs_list[0].get('url_name')).netloc,
#                         tree_dict=craigs_list
#                         )





