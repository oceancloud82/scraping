from product_spiders.items import ProductLoaderWithNameStrip
from scrapy.contrib.loader.processor import MapCompose

class ProductLoader(ProductLoaderWithNameStrip):
    sku_in = MapCompose(unicode, unicode.strip, unicode.lower, lambda v: v.replace('-', ''), lambda v: v.replace(' ', ''))
