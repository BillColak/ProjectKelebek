from scrapy import Spider
from scrapy.http import Request
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from quotes_spider.items import SpiderItemLoader
from scrapy.utils import project
# from scrapy import spiderloader
# from scrapy.utils.log import configure_logging
# from twisted.internet import reactor
# from scrapy.spiders import Rule  # garbage
# from scrapy.linkextractors import LinkExtractor  # garbage

# TODO Calculate time required to fetch a single item.
# TODO get API Item

# .css selector just gets the xpath: descent-or-self::h1/text()
# .getall() gives a list of all items.
# https://stackoverflow.com/questions/46579130/passing-extra-arguments-to-scrapy-request

file_format = 'csv'
uri = 'test.csv'
pagination = False
link = False


def product_info(response, value):
    return response.xpath('//th[text()="' + value + '"]/following-sibling::td/text()').extract_first()


def multi_item(local_name: str, attributes: dict, path: str):
    attributes_ = attributes.copy()
    query_ = local_name
    if 'class' in attributes_.keys():
        query_ += '.' + attributes_['class'].replace(' ', '.')
        del attributes_['class']
    query_ += "".join([f'[{key}]' for key in attributes_.keys()])
    element_path = f'//{local_name}[' + ' and '.join([f'@{key}' for key in attributes.keys()]) + ']'
    return element_path


class QuotesSpider(Spider):
    name = 'books'

    custom_settings = {
        'FEED_FORMAT': file_format,
        'FEED_URI': uri
    }

    def __init__(self, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = ['books.toscrape.com']
        self.start_urls = ['http://books.toscrape.com/']

    def parse(self, response, **kwargs):  # must return a request
        loader = SpiderItemLoader(response)
        books = response.xpath('//h3/a/@href').extract()

        # if link:
        #     for book in books:
        #         absolute_url = response.urljoin(book)
        #         href = Request(absolute_url, callback=self.parse_book)  # this call back is weird isn't used for pagination?
        #         yield href
        # else:
        #     yield books
        #
        # # process next page
        # if pagination:
        #     next_page_url = response.xpath('//a[text()="next"]/@href').extract_first()
        #     absolute_next_page_url = response.urljoin(next_page_url)
        #     yield Request(absolute_next_page_url)

    def parse_book(self, response):
        title = response.css('h1::text').extract_first()
        price = response.xpath('//*[@class="price_color"]/text()').extract_first()

        # image_url = response.xpath('//img/@src').extract_first()
        # image_url = image_url.replace('../..', 'http://books.toscrape.com/')
        #
        # rating = response.xpath('//*[contains(@class, "star-rating")]/@class').extract_first()
        # rating = rating.replace('star-rating ', '')
        #
        # description = response.xpath(
        #     '//*[@id="product_description"]/following-sibling::p/text()').extract_first()
        #
        # # product information data points
        # upc = product_info(response, 'UPC')
        # product_type =  product_info(response, 'Product Type')
        # price_without_tax = product_info(response, 'Price (excl. tax)')
        # price_with_tax = product_info(response, 'Price (incl. tax)')
        # tax = product_info(response, 'Tax')
        # availability = product_info(response, 'Availability')
        # number_of_reviews = product_info(response, 'Number of reviews')

        jimnjerry = {
            'title': title,
            'price': price,
        #     'image_url': image_url,
        #     'rating': rating,
        #     'description': description,
        #     'upc': upc,
        #     'product_type': product_type,
        #     'price_without_tax': price_without_tax,
        #     'price_with_tax': price_with_tax,
        #     'tax': tax,
        #     'availability': availability,
        #     'number_of_reviews': number_of_reviews
        }
        # onion.append(jimnjerry)
        yield jimnjerry


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()

