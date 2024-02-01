import re
import time
import json

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

MAIN_URL = "https://samokat.ru"
CATEGORY_TEST_URL = \
    "https://samokat.ru/category/92f6c90d-e7ce-42b8-9b02-4203e6dec3f9"


def main() -> dict:
    with open("parser/data/all_categories_dict.json", "r", encoding='utf-8') as file:
        all_categories_dict = json.load(file)
    url = [i for i in all_categories_dict.values()][0]

    # you can choose 1 category from file categories.html,
    # or you can uncomment this part of code to make it for all categories
    # this part of code coming soon :D

    # Initialize the Chrome browser
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get(url)

    # Wait for the dynamic data to load
    WebDriverWait(driver, 5)

    html = driver.page_source

    time.sleep(3)

    # Close the browser
    driver.quit()

    # Create a BeautifulSoup object
    soup = BeautifulSoup(html, "lxml")

    # Find all elements with a class that matches the specified pattern,
    # i.e. category
    all_data_for_names = (
        soup.find_all(class_=re.compile("ProductsList_productList")))

    # Create the dictionary
    # to store products of category by names and their URLs
    products_dict = {}
    for data in all_data_for_names:
        for product in data:
            product_name = (
                product.find(class_=re.compile("ProductCard_name")).text.replace(" ", ' ').strip())
            product_link = 'https://samokat.ru' + product.get("href")
            products_dict[product_name] = product_link

    # Save the dictionary to a JSON file
    with open(f"parser/data/category_all_products.json", "w", encoding='utf-8') as file:
        json.dump(products_dict, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
