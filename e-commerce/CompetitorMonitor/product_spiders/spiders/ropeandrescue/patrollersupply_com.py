from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from product_spiders.items import Product, ProductLoaderWithNameStrip as ProductLoader

class PatrollerSupplyComSpider(BaseSpider):
    name = 'patrollersupply.com'
    allowed_domains = ['patrollersupply.com']
    start_urls = ('http://www.patrollersupply.com/gear/category_index.asp',)

    def _start_requests(self):
        yield Request('http://www.patrollersupply.com/petzl/fire_rescue/exo_escape.asp', callback=self.parse_product)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//a[@class="tableLink"]/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product_list)

    def parse_product_list(self, response):
        hxs = HtmlXPathSelector(response)

        for url in hxs.select(u'//table[contains(@class,"tableStyleSummary")]/tr/td/a[last()]/@href').extract():
            url = urljoin_rfc(get_base_url(response), url)
            yield Request(url, callback=self.parse_product)

        next_url = hxs.select(u'//a[contains(text(),"View next page")]/@href').extract()
        if next_url:
            url = urljoin_rfc(get_base_url(response), next_url[0])
            yield Request(url, callback=self.parse_product_list)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        try:
            name = hxs.select(u'//h1/a/text()').extract()[-1].strip()
        except:
            try:
                name = hxs.select(u'//h1/text()').extract()[-1].strip()
            except:
                retry = int(response.meta.get('retry', 0))
                if retry < 10:
                    new_meta = response.meta.copy()
                    new_meta['retry'] = retry + 1
                    yield Request(response.url, meta=new_meta, callback=self.parse_product, dont_filter=True)
                    return
        price = hxs.select(u'//tr/td//font[starts-with(text(),"$")]/text()').extract()
        if price:
            price = price[0].split()[0]
        else:
            price = hxs.select(u'//tr/td[starts-with(text(),"Price:")]/text()').extract()
            if price:
                price = price[0].split('$')[-1]
            else:
                price = ''

        hxs = HtmlXPathSelector(response)

        category = hxs.select(u'//a[@class="linkHeading"]/text()').extract()
        if category:
            category = category[1].split(' - ')[0].strip()

        # For some products name does not change by selecting different options
        name_selected = hxs.select(u'//tr/td/select/option[@selected]/text()').extract()
        if name_selected:
            try:
                name += name_selected[0][name_selected[0].index('~') + 1:].strip()
            except:
                # http://www.patrollersupply.com/equipment/item_703.asp only price
                try:
                    name += name_selected[0][name_selected[0].index(' ') + 1:].strip()
                except:
                    pass

        sku = hxs.select(u'//tr/td[contains(text(),"SKU") or contains(text(),"Part #")]/text()').re("Part #\xa0(.+)$")

        product_loader = ProductLoader(item=Product(), selector=hxs)
        product_loader.add_value('url', response.url)
        product_loader.add_value('name', name)
        product_loader.add_value('price', price)
        product_loader.add_value('sku', sku)
        identifier = response.url.split('_')[-1].split('.asp')[0]
        product_loader.add_value('identifier', identifier)
        product_loader.add_value('category', category)
        img = hxs.select('//tr/td/img[contains(@src, "products")]/@src').extract()
        if img:
            img = urljoin_rfc(get_base_url(response), img[0])
            product_loader.add_value('image_url', img)
        product_loader.add_xpath('brand', u'//tr/td[contains(text(),"Manufacturer")]/../td[last()]/a/text()')
        product_loader.add_value('shipping_cost', '')
        yield product_loader.load_item()

        options = hxs.select(u'//tr/td/select/option/@value').extract()
        for opt in options:
            yield Request('http://www.patrollersupply.com/store/cart_item_review.asp?ID=' + opt, callback=self.parse_product)
