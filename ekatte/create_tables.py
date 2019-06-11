# -*- coding: utf-8 -*-
import psycopg2
from config import config

 
def create_tables():
    commands = (
        """ CREATE TYPE t_v_m AS ENUM('с.', 'гр.', 'ман.')
        """,
        """ CREATE TABLE Regions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(60) UNIQUE NOT NULL,
                code VARCHAR(3) UNIQUE NOT NULL
        )
        """,
        """ CREATE TABLE Minicapilities (
                id SERIAL PRIMARY KEY,
                name VARCHAR(60) NOT NULL,
                code VARCHAR(5) NOT NULL,
                regionId INTEGER NOT NULL,
                UNIQUE(name, code),
                FOREIGN KEY (regionId) REFERENCES Regions(id)
            )
        """,
        """ CREATE TABLE Villages (
                id SERIAL PRIMARY KEY,
                ekatte INTEGER UNIQUE NOT NULL,
                t_v_m t_v_m NOT NULL,
                name VARCHAR(60) NOT NULL,
                minicapilityId INTEGER NOT NULL,
                FOREIGN KEY (minicapilityId) REFERENCES Minicapilities(id),
                UNIQUE(name, minicapilityId)
        )
        """)
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
 
if __name__ == '__main__':
    create_tables()