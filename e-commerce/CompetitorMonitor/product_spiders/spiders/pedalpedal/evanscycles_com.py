"""

Name: evanscycles.com
Account: CRC

IMPORTANT!!

- Please be careful, this spider will be blocked if you're not
- This spider use EvansCyclesBaseSpider
- Do not use BSM here. EvansCyclesBaseSpider uses a custom BSM

"""


from product_spiders.base_spiders import EvansCyclesBaseSpider


class EvansCyclesComSpider(EvansCyclesBaseSpider):
    name = 'evanscycles.com'
    extract_rrp = True