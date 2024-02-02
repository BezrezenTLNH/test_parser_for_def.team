# Description 
### This is a parser for samokat website. Without proxies. So all the files will be saved as .html and .json files to work with data easily

# Requirements
* python ^3.10
* beautifulsoup4 ^4.12.3
* lxml ^5.1.0
* selenium ^4.17.2
* flake8 ^7.0.0
* postgres ^4.0
* psycopg2-binary ^2.9.9

# Installation and launch instructions
## Install:
1) Clone the project github using `git clone`
2) Install dependencies by running `make install` (Poetry is required). After installing change files **"build.sh", "deep_search", and "quick_search"** in the root directory of the project. This file must contain database URL:
   * Change the DATABASE_URL on your local machine(Format: {provider}://{user}:{password}@{host}:{port}/{db})
## Start to work:
1) Create databases for saving data by command `make build`. Pay attention that your database URL should be changed.
2) Create all categories from main site by command `make categories`
3) Create all products inside chosen category by command `make category_data`
4) Make quick search by command `make quick_search` to prices, names and values for all products from 1 category and write it to your local database.
5) Make deep search by command `make deep_search` **(at this moment it's a demo version, because proxies are necessary for that function because site has a limit connection from IP per minute)**
