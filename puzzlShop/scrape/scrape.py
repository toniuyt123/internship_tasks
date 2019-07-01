from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import random 
from loremipsum import generate_paragraph
import urllib
import psycopg2
from config import config

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def scrape():
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    for i in range(1,23):
        try:
            raw_html = simple_get('https://www.puzzlemaster.ca/browse/cubepuzzle/p' + str(i))
            soup = BeautifulSoup(raw_html, 'html.parser')
            for con in soup.findAll("div", {"class": "prod-con"}):
                name = con.find('span', {'class': "productListingTitle"}).text
                price = con.find('span', {'class': "productListingPrice"}).text
                rating = random.random() * 6
                difficulty = random.randint(1,6)
                quanity = random.randint(0, 100)

                imagepath = con.find('img', {'class': "productListingImage"}).get('src')

                details_href = con.find('a', {"class": "productname-new"}).get('href')
                details_html = simple_get('https://www.puzzlemaster.ca' + details_href)
                details_soup = BeautifulSoup(details_html, 'html.parser')
                description = details_soup.find('h2', text="Product Description").findNext('p').text
                print(name)
                cur.execute(""" INSERT INTO Products(name, price, rating, difficulty, quantity, imagepath, description)
                                VALUES(%s, %s, %s, '%s', %s, %s, %s)""" , (name, float(price[1:]), rating, difficulty, quanity, imagepath, description))
        except AttributeError as e:
            continue
    cur.close()
    conn.commit()


    return 0

if __name__ == "__main__":
    scrape()