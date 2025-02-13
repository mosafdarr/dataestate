from scrapy import Request, Spider, Selector
from time import sleep

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from ...utils import to_scrape_urls, scroll_down_page


class BayutUAESpider(Spider):
    name = "BayutUAESpider"

    domain = "www.bayut.com"
    allowed_domains = ["www.bayut.com"]
    start_urls = ["https://www.bayut.com"]

    custom_settings = {
        "HTTPERROR_ALLOWED_CODES": [503, 200, 403, 429, 301],
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 3.0,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': None
        }
    }

    country = "UAE"
    currency = "AED"

    search_residential_for_sale_url = "https://www.bayut.com/for-sale/property/{0}"
    search_residential_to_rent_url = "https://www.bayut.com/to-rent/property/{0}"
    search_commercial_to_rent_url = "https://www.bayut.com/to-rent/commercial/{0}"
    search_commercial_for_sale_url = "https://www.bayut.com/for-sale/commercial/{0}"

    uae_properties = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = self.get_driver()

    def get_driver(self):
        """Get Selenium driver"""

        options = ChromeOptions()
        options.add_argument("--headless=new")
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
        """start scrapy request"""

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
        """Parse listing properties urls"""

        sleep(1)

        self.driver.get(kwargs.get("url"))
        self.search_properties(kwargs)
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

    def search_properties(self, kwargs):
        """Search properties with keywords"""

        try:
            search_input_field_css = '[aria-label="Location filter"] > input'
            input_element = self.driver.find_element(By.CSS_SELECTOR, search_input_field_css)
            input_element.clear()
            input_element.send_keys(kwargs.get("city"))

            sleep(1)

            input_element.send_keys(Keys.RETURN)
            return True
        except:
            return False

    def parse_property_details(self, response, **kwargs):
        """Parse property details"""

        self.driver.get(kwargs.get("url"))

        sleep(2)

        scroll_down_page(self.driver, scroll_increment=50, scroll_pause_time=3)
        resp = Selector(text=self.driver.page_source)
        parse_property = self.parse_propery_data(resp)
        self.uae_properties.append(parse_property)

    def parse_property_data(self, response):
        """parse property data"""

        return {
            "currency": self.currency,
            "title": self.parse_property_title(response),
            "url": self.parse_property_url(response),
            "description": self.parse_property_description(response),
            "total_price": self.parse_property_total_price(response),
            "images": self.parse_property_images(response),
            "property_info": self.parse_property_info(response),
            "developer": self.parse_property_developer_name(response),
            "building_info": self.parse_property_building_info(response),
            "amenities": self.parse_property_amenities(response),
            "regulatory_info": self.parse_property_regulatory_info(response),
            "broker_info": self.parse_property_broker_info(response)
        }

    def parse_property_title(self, response):
        """Parse property title """

    def parse_property_url(self, response):
        """Parse property detail page url"""

    def parse_property_description(self, response):
        """Parse property description"""

    def parse_property_total_price(self, response):
        """Parse property total price"""

    def parse_property_developer_name(self, response):
        """Parse property developer name"""

    def parse_property_amenities(self, response):
        """Parse property amenities names"""

    def parse_property_images(self, response) -> list:
        """Parse property images url"""

    def parse_property_broker_info(self, response):
        """Parse propery broker info"""

        return {
            "name": "",
            "phone": "",
            "email": "",
            "registration_no": "",
            "experience": "",
            "languages": [],
            "service_area": "",
            "description": ""
        }

    def parse_property_regulatory_info(self, response):
        """Parse property regulatory information"""

        return {
            "permit_no": "",
            "department_of_economic_development_no": "",
            "real_estate_regulatory_agency_no": "",
            "broker_registration_no": ""
        }

    def parse_property_building_info(self, response):
        """Parse property building information"""

        return {
            "building_name": "",
            "total_floors": "",
            "swimming_pools": "",
            "total_parking_space": "",
            "total_building_area": "",
            "parking_availability": "",
            "elevators": "",
            "location": self.parse_property_building_location(response)
        }

    def parse_property_building_location(response):
        """Parse property building location informtion"""

        return {
            "country": "",
            "city": "",
            "neighbourhood_places": [],
            "address": ""
        }

    def parse_property_info(self, response):
        """Parse property information"""

        return {
            "type": "Apartment/Flat/Studio..etc",
            "purpose": "for-sale/to-rent",
            "reference_no": "",
            "furnished": True,
            "added_date": "27-01-2025",
            "compeletion": "off-Plan/Ready",
            "handover_date": "Q4 2027",
            "ownership_type": "",
            "total_size": "",
            "bedrooms": "",
            "bathrooms": "",
            "service_charges": "",
            "usage": "",
            "avg_rent_generation": ""
        }

    def closed(self, reason):
        self.driver.quit()
