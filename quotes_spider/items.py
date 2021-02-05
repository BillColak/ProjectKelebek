import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import Identity, TakeFirst, MapCompose
# from scrapy.loader.processors import TakeFirst, Identity, MapCompose
import re
from collections import defaultdict

#  https://stackoverflow.com/questions/5069416/scraping-data-without-having-to-explicitly-define-each-field-to-be-scraped?noredirect=1&lq=1


class AbstractItem(scrapy.Item):
    fields = defaultdict(scrapy.Field)

    def __setitem__(self, key, value):
        # all keys are supported  then how do you mapCompose this?
        self._values[key] = value


def get_numbers(value):
    if value:
        number = re.search(r'\d+\.\d+', value)
        return float(number.group())


# class SimpleSpiderItem(scrapy.Item):
#     """response does not go here, use SpiderItemLoader instead!"""
#     name = scrapy.Field()
#     price = scrapy.Field()


class SpiderItemLoader(ItemLoader):
    """add response to this"""
    # default_item_class = SimpleSpiderItem
    default_item_class = AbstractItem
    default_input_processor = Identity()
    default_output_processor = TakeFirst()

    # price_in = MapCompose(get_numbers)  # how to deal with this....
