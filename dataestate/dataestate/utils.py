from configs.db_queries import fetch_country_and_cities

def to_scrape_urls(url: str, country_name: str) -> list:
    """Takes url and country name to return all the cities appended in search url."""

    _, cities = fetch_country_and_cities(country_name)
    search_urls = [url.format(city) for city in cities]
    return search_urls, cities

def scroll_down_page(driver, scroll_pause_time=1, scroll_increment=500):
    """
    Scrolls the page bit by bit until the end.

    Args:
        driver (selenium.webdriver): The WebDriver instance controlling the browser.
        scroll_pause_time (int): Time to wait between scrolls.
        scroll_increment (int): The amount of pixels to scroll each time.
    """

    last_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0

    while current_position < last_height:
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        driver.implicitly_wait(scroll_pause_time)  # Wait for the page to load
        current_position += scroll_increment

        new_height = driver.execute_script("return document.body.scrollHeight")
        if current_position >= new_height:
            break

        last_height = new_height