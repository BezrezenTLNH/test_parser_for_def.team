# At this ,moment I'm still worked at the City choose part,
# tests and function that should take all the data
# All the JSON file created for test and for visibility
# At this moment all links was changed by test links, but it will be automatized in
# categories section in few days
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


def get_categories(url: str = MAIN_URL) -> dict:
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get(url)

    # Wait for the dynamic data to load
    WebDriverWait(driver, 5)

    html = driver.page_source

    with open('data/categories.html', 'w', encoding='utf-8') as file:
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

    print(all_categories_dict)
    return all_categories_dict


def get_products_dict() -> dict:
    all_categories_dict = get_categories(MAIN_URL)
    url = [i for i in all_categories_dict.values()][0]

    # you can choose 1 category from file categories.html,
    # or you can uncomment this part of code to make it for all categories
    # this part of code coming soon :D
    chrome_options = Options()
    user_agent = UserAgent()
    chrome_options.add_argument(f"user-agent={user_agent.random}")

    # Initialize the Chrome browser
    driver = webdriver.Chrome(options=chrome_options)

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
                product.find(class_=re.compile("ProductCard_name")).text)
            product_link = 'https://samokat.ru' + product.get("href")
            products_dict[product_name] = product_link

    print(products_dict)
    return products_dict


def get_data_deep_search(products_dict: dict) -> None:
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


def get_data_quick_search() -> None:
    products_dict = get_products_dict()
    # Make limit for test start
    limit = 0

    # Connect to DB and fill it with our data
    conn = psycopg2.connect(DATABASE_URL)

    while limit < TEST_LIMITS:
        for product_link in products_dict.values():

            # Initialize the Chrome browser
            driver = webdriver.Chrome()

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
                soup.find(class_=re.compile("ProductCard_name")).text.strip())

            try:
                product_volume = (
                    soup.find(class_=re.compile("ProductCard_specifications")).find_all("span").text.strip())
            except Exception:
                product_volume = None

            try:
                product_old_price = (
                    soup.find(class_=re.compile("ProductCardActions_root"))
                    .find_all("span")[2].text.strip())
            except Exception:
                product_old_price = None

            try:
                product_new_price = (
                    soup.find(class_=re.compile("ProductCardActions_root"))
                    .find_all("span")[2].text.strip())
            except Exception:
                product_new_price = None

            with conn.cursor(
                    cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute('INSERT INTO products_deep_search (name, '
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
            # Up the limit qty to end the cycle
            limit += 1

            # Inform user about iterations
            print(f'Operation {limit} out of 15 for test using')
    # Close connection to DB
    conn.close()
    print('parsing is done')


def main():
    # time.sleep(5)
    # # get_data_deep_search(product_link)
    get_data_quick_search()


if __name__ == "__main__":
    main()
