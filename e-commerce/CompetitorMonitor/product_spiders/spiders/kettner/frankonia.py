import re
import functools

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc, add_or_replace_parameter
from scrapy.log import msg

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader
# from product_spiders.utils import extract_price

# HERE = os.path.dirname(os.path.abspath(__file__))


def comas2dots(s):
    if s:
        s[0] = s[0].replace(",", ".").replace(u'\xa0', '')
    return s

def first(s):
    if isinstance(s, list):
        return s[0]
    return s


class FrankoniaSpider(BaseSpider):

    name = 'frankonia.fr'
    allowed_domains = ['frankonia.fr']
    start_urls = ('http://www.frankonia.fr/marques-de-a-a-z/categorylist.html',)


    def parse(self, response):
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)

        categories = hxs.select("//ul[@id='topNav']//a/@href").extract()
        for url in categories:
            yield Request(urljoin_rfc(base_url, url), callback=self.parse_page)


    def parse_page(self, response):
        base_url = get_base_url(response)

        hxs = HtmlXPathSelector(response)
        cats = hxs.select("//ul[@id='nav']//a/@href").extract()
        for url in cats:
            url_ = add_or_replace_parameter(urljoin_rfc(base_url, url), 'pagingSize', '10000')
            yield Request(url_, callback=self.parse_page)

        # next page
        hxs = HtmlXPathSelector(response)
        url = hxs.select("//div[@class='pagerLine']//a[@class='next']/@data-query").extract()
        if url:
            url_ = add_or_replace_parameter(urljoin_rfc(base_url, url[0]), 'pagingSize', '10000')
            yield Request(url_, callback=self.parse_page)

        # products
        for z in hxs.select("//div[@class='products']//li"):
            # name = z.select(".//div[@class='detailsInnerWrap']/a[@class='name']/text()").extract()
            loader = ProductLoader(selector=z, item=Product())
            loader.add_xpath('identifier', "@data-product-url", first, re="articleNumber=(\d+)")
            loader.add_xpath('sku', "@data-product-url", first, re="articleNumber=(\d+)")
            loader.add_value('url', urljoin_rfc(base_url, z.select("@data-product-url").extract()[0].strip()))
            loader.add_xpath('name', ".//*[contains(@class, 'name')]/text()")
            loader.add_xpath('brand', ".//*[contains(@class, 'brand')]/text()")
            price = z.select(".//p[@class='price']/ins//text()") \
                    or z.select(".//p[@class='price']//text()") \
                    or z.select(".//p[@class='price']/del//text()")

            price = ''.join(price.extract()).replace(',', '.').replace(u'\xa0', '')
            loader.add_value('price', price)

            yield loader.load_item()
