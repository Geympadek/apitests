from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup, NavigableString

import asyncio
import re

def init_webdriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--webview-safebrowsing-block-all-resources")


    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.cookies": 1,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.plugins": 2
    }
    options.add_experimental_option("prefs", prefs)

    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    stealth(driver, platform="Win32")
    return driver

def clean_name(name: str):
    return re.sub(r"\s+", " ", name)

def parse_price(price_span):
    return int("".join([c if c.isdigit() else "" for c in price_span.text]))

def price_from_spans(priceSpans):
    count = len(priceSpans)
    
    price_span = None
    if count == 3:
        price_span = priceSpans[1]
    elif count == 2:
        price_span = priceSpans[0]
    else:
        raise SyntaxError(f"Number of price span is {count}, unexpected.")
    return parse_price(price_span)

async def get_price_and_name(driver: webdriver.Chrome, article: str | int):
    driver.get(f"https://ozon.ru/product/{article}")

    while "Antibot" in driver.title:
        await asyncio.sleep(0.5)

    raw_html = BeautifulSoup(driver.page_source, "html.parser")

    name_header = raw_html.find("h1")
    if not name_header:
        raise LookupError("Unable to find the main header.")

    name = clean_name(name_header.text)

    price_div = raw_html.find('div', {"data-widget": "webPrice"})
    price_spans = price_div.find_all('span', string=lambda text: text and '₽' in text)

    price = price_from_spans(price_spans)

    return name, price

async def main():
    driver = init_webdriver()

    for _ in range(2):
        article = input("Введите артикул товара")

        name, price = await get_price_and_name(driver, article)
        print(f"Название товара: {name}")
        print(f"Цена товара: {price}")

if __name__ == "__main__":
    asyncio.run(main())