import scrapy
from scrapy.crawler import CrawlerProcess

from quotes_spider.items import SpiderItemLoader


class QuotesSpider(scrapy.Spider):
    name = 'books_version2'

    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    def parse(self, response, **kwargs):
        urls = response.css('.nav ul a::attr(href)').getall()
        for url in urls:
            yield response.follow(
                url,
                callback=self.parse_shelf,
            )

    def parse_shelf(self, response):
        urls = response.css('.image_container a::attr(href)').getall()
        for url in urls:
            yield response.follow(
                url,
                callback=self.parse_book,
            )

    def parse_book(self, response):
        loader = SpiderItemLoader(response=response)
        loader.add_css('name', 'h1::text')
        loader.add_css('price', '.price_color::text')
        yield loader.load_item()


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()
