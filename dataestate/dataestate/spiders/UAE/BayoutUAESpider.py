from scrapy import Request, Spider, Selector

from seleniumbase import Driver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from time import sleep

from ...utils import to_scrape_urls, scroll_down_page


class BayoutUAESpider(Spider):
    name = "BayoutUAESpider"

    domain = "www.bayut.com"
    allowed_domains = ["www.bayut.com"]
    start_urls = ["https://www.bayut.com"]

    custom_settings = {
        "HTTPERROR_ALLOWED_CODES": [503, 200, 403, 429, 301],
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 3.0,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': None
        }
    }

    country = "UAE"

    search_residential_for_sale_url = "https://www.bayut.com/for-sale/property/{0}"
    search_residential_to_rent_url = "https://www.bayut.com/to-rent/property/{0}"
    search_commercial_to_rent_url = "https://www.bayut.com/to-rent/commercial/{0}"
    search_commercial_for_sale_url = "https://www.bayut.com/for-sale/commercial/{0}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = self.get_driver()

    def get_driver(self):
        options = ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = Chrome(options=options)
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setBlockedURLs', {
            'urls': ['https://analytics.twitter.com/1/i/adsct?bci=4&dv=*']
        })

        return driver

    def start_requests(self):
        residential_urls, cities = to_scrape_urls(self.search_residential_for_sale_url, self.country)
        for url, city in zip(residential_urls, cities):
            yield Request(
                url="http://quotes.toscrape.com/",
                callback=self.parse,
                dont_filter=True,
                cb_kwargs={"city": city, "url": url}
            )

        # TODO: scrape other 3 types of urls too.

    def parse(self, response, **kwargs):

        sleep(1)
        self.driver.get(kwargs.get("url"))
        self.driver.execute_script("window.stop();")

        search_input_field_css = '[aria-label="Location filter"] > input'
        input_element = self.driver.find_element(By.CSS_SELECTOR, search_input_field_css)

        input_element.clear()
        input_element.send_keys(kwargs.get("city"))
        sleep(1)

        input_element.send_keys(Keys.RETURN)

        resp = Selector(text=self.driver.page_source)
        property_urls_css = '[role=article] article > div > [aria-label="Listing link"]::attr(href)'
        property_urls = resp.css(property_urls_css).getall()

        for absolete_url in property_urls:
            relative_url = f"https://{self.domain}{absolete_url}"
            yield Request(
                url="http://quotes.toscrape.com/",
                callback=self.parse_property_details,
                dont_filter=True,
                cb_kwargs={"city": kwargs.get("city"), "url": relative_url}
            )

        next_page_url = resp.css("a[title=Next]::attr(href)").get()
        if next_page_url:
            yield Request(
                url="http://quotes.toscrape.com",
                callback=self.parse,
                dont_filter=True,
                cb_kwargs={"city": kwargs.get("city"), "url": f"https://{self.domain}{next_page_url}"}
            )

    def parse_property_details(self, response, **kwargs):
        self.driver.get(kwargs.get("url"))
        sleep(2)

        scroll_down_page(self.driver, scroll_increment=50, scroll_pause_time=3)
        resp = Selector(text=self.driver.page_source)

    def closed(self, reason):
        self.driver.quit()
