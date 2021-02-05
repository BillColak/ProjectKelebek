from scrapy import Spider
# from scrapy.utils import project
# from scrapy import spiderloader
# from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner, CrawlerProcess
# from twisted.internet import reactor
from scrapy.http import Request

onion = []
# yeet = []
# rudy = []


def product_info(response, value):
    return response.xpath('//th[text()="' + value + '"]/following-sibling::td/text()').extract_first()


class QuotesSpider(Spider):
    name = 'quotes'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    def parse(self, response, **kwargs):
        books = response.xpath('//h3/a/@href').extract()
        for book in books:
            absolute_url = response.urljoin(book)
            verynice = Request(absolute_url, callback=self.parse_book)
            # yeet.append(verynice)
            yield verynice

        # process next page
        next_page_url = response.xpath('//a[text()="next"]/@href').extract_first()
        absolute_next_page_url = response.urljoin(next_page_url)
        borat = Request(absolute_next_page_url)
        # rudy.append(borat)
        yield borat
        # h1_tag = response.xpath('//a[@title]').extract()
        # yield {'header_tag': h1_tag}

    def parse_book(self, response):
        title = response.css('h1::text').extract_first()
        price = response.xpath('//*[@class="price_color"]/text()').extract_first()

        image_url = response.xpath('//img/@src').extract_first()
        image_url = image_url.replace('../..', 'http://books.toscrape.com/')

        rating = response.xpath('//*[contains(@class, "star-rating")]/@class').extract_first()
        rating = rating.replace('star-rating ', '')

        description = response.xpath(
            '//*[@id="product_description"]/following-sibling::p/text()').extract_first()

        # product information data points
        upc = product_info(response, 'UPC')
        product_type =  product_info(response, 'Product Type')
        price_without_tax = product_info(response, 'Price (excl. tax)')
        price_with_tax = product_info(response, 'Price (incl. tax)')
        tax = product_info(response, 'Tax')
        availability = product_info(response, 'Availability')
        number_of_reviews = product_info(response, 'Number of reviews')

        jimnjerry = {
            'title': title,
            'price': price,
            'image_url': image_url,
            'rating': rating,
            'description': description,
            'upc': upc,
            'product_type': product_type,
            'price_without_tax': price_without_tax,
            'price_with_tax': price_with_tax,
            'tax': tax,
            'availability': availability,
            'number_of_reviews': number_of_reviews
        }
        onion.append(jimnjerry)
        yield jimnjerry


# scrapy startproject quotes_spider
# scrapy genspider quotes books.toscrape.com
# scrapy shell
# fetch('http://books.toscrape.com')
# view(response)
# h1_tag = response.xpath('//h1/text()').extract() in parse method.
# scrapy crawl quotes: run a spider
# -> there is 1050 response_received_count because 50 pagination
# scrapy
# scrapy
# response.xpath('//div[@id="not-exists"]/text()').get(default='not-found')
#


# if __name__ == '__main__':
#     process = CrawlerProcess()
#     process.crawl(QuotesSpider)
#     process.start()
#     print(len(onion), rudy[0], yeet[0])

