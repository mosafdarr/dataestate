import scrapy


class BayoutuaespiderSpider(scrapy.Spider):
    name = "bayoutUAESpider"
    allowed_domains = ["www.bayut.com"]
    start_urls = ["https://www.bayut.com"]

    def parse(self, response):
        pass
