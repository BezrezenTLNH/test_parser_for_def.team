# this function is not done,
# because it's really problematic to make some good function
# without using proxies
# solution coming soon
import json
import re
import time
from datetime import date

import psycopg2
import psycopg2.extras
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

MAIN_URL = "https://samokat.ru"
CATEGORY_TEST_URL = \
    "https://samokat.ru/category/92f6c90d-e7ce-42b8-9b02-4203e6dec3f9"

# Qty of iterations of this parser just to check the stability of it
TEST_LIMITS = 16

# Get the DB_URL from your environment file
# You should change in your build.sh file
# (format: {provider}://{user}:{password}@{host}:{port}/{db})
# example: DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/mydb
DATABASE_URL = "postgresql://postgres:444305@localhost:5432/postgres"

with open("parser/data/category_all_products.json", "r", encoding='utf-8') as file:
    products_dict = json.load(file)


def main(products_dict: dict = products_dict) -> None:
    # Make limit for test start
    limit = 0

    # Connect to DB and fill it with our data
    conn = psycopg2.connect(DATABASE_URL)

    while limit < TEST_LIMITS:
        for product_link in products_dict.values():
            chrome_options = Options()
            user_agent = UserAgent()
            chrome_options.add_argument(f"user-agent={user_agent.random}")

            # Initialize the Chrome browser
            driver = webdriver.Chrome(options=chrome_options)

            # Open the webpage
            driver.get(product_link)

            # Wait for the dynamic data to load
            WebDriverWait(driver, 3)

            # Get data from product
            product_src = driver.page_source

            # Close the browser
            driver.quit()

            # Create a BeautifulSoup object
            soup = BeautifulSoup(product_src, "lxml")

            # Get all data that we need
            product_name = (
                soup.find(class_=re.compile("ProductTitle_title")).find
                ("h1").text.strip())

            product_volume = (
                soup.find(class_=re.compile("ProductTitle_title")).find
                ("span").text.strip())

            try:
                product_highlights = ", ".join(
                    [i.text.strip() for i in
                     soup.find(class_=re.compile("ProductHighlights_root"))
                     .find_all("span")])
            except Exception:
                product_highlights = None

            try:
                product_marketing_description = (
                    soup.find(class_=re.compile("ProductDescription_description"))
                    .find("div").text.strip())
            except Exception:
                product_marketing_description = None

            try:
                product_cpfs = {
                    "calories": soup.find(
                        class_=re.compile("ProductNutritions_nutrition"))
                    .find_all("span")[1].text.strip(),

                    "proteins": soup.find(
                        class_=re.compile("ProductNutritions_nutrition"))
                    .find_all("span")[3].text.strip(),

                    "fats": soup.find(
                        class_=re.compile("ProductNutritions_nutrition"))
                    .find_all("span")[5].text.strip(),

                    "carbohydrates": soup.find(
                        class_=re.compile("ProductNutritions_nutrition"))
                    .find_all("span")[7].text.strip()
                }
            except Exception:
                product_cpfs = {
                    "calories": None,

                    "proteins": None,

                    "fats": None,

                    "carbohydrates": None
                }

            try:
                product_composition = (
                    soup.find(class_=re.compile("ProductAttributes_attributes"))
                    .find_all("span")[1].text.strip())
            except Exception:
                product_composition = None

            try:
                product_shelf_life = (
                    soup.find(class_=re.compile("ProductAttributes_attributes"))
                    .find_all("span")[3].text.strip())
            except Exception:
                product_shelf_life = None

            try:
                product_storage_conditions = (
                    soup.find(class_=re.compile("ProductAttributes_attributes"))
                    .find_all("span")[5].text.strip())
            except Exception:
                product_storage_conditions = None

            try:
                product_manufacturer = (
                    soup.find(class_=re.compile("ProductAttributes_attributes"))
                    .find_all("span")[7].text.strip())
            except Exception:
                product_manufacturer = None

            product_old_price = (
                soup.find(class_=re.compile("ProductCardActions_text"))
                .find_all("span")[1].text.strip())

            try:
                product_new_price = (
                    soup.find(class_=re.compile("ProductCardActions_root"))
                    .find_all("span")[2].text.strip())
            except Exception:
                product_new_price = None

            with conn.cursor(
                    cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute('INSERT INTO products_deep_search (name, '
                            'volume, created_at, highlights,'
                            ' marketing_description, calories, proteins,'
                            ' fats, carbohydrates, composition, shelf_life, '
                            'storage_conditions, manufacturer,'
                            ' old_price, new_price)'
                            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s,'
                            ' %s, %s, %s, %s, %s, %s, %s)',
                            ((product_name,
                              product_volume
                              if product_volume else None,
                              date.today().isoformat(),
                              product_highlights
                              if product_highlights else None,
                              product_marketing_description
                              if product_marketing_description else None,
                              product_cpfs['calories']
                              if product_cpfs['calories'] else None,
                              product_cpfs['proteins']
                              if product_cpfs['proteins'] else None,
                              product_cpfs['fats']
                              if product_cpfs['fats'] else None,
                              product_cpfs['carbohydrates']
                              if product_cpfs['carbohydrates'] else None,
                              product_composition
                              if product_composition else None,
                              product_shelf_life
                              if product_shelf_life else None,
                              product_storage_conditions
                              if product_storage_conditions else None,
                              product_manufacturer
                              if product_manufacturer else None,
                              product_old_price
                              if product_old_price else None,
                              product_new_price
                              if product_new_price else None)))
                conn.commit()

            # Up the limit qty to end the cycle
            limit += 1

            # Wait for nor break the limits of requests
            time.sleep(10)

            # Inform user about iterations
            print(f'Operation {limit} out of 10 for test using')
    # Close connection to DB
    conn.close()


if __name__ == "__main__":
    main()
