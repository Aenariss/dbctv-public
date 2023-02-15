/*
    * create.sql 
    * Autor: Vojtech Fiala <xfiala61>
    *
    # Soucast bakalarske prace Databaze Vysilani Ceskoslovenske Televize, 2022
    *
    * Skript pro vytvoreni SQLite3 databaze
*/


CREATE TABLE Person (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL UNIQUE,
    shadowName text NOT NULL
);

CREATE TABLE Role (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL UNIQUE
);

CREATE TABLE Description (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    description text UNIQUE
);

CREATE TABLE Series (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    shadowName text NOT NULL
);

CREATE TABLE Date (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    date text NOT NULL UNIQUE
);

CREATE TABLE Time (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    timeAiring text NOT NULL UNIQUE
);

CREATE TABLE Country (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL UNIQUE
);

CREATE TABLE PersonPlays (
    id_aired integer NOT NULL,
    id_person integer NOT NULL,
    id_role integer NOT NULL,
    PRIMARY KEY (id_aired, id_person),
    FOREIGN KEY(id_aired) references AiredAtTime(id),
    FOREIGN KEY(id_person) references Person(id),
    FOREIGN KEY(id_role) references Role(id)
);

CREATE TABLE AiredAtTime (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    series_id integer NOT NULL,
    time_id integer NOT NULL,
    date_id integer NOT NULL,
    programme integer NOT NULL,
    country_id integer NOT NULL,
    desc_id integer NOT NULL,
    FOREIGN KEY(series_id) references Series(id),
    FOREIGN KEY(time_id) references Time(id),
    FOREIGN KEY(date_id) references Date(id),
    FOREIGN KEY(desc_id) references Description(id),
    FOREIGN KEY(country_id) references Country(id)
);

/* vyhledavani skrz ilike je case insensitive */
PRAGMA case_sensitive_like=OFF;
