import os
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

HERE = os.path.abspath(os.path.dirname(__file__))


class JustVitaminsSpider(BaseSpider):
    name = 'justvitamins.co.uk-merckgroup'
    allowed_domains = ['www.justvitamins.co.uk', 'justvitamins.co.uk']
    start_urls = ('http://www.justvitamins.co.uk/A-Z-Product-Listing.aspx',)

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        # getting product links from A-Z product list
        links = hxs.select('//div[@class="Product"]/a/@href').extract()
        for prod_url in links:
            url = urljoin_rfc(get_base_url(response), prod_url)
            yield Request(url)

        # products
        for product in self.parse_product(response):
            yield product

    def parse_product(self, response):
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)

        name = hxs.select('//h1[@class="ProductDetails"]/text()').extract()
        if name:
            name = name[0].strip()
            url = response.url
            url = urljoin_rfc(get_base_url(response), url)
            items = hxs.select('//div[@class="Item"]')
            main_id = response.url.split('.aspx')[0].split('/')[-1]
            for item in items:
                loader = ProductLoader(item=Product(), selector=item)
                loader.add_value('url', url)
                sku = ''.join(item.select('./div[@class="Size"]/text()').extract())
                n = name
                if sku:
                    n += ' ' + sku.strip()
                identifier = main_id + '-' + sku.replace(' ','')

                loader.add_value('identifier', identifier)
                loader.add_value('identifier', identifier)

                loader.add_value('name', n)
                loader.add_xpath('price', './/span[@itemprop="price"]/text()')

                image_url = hxs.select('//td[@class="MainPhoto"]/a/img/@src').extract()
                if image_url:
                    image_url = urljoin_rfc(get_base_url(response), image_url[0])
                    loader.add_value('image_url', image_url)

                category = hxs.select('//div[@class="breadcrumbtrail"]/div/a/span/text()').extract()
                category = category[-1] if category else ''
                loader.add_value('category', category)
                stock = 'IN STOCK' in ''.join(item.select('div[@class="StockLevels"]/text()').extract()).upper()
                if not stock:
                    loader.add_value('stock', 0)
                
                yield loader.load_item()
