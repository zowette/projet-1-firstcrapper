import requests
import json
from bs4 import BeautifulSoup as BS
import re

session = requests.Session()

cache = {}
def hashable_cache(f):
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

def get_leader():
    root_url = "https://country-leaders.herokuapp.com"
    country_url = "https://country-leaders.herokuapp.com/countries" 
    cookie_url = "https://country-leaders.herokuapp.com/cookie"
    leaders_url = "https://country-leaders.herokuapp.com/leaders"

    cookie = (requests.get(cookie_url)).cookies
    countries = requests.get(country_url, cookies=cookie)

    leaders_per_country = {}
    for country in countries.json():
        leaders = requests.get(leaders_url, cookies=cookie,params={"country":country})
        if(leaders.status_code != 200):
            cookie = (requests.get(cookie_url)).cookies
            leaders = requests.get(leaders_url, cookies=cookie, params={"country":country})

        leaders_per_country[country] = leaders.json()
        
        leaderss = {}
        for leader in leaders.json():
            wikipedia_url = leader["wikipedia_url"]
            first_paragraph = get_first_paragraph(wikipedia_url, session)
            leader.update({"first_paragraph":first_paragraph})
            leaderss.update({leader["id"]:leader})

        leaders_per_country.update({country:leaderss})
                      
    return leaders_per_country   

@hashable_cache
def get_first_paragraph(wikipedia_url, session):
    req = session.get(wikipedia_url)
    soup = BS(req.text, "html.parser")
    for paragraph in soup.find_all('p'):
        if paragraph.find_all('b'):
            toclean = paragraph.text
            first_paragraph = re.sub(r'\[\d+\]|\(listen\)|Écouter','', toclean)
            return first_paragraph

def save():
    leaders_per_country = get_leader()

    #json_string = json.dumps(leaders_per_country)
    with open("leaders.json", 'w') as json_file:
        json.dump(leaders_per_country, json_file)

    filename = "./leaders.json"
    with open(filename, "r") as my_file:
        print(my_file.read())

save()