install:
	poetry install

categories:
	poetry run get_categories

category_data:
	poetry run get_data_from_category

deep_search:
	poetry run deep_search

quick_search:
	poetry run quick_search

lint:
	poetry run flake8 parser

build:
	./build.sh