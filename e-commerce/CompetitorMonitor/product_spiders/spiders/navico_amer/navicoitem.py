from datetime import date, datetime
import re

from scrapy.item import Item, Field
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import MapCompose, Join, TakeFirst, Identity
from scrapy.utils.markup import remove_entities

class NavicoMeta(Item):
    screen_size = Field()
    sub_category = Field()
    is_map = Field()
    is_mrp = Field()
    MAP = Field()
