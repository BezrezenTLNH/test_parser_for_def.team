# this function is not done,
# because it's really problematic to make some good function
# without using proxies
# solution coming soon
import json
import time
import re
from datetime import date

import psycopg2
import psycopg2.extras
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

# Get the DB_URL from your environment file
# You should change in your build.sh file
# (format: {provider}://{user}:{password}@{host}:{port}/{db})
# example: DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/mydb
DATABASE_URL = "postgresql://postgres:444305@localhost:5432/postgres"

with open("parser/data/all_categories_dict.json",
          "r", encoding='utf-8') as file:
    all_categories_dict = json.load(file)


def main(all_categories_dict: dict = all_categories_dict) -> None:
    # this category will be an example
    category = [i for i in all_categories_dict.values()][0]

    # Initialize the Chrome browser
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get(category)

    # Wait for the dynamic data to load
    WebDriverWait(driver, 5)

    html = driver.page_source

    time.sleep(3)

    # Make HTML file to work with
    with open('parser/data/all_products_data.html',
              'w', encoding='utf-8') as file:
        file.write(html)

    # Close the browser
    driver.quit()

    time.sleep(3)

    # Open HTML file to take all data
    with open('parser/data/all_products_data.html',
              "r", encoding="utf-8") as file:
        src = file.read()

    # Create a BeautifulSoup object
    soup = BeautifulSoup(src, "lxml")

    all_products_data = soup.find_all(class_=re.compile("ProductCard_content"))

    # Connect to DB and fill it with our data
    conn = psycopg2.connect(DATABASE_URL)

    for product in all_products_data:
        # Get all data that we need
        product_name = (
            product.find(class_=re.compile("ProductCard_name")).text.strip())

        try:
            product_volume = (
                product.find(
                    class_=re.compile("ProductCard_details"))
                .find_all("span").text.strip())
        except Exception:
            product_volume = None

        try:
            product_old_price = (
                product.find(class_=re.compile("ProductCardActions_text"))
                .find_all("span")[1].text.strip())
        except Exception:
            product_old_price = None

        try:
            product_new_price = (
                product.find(class_=re.compile("ProductCardActions_text"))
                .find_all("span")[2].text.strip())
        except Exception:
            product_new_price = None

        with conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute('INSERT INTO products_quick_search (name, '
                        'volume, created_at, old_price, new_price)'
                        'VALUES (%s, %s, %s, %s, %s)',
                        ((product_name,
                          product_volume
                          if product_volume else None,
                          date.today().isoformat(),
                          product_old_price
                          if product_old_price else None,
                          product_new_price
                          if product_new_price else None)))
            conn.commit()
    # Close connection to DB
    conn.close()
    print('Parsing is done')


if __name__ == "__main__":
    main()
