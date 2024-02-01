import json
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

MAIN_URL = "https://samokat.ru"


def main(url: str = MAIN_URL) -> dict:
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get(url)

    # Wait for the dynamic data to load
    WebDriverWait(driver, 5)

    html = driver.page_source

    with open('parser/data/categories.html', 'w', encoding='utf-8') as file:
        file.write(html)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(html, "lxml")

    # Find all elements with a class that matches the specified pattern,
    # i.e. category
    all_categories = soup.find_all(class_=re.compile("CategoryLink_root"))

    # Create the dictionary to store category names and their URLs
    all_categories_dict = {}

    # Iterate through each category element and construct its URL,
    # deleting all unnecessary symbols and put it in dict
    for category in all_categories:
        category_text = category.text.replace(" ", ' ').strip()
        category_url = "https://samokat.ru" + category["href"]
        all_categories_dict[category_text] = category_url

    # Save the dictionary to a JSON file
    with open("parser/data/all_categories_dict.json",
              "w", encoding='utf-8') as file:
        json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
