/*
    zeit.api.schemas.database
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    These are the initialization statements for the main SQLite database.

    Copyright: (c) 2013 by ZEIT ONLINE.
    License: BSD, see LICENSE.md for more details.
*/

CREATE TABLE IF NOT EXISTS author
(
	href		CHAR(256),
	id			CHAR(256)	NOT NULL PRIMARY KEY,
	type		CHAR(32)	NOT NULL,
	uri			CHAR(288)	NOT NULL,
	value		CHAR(256)	NOT NULL
);

CREATE TABLE IF NOT EXISTS client
(
	api_key		CHAR(64)	NOT NULL PRIMARY KEY,
	tier		CHAR(32)	NOT NULL,
	name		CHAR(128),
	email		CHAR(128),
	requests	UNSIGNED INTEGER,
	reset		UNSIGNED INTEGER
);

CREATE TABLE IF NOT EXISTS department
(
	href		CHAR(128),
	id			CHAR(64)	NOT NULL PRIMARY KEY,
	parent		CHAR(64),
	uri			CHAR(96)	NOT NULL,
	value		CHAR(64)	NOT NULL,
	FOREIGN KEY(parent) REFERENCES department(id)
);

CREATE TABLE IF NOT EXISTS keyword
(
	href		CHAR(128),
	id			CHAR(64)	NOT NULL PRIMARY KEY,
	lexical		CHAR(64)	NOT	NULL,
	score		UNSIGNED INTEGER,
	type		CHAR(32)	NOT NULL,
	uri			CHAR(96)	NOT NULL,
	value		CHAR(64)	NOT NULL
);

CREATE TABLE IF NOT EXISTS product
(
	href		CHAR(128),
	id			CHAR(32)	NOT NULL PRIMARY KEY,
	uri			CHAR(64)	NOT NULL,
	value		CHAR(64)	NOT NULL
);

CREATE TABLE IF NOT EXISTS series
(
	href		CHAR(128),
	id			CHAR(64)	NOT NULL PRIMARY KEY,
	name		CHAR(128)	NOT NULL,
	uri			CHAR(96)	NOT NULL,
	value		CHAR(128)	NOT NULL
);