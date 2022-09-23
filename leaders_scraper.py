#importing all i am gonna need
import requests
import re
import json
from requests import Session
from bs4 import BeautifulSoup

#creating a cache that can work with a session
cache = {}
def hashable_cache(f):
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

#usinig the cache and creating a function that is gonna take the first paragraphe of a given web page (secondary function)
@hashable_cache
def get_first_paragraph(wikipedia_url, session: Session):
    print(wikipedia_url) # keep this for the rest of the notebook
    req = session.get(wikipedia_url).text
    soup = BeautifulSoup(req, 'html.parser')
    for paragraph in soup.find_all('p'):
        if paragraph.find('b'):
            first_paragraph = paragraph.text
            regex_paragraph = re.sub("\[\d+\]|\\n", '', first_paragraph)
            break
    return regex_paragraph

#
def get_leaders():
    #setting the urls
    root_url = "https://country-leaders.herokuapp.com"
    countries_url = root_url + "/countries"
    leaders_url = root_url + "/leaders"
    cookie_url = root_url + "/cookie"
    status_url = root_url + "/status"
    
    #fetching the cookies
    cookie = requests.get(cookie_url).cookies
    #fetching the countries
    countries = requests.get(countries_url,cookies=cookie).json()
    #saving the leaders in a dictionary
    leaders_list = []
    #initialtation of the session
    with Session() as session:
        #loop troo the countries
        for i in range(int(len(countries))) :
            leaders_content = requests.get(leaders_url,cookies=cookie, params=f"country={countries[i]}")
            leader_of_country = []
            j = 0
        #check if the cookie is still good
            while leaders_content.status_code == 403:
                print('refreshing cookies')
                print(cookie)
                cookie = requests.get(cookie_url).cookies
                leaders_content = requests.get(leaders_url,cookies=cookie, params=f"country={countries[i]}")
                j += 1
                if j == 5:
                    return {}
        #loop troo the leaders of the country
            for leader in leaders_content.json():
                result = get_first_paragraph(leader['wikipedia_url'], session)
                leader_of_country.append(result)
            
            leaders_list.append(leader_of_country)

        countLead_dict = {countrie:leaders for countrie, leaders in zip(countries, leaders_list)}
        return countLead_dict

#creating a function that save the output of the get_leader() fct in a json file
def save():
    with open('leaders.json', 'w') as f:
        leaders_per_counrty_json = json.dumps(leaders_per_country, indent=4)
        f.write(leaders_per_counrty_json)
        print("json file has been created")

leaders_per_country = get_leaders()
save()