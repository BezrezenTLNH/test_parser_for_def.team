DROP TABLE IF EXISTS products_deep_search;
DROP TABLE IF EXISTS products_quick_search;

CREATE TABLE products_deep_search (
	id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	name text,
	volume text,
	created_at date NOT NULL,
	highlights text,
	marketing_description text,
	calories varchar(30),
	proteins varchar(30),
	fats varchar(30) ,
	carbohydrates varchar(30),
	composition text,
	shelf_life text,
	storage_conditions text,
	manufacturer text,
	old_price varchar(30),
	new_price varchar(30));

CREATE TABLE products_quick_search (
	id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	name text,
	volume text,
	created_at date NOT NULL,
	old_price varchar(30),
	new_price varchar(30));