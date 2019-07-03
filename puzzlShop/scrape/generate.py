import lorem
import psycopg2
from config import config
import random

def generate():
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    for i in range(50000):
        name = lorem.sentence()
        price = random.random() * 200
        rating = random.random() * 6
        difficulty = random.randint(1,6)
        quanity = random.randint(0, 100)

        imagepath = 'https://loremflickr.com/320/240?lock=' + str(i)
        description = lorem.paragraph()

        cur.execute(""" INSERT INTO Products(name, price, rating, difficulty, quantity, imagepath, description)
                        VALUES(%s, %s, %s, '%s', %s, %s, %s)""" , (name, price, rating, difficulty, quanity, imagepath, description))

    cur.close()
    conn.commit()


def generate_tags():
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    for i in range(100, 50000):
        cur.execute(""" INSERT INTO productstags VALUES (%s, %s)""", (i, random.randint(1,4)))

    cur.close()
    conn.commit()

if __name__ == "__main__":
    generate_tags()