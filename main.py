from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from time import time

from bs4 import BeautifulSoup, NavigableString

import asyncio
import re

t = 0
def start_timer():
    global t
    t = time()

def time_passed():
    return round(time() - t, 2)

def init_webdriver():
    options = Options()

    # run browser without opening a new window
    options.add_argument("--headless")
        
    # fixes a gpu error without fully disabling gpu
    options.add_argument("--disable-gpu-compositing")
    # suppresses SSL errors 
    options.add_argument("--ignore-certificate-errors")

    options.add_argument("--log-level=OFF") # disable console output
    
    # prevents browser from playing audio
    options.add_argument("--mute-audio")
    # prevents browser from loading images
    prefs = {
        "profile.managed_default_content_settings.images": 2
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    stealth(driver,
            platform="Win32",
            vendor="Google Inc.",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine")
    return driver

driver = init_webdriver()

def clean_name(name: str):
    return re.sub(r"\s+", " ", name).strip()

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

async def get_html_ozon(id: int):
    driver.get(f"https://ozon.ru/product/{id}")

    while "Antibot" in driver.title:
        await asyncio.sleep(0.5)
    
    return BeautifulSoup(driver.page_source, "html.parser")

async def get_price_and_name(driver: webdriver.Chrome, article: str | int):
    start_timer()
    raw_html = await get_html_ozon(article)
    print("got html code:", time_passed())

    name_header = raw_html.find("h1")
    if not name_header:
        raise LookupError("Unable to find the main header.")

    name = clean_name(name_header.text)

    price_div = raw_html.find('div', {"data-widget": "webPrice"})
    price_spans = price_div.find_all('span', string=lambda text: text and '₽' in text)

    price = price_from_spans(price_spans)

    return name, price

async def main():
    for _ in range(5):
        article = input("Введите артикул товара")
        # article = 1361717848

        name, price = await get_price_and_name(driver, article)
        print(f"Название товара: {name}")
        print(f"Цена товара: {price}")

if __name__ == "__main__":
    asyncio.run(main())