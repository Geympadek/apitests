from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

def init_webdriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")  # Recommended for running in headless
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems   
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--webview-safebrowsing-block-all-resources")

    driver = webdriver.Chrome(options=options)
    stealth(driver, platform="Win32")
    return driver

def get_price_and_name(article):
    driver = init_webdriver()
    driver.get(f"https://ozon.ru/product/{article}")

    while "Antibot" in driver.title:
        pass

    raw_html = BeautifulSoup(driver.page_source, "html.parser")

    name = raw_html.find("h1").text.replace('\n', "")

    driver.quit()

    priceDiv = raw_html.find('div', {"data-widget": "webPrice"})
    priceSpans = priceDiv.find_all('span', string=lambda text: text and '₽' in text)

    price = int("".join([c if c.isdigit() else "" for c in priceSpans[1].text]))

    return name, price

article = input("Введите артикул товара")

name, price = get_price_and_name(article)
print(f"Название товара: {name}")
print(f"Цена товара: {price}")