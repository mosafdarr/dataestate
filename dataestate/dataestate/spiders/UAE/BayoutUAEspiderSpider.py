from scrapy import Request, Spider

from configs.db_queries import fetch_country_and_cities


class BayoutUAEspiderSpider(Spider):
    name = "BayoutUAEspiderSpider"
    allowed_domains = ["www.bayut.com"]
    start_urls = ["https://www.bayut.com"]

    def start_requests(self):
        fetch_country_and_cities('UAE')

        # Proceed with your usual scraping logic
        urls = ['https://example.com']
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        pass
