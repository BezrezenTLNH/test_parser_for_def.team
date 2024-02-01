# Description 
### This is a parser for samokat website

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
2) Install dependencies by running `make install` (Poetry is required). After installing change file **"build.sh**" in the root directory of the project. This file must contain database URL:
   * Change the DATABASE_URL on your local machine(Format: {provider}://{user}:{password}@{host}:{port}/{db})