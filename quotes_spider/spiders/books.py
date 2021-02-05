# from scrapy import Spider
# from scrapy.utils import project
# # from scrapy import spiderloader
# # from scrapy.utils.log import configure_logging
# from scrapy.crawler import CrawlerRunner, CrawlerProcess
# # from twisted.internet import reactor
# from scrapy.http import Request
#
# # TODO Calculate time required to fetch a single item.
# # TODO get API Item
# # file:///C:/Users/Owner/PycharmProjects/ScrapyGUI/zillow/zillow/spiders/asfas.JSON
#
# onion = []
# file_format = 'json'
# uri = 'test.json'
#
# def product_info(response, value):
#     return response.xpath('//th[text()="' + value + '"]/following-sibling::td/text()').extract_first()
#
# def pagination(path):
#     return path
# def link_item(item):
#     return item
#
#
# class QuotesSpider(Spider):
#     name = 'books'
#
#     custom_settings = {
#         'FEED_FORMAT': file_format,
#         'FEED_URI': uri
#     }
#
#     def __init__(self, *args, **kwargs):
#         super(QuotesSpider, self).__init__(*args, **kwargs)
#
#         self.allowed_domains = ['books.toscrape.com']  # maybe good for general spiders that to the py4e shit?
#         self.start_urls = ['http://books.toscrape.com/']
#
#
#     def parse(self, response, **kwargs):
#         books = response.xpath('//h3/a/@href').extract()
#         for book in books:
#             absolute_url = response.urljoin(book)
#             href = Request(absolute_url, callback=self.parse_book)  # this call back is weird isn't used for pagination?
#             yield href
#
#         # process next page
#         # next_page_url = response.xpath('//a[text()="next"]/@href').extract_first()
#         # absolute_next_page_url = response.urljoin(next_page_url)
#         # pagination = Request(absolute_next_page_url)
#         # yield pagination
#
#     def parse_book(self, response):
#         title = response.css('h1::text').extract_first()
#         price = response.xpath('//*[@class="price_color"]/text()').extract_first()
#
#
#         image_url = response.xpath('//img/@src').extract_first()
#         image_url = image_url.replace('../..', 'http://books.toscrape.com/')
#
#         rating = response.xpath('//*[contains(@class, "star-rating")]/@class').extract_first()
#         rating = rating.replace('star-rating ', '')
#
#         description = response.xpath(
#             '//*[@id="product_description"]/following-sibling::p/text()').extract_first()
#
#         # product information data points (TABLE)
#         upc = product_info(response, 'UPC')
#         product_type =  product_info(response, 'Product Type')
#         price_without_tax = product_info(response, 'Price (excl. tax)')
#         price_with_tax = product_info(response, 'Price (incl. tax)')
#         tax = product_info(response, 'Tax')
#         availability = product_info(response, 'Availability')
#         number_of_reviews = product_info(response, 'Number of reviews')
#
#         jimnjerry = {
#             'title': title,
#             'price': price,
#             'image_url': image_url,
#             'rating': rating,
#             'description': description,
#             'upc': upc,
#             'product_type': product_type,
#             'price_without_tax': price_without_tax,
#             'price_with_tax': price_with_tax,
#             'tax': tax,
#             'availability': availability,
#             'number_of_reviews': number_of_reviews
#         }
#         onion.append(jimnjerry)
#         yield jimnjerry
#
# # import scrapy
# #
# #
# # class PostsSpider(scrapy.Spider):
# #     name = "posts"
# #
# #     start_urls = [
# #         'https://blog.scrapinghub.com/'
# #     ]
# #
# #     def parse(self, response):
# #         for post in response.css('div.post-item'):
# #             yield {
# #                 'title': post.css('.post-header h2 a::text')[0].get(),
# #                 'date': post.css('.post-header a::text')[1].get(),
# #                 'author': post.css('.post-header a::text')[2].get()
# #             }
# #         next_page = response.css('a.next-posts-link::attr(href)').get()
# #         if next_page is not None:
# #             next_page = response.urljoin(next_page)
# #             yield scrapy.Request(next_page, callback=self.parse)
#
#
# if __name__ == '__main__':
#     process = CrawlerProcess()
#     process.crawl(QuotesSpider)
#     process.start()
#     print(len(onion))
#
