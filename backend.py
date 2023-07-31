# Webscraping and data storage with requests, beautifulsoup, sqlite3, review tkinter
# backend.py -> Webscrape Michelin Website, create

"""
The backend.py has two parts.
Part A will Webscrape data from the Michelin Guide page and create a JSON file
Part B will read data from the JSON file into the SQLite database

"""

# importing modules
import urllib.request as ur
import requests
from bs4 import BeautifulSoup
import re
import json
import sqlite3

san_jose_url = 'https://guide.michelin.com/us/en/california/san-jose/restaurants'
cupertino_url = 'https://guide.michelin.com/us/en/california/cupertino/restaurants'
san_francisco_url = 'https://guide.michelin.com/us/en/california/san-francisco/restaurants'

'''
Part A: Code below can be commented out after the JSON Files are created.
    From the URL above, use requests and beautifulsoup to extract the following information for each restaurant on the page:
    * URL of the restaurant
    * Name of the restaurant
    * Location or city name (such as San Jose or Los Gatos)
    * Cost (number of $ signs)
    * Cuisine (Mexican or French)
    Then, use the URL of the restaurant to do a web crawl to the restaurant page and extract the following information:
    * Address of the restaurant (street address and city)
    * Alternatively, the cost and cuisine can be extracted from this page instead of the previous page.
'''

def webscrape(url):
    '''
    webscrape function will take in an url as an argument, and scrape data from the website
    it will return the scrapped data as a list
    '''
    # print("scraping url:", url)
    root_site = "https://guide.michelin.com"
    restaurant_data = []
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "lxml")
    # print(soup.prettify()[:1000])
    # print()

    div = soup.find_all('div', class_='card__menu-content js-match-height-content')
    for item in div:
        information = []
        # Name
        information.append(item.find('a').text.strip())
        # URL
        information.append("https://guide.michelin.com" + item.find('a')['href'])
        # Location
        information.append(
            item.find('div', class_='card__menu-footer--location flex-fill pl-text').text.strip().split(',')[0])
        # Dollar Sign
        information.append(
            re.search("\$+", item.find('div', class_='card__menu-footer--price pl-text').text).group())
        # Cuisine
        information.append(
            re.search("\w+", item.find('div', class_='card__menu-footer--price pl-text').text).group())
        # address
        page = requests.get("https://guide.michelin.com" + item.find('a')['href'])
        soup1 = BeautifulSoup(page.content, "lxml")
        div = soup1.find('div', class_='restaurant-details__heading d-lg-none')
        address = div.find('ul').text.strip().splitlines()[0]
        information.append(address)

        restaurant_data.append(information)

    # print(restaurant_data)

    # print()
    # find the pagination section with multiple page block
    next_div = soup.find('ul', class_='pagination')
    # find the RIGHT CLICK button
    next_button = next_div.find('i', class_='fa fa-angle-right')
    # IF RIGHT CLICK button exists..
    # recursive function.. run function again,  add the og list to the new list
    if next_button:
        nxtpg_url = next_div.find_all('li', class_='arrow')[-1].a['href']
        url = root_site + str(nxtpg_url)
        # print("found the next button. . . new url =  ", url)
        restaurant_data = restaurant_data + webscrape(url)
    else:
        print("done!")

    # print(restaurant_data)
    return restaurant_data


def write_JSON(data, filename):
    '''
    write_JSON function will make the JSON file with the data that is scraped from webscrape() function
    '''
    with open(filename, 'w') as fh:
        json.dump(data, fh)
    return filename


sj_michelin_data = webscrape(san_jose_url)
cupertino_michelin_data = webscrape(cupertino_url)
sf_michelin_data = webscrape(san_francisco_url)

combined_data = sj_michelin_data + cupertino_michelin_data + sf_michelin_data

# Save the combined data into a single JSON file
combined_json_filename = 'michelin_data_combined.json'
Combined_JSON = write_JSON(combined_data, combined_json_filename)


## PART B: READ THE DATA FROM JSON FILE into THE SQLITE DATABASE
def makeDBfile(data, dbfile_name):
    '''
    makeDBfile function will make the DB file from the JSON file that was created by the write_JSON function
    '''
    filename = dbfile_name.split('.')[0]
    # create connection to database and create file
    conn = sqlite3.connect(f'{filename}.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS Locations")
    cur.execute('''CREATE TABLE Locations(
                        id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                        location TEXT UNIQUE ON CONFLICT IGNORE)''')
    cur.execute("DROP TABLE IF EXISTS Costs")
    cur.execute('''CREATE TABLE Costs(
                        id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                        sign TEXT UNIQUE ON CONFLICT IGNORE)''')
    cur.execute("DROP TABLE IF EXISTS Cuisines")
    cur.execute('''CREATE TABLE Cuisine(
                        id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                        type TEXT UNIQUE ON CONFLICT IGNORE)''')
    cur.execute("DROP TABLE IF EXISTS RestaurantsDB")
    cur.execute('''CREATE TABLE RestaurantsDB(
                        Name TEXT NOT NULL PRIMARY KEY UNIQUE,
                        URL TEXT,
                        Loc INT,
                        Cost INT,
                        Type INT,
                        Address TEXT)''')

    # propagate the Database
    for restaurant_info in data:
        cur.execute('''INSERT OR IGNORE INTO Locations (location) VALUES (?)''', (restaurant_info[2],))
        cur.execute('''SELECT id FROM Locations WHERE location = ?''', (restaurant_info[2],))
        location_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO Costs (sign) VALUES (?)''', (restaurant_info[3],))
        cur.execute('''SELECT id FROM Costs WHERE sign = ?''', (restaurant_info[3],))
        cost_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO Cuisine (type) VALUES (?)''', (restaurant_info[4],))
        cur.execute('''SELECT id FROM Cuisine WHERE type = ?''', (restaurant_info[4],))
        cuisine_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO RestaurantsDB
                            (Name, URL, Loc, Cost, Type, Address)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                    (restaurant_info[0], restaurant_info[1], location_id, cost_id, cuisine_id, restaurant_info[-1]))
    conn.commit()
    conn.close()

makeDBfile(combined_data, 'michelin_data_combined.db')



# UNIT TESTING: OUTPUT FROM SHELL #
# initial testing with only San Jose and Cupertino
# confirmed that code scrapes multiple pages if available

'''
scraping url: https://guide.michelin.com/us/en/california/san-jose/restaurants

[['LeYou', 'https://guide.michelin.com/us/en/california/san-jose/restaurant/leyou', 'San Jose', '$$', 'Ethiopian', '1100 N. First St., Ste. C., San Jose, 95112, USA'], 
['Petiscos', 'https://guide.michelin.com/us/en/california/san-jose/restaurant/petiscos', 'San Jose', '$$', 'Portuguese', '399 S. 1st St., San Jose, 95113, USA'], 
['Luna Mexican Kitchen', 'https://guide.michelin.com/us/en/california/san-jose/restaurant/luna-mexican-kitchen', 'San Jose', '$$', 'Mexican', '1495 The Alameda, San Jose, 95126, USA'], 
['Adega', 'https://guide.michelin.com/us/en/california/san-jose/restaurant/adega', 'San Jose', '$$$$', 'Portuguese', '1614 Alum Rock Ave., San Jose, 95116, USA'], 
['Be.Stéak.Ă', 'https://guide.michelin.com/us/en/california/campbell/restaurant/be-steak-a', 'Campbell', '$$$', 'Steakhouse', '1887 S. Bascom Ave., Campbell, 95008, USA'], 
['Orchard City Kitchen', 'https://guide.michelin.com/us/en/california/campbell/restaurant/orchard-city-kitchen', 'Campbell', '$$', 'International', '1875 S. Bascom Ave., Ste.190, Campbell, 95008, USA'], 
['Beijing Duck House', 'https://guide.michelin.com/us/en/california/cupertino/restaurant/beijing-duck-house', 'Cupertino', '$$', 'Chinese', '10883 S. Blaney Ave., Cupertino, 95014, USA'], 
['The Bywater', 'https://guide.michelin.com/us/en/california/los-gatos/restaurant/the-bywater', 'Los Gatos', '$$', 'Southern', '532 N. Santa Cruz Ave., Los Gatos, 95030, USA'], 
['ASA South', 'https://guide.michelin.com/us/en/california/los-gatos/restaurant/asa-south', 'Los Gatos', '$$', 'Californian', '57 Los Gatos-Saratoga Rd., Los Gatos, 95032, USA'], 
['Dio Deka', 'https://guide.michelin.com/us/en/california/los-gatos/restaurant/dio-deka', 'Los Gatos', '$$$', 'Greek', '210 E. Main St., Los Gatos, 95030, USA'], 
['Plumed Horse', 'https://guide.michelin.com/us/en/california/saratoga/restaurant/plumed-horse', 'Saratoga', '$$$$', 'Contemporary', '14555 Big Basin Way, Saratoga, 95070, USA'], 
['Doppio Zero Pizza Napoletana', 'https://guide.michelin.com/us/en/california/mountain-view/restaurant/doppio-zero-pizza-napoletana', 'Mountain View', '$$', 'Pizza', '160 Castro St., Mountain View, 94041, USA'], 
['Chez TJ', 'https://guide.michelin.com/us/en/california/mountain-view/restaurant/chez-tj', 'Mountain View', '$$$$', 'Contemporary', '938 Villa St., Mountain View, 94041, USA'], 
['Aurum', 'https://guide.michelin.com/us/en/california/los-altos/restaurant/aurum-1195363', 'Los Altos', '$$$', 'Indian', '132 State St., Los Altos, 94022, USA'], 
['Protégé', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/protege', 'Palo Alto', '$$$$', 'Contemporary', '250 California Ave., Palo Alto, 94306, USA'], 
['iTalico', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/italico', 'Palo Alto', '$$', 'Italian', '341 California Ave., Palo Alto, 94306, USA'], 
['Zola', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/zola', 'Palo Alto', '$$$', 'French', '565 Bryant St., Palo Alto, 94301, USA'], 
['Tamarine', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/tamarine', 'Palo Alto', '$$$', 'Vietnamese', '546 University Ave., Palo Alto, 94301, USA'], 
['Ettan', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/ettan', 'Palo Alto', '$$$', 'Indian', '518 Bryant St., Palo Alto, 94301, USA'], 
['Bird Dog', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/bird-dog', 'Palo Alto', '$$', 'Contemporary', '420 Ramona St., Palo Alto, 94301, USA']]

found the next button.. new url: https://guide.michelin.com/us/en/california/san-jose/restaurants/page/2
scraping url: https://guide.michelin.com/us/en/california/san-jose/restaurants/page/2

[['Evvia', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/evvia', 'Palo Alto', '$$$', 'Greek', '420 Emerson St., Palo Alto, 94301, USA'], 
['Vina Enoteca', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/vina-enoteca', 'Palo Alto', '$$$', 'Italian', '700 Welch Rd., Unit 110, Palo Alto, 94304, USA'], 
['Camper', 'https://guide.michelin.com/us/en/california/menlo-park/restaurant/camper', 'Menlo Park', '$$', 'Californian', '898 Santa Cruz Ave., Menlo Park, 94025, USA'], 
['Flea St. Cafe', 'https://guide.michelin.com/us/en/california/menlo-park/restaurant/flea-st-cafe', 'Menlo Park', '$$$', 'Contemporary', '3607 Alameda de las Pulgas, Menlo Park, 94025, USA']]

done!

scraping url: https://guide.michelin.com/us/en/california/cupertino/restaurants

[['Beijing Duck House', 'https://guide.michelin.com/us/en/california/cupertino/restaurant/beijing-duck-house', 'Cupertino', '$$', 'Chinese', '10883 S. Blaney Ave., Cupertino, 95014, USA'], 
'Plumed Horse', 'https://guide.michelin.com/us/en/california/saratoga/restaurant/plumed-horse', 'Saratoga', '$$$$', 'Contemporary', '14555 Big Basin Way, Saratoga, 95070, USA'], 
['Orchard City Kitchen', 'https://guide.michelin.com/us/en/california/campbell/restaurant/orchard-city-kitchen', 'Campbell', '$$', 'International', '1875 S. Bascom Ave., Ste.190, Campbell, 95008, USA'], 
['Be.Stéak.Ă', 'https://guide.michelin.com/us/en/california/campbell/restaurant/be-steak-a', 'Campbell', '$$$', 'Steakhouse', '1887 S. Bascom Ave., Campbell, 95008, USA'], 
['Doppio Zero Pizza Napoletana', 'https://guide.michelin.com/us/en/california/mountain-view/restaurant/doppio-zero-pizza-napoletana', 'Mountain View', '$$', 'Pizza', '160 Castro St., Mountain View, 94041, USA'], 
['Chez TJ', 'https://guide.michelin.com/us/en/california/mountain-view/restaurant/chez-tj', 'Mountain View', '$$$$', 'Contemporary', '938 Villa St., Mountain View, 94041, USA'], 
['Aurum', 'https://guide.michelin.com/us/en/california/los-altos/restaurant/aurum-1195363', 'Los Altos', '$$$', 'Indian', '132 State St., Los Altos, 94022, USA'], 
['Luna Mexican Kitchen', 'https://guide.michelin.com/us/en/california/san-jose/restaurant/luna-mexican-kitchen', 'San Jose', '$$', 'Mexican', '1495 The Alameda, San Jose, 95126, USA'], 
['The Bywater', 'https://guide.michelin.com/us/en/california/los-gatos/restaurant/the-bywater', 'Los Gatos', '$$', 'Southern', '532 N. Santa Cruz Ave., Los Gatos, 95030, USA'], 
['ASA South', 'https://guide.michelin.com/us/en/california/los-gatos/restaurant/asa-south', 'Los Gatos', '$$', 'Californian', '57 Los Gatos-Saratoga Rd., Los Gatos, 95032, USA'], 
['Dio Deka', 'https://guide.michelin.com/us/en/california/los-gatos/restaurant/dio-deka', 'Los Gatos', '$$$', 'Greek', '210 E. Main St., Los Gatos, 95030, USA'], 
['LeYou', 'https://guide.michelin.com/us/en/california/san-jose/restaurant/leyou', 'San Jose', '$$', 'Ethiopian', '1100 N. First St., Ste. C., San Jose, 95112, USA'], 
['Petiscos', 'https://guide.michelin.com/us/en/california/san-jose/restaurant/petiscos', 'San Jose', '$$', 'Portuguese', '399 S. 1st St., San Jose, 95113, USA'], 
['Adega', 'https://guide.michelin.com/us/en/california/san-jose/restaurant/adega', 'San Jose', '$$$$', 'Portuguese', '1614 Alum Rock Ave., San Jose, 95116, USA'], 
['iTalico', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/italico', 'Palo Alto', '$$', 'Italian', '341 California Ave., Palo Alto, 94306, USA'], 
['Protégé', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/protege', 'Palo Alto', '$$$$', 'Contemporary', '250 California Ave., Palo Alto, 94306, USA'],
['Zola', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/zola', 'Palo Alto', '$$$', 'French', '565 Bryant St., Palo Alto, 94301, USA'], 
['Ettan', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/ettan', 'Palo Alto', '$$$', 'Indian', '518 Bryant St., Palo Alto, 94301, USA'], 
['Vina Enoteca', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/vina-enoteca', 'Palo Alto', '$$$', 'Italian', '700 Welch Rd., Unit 110, Palo Alto, 94304, USA'], 
['Evvia', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/evvia', 'Palo Alto', '$$$', 'Greek', '420 Emerson St., Palo Alto, 94301, USA']]

found the next button.. new url: https://guide.michelin.com/us/en/california/cupertino/restaurants/page/2
scraping url: https://guide.michelin.com/us/en/california/cupertino/restaurants/page/2

[['Bird Dog', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/bird-dog', 'Palo Alto', '$$', 'Contemporary', '420 Ramona St., Palo Alto, 94301, USA'], 
['Tamarine', 'https://guide.michelin.com/us/en/california/palo-alto/restaurant/tamarine', 'Palo Alto', '$$$', 'Vietnamese', '546 University Ave., Palo Alto, 94301, USA'], 
['Madera', 'https://guide.michelin.com/us/en/california/menlo-park/restaurant/madera', 'Menlo Park', '$$$$', 'Contemporary', '2825 Sand Hill Rd., Menlo Park, 94025, USA'], 
['Flea St. Cafe', 'https://guide.michelin.com/us/en/california/menlo-park/restaurant/flea-st-cafe', 'Menlo Park', '$$$', 'Contemporary', '3607 Alameda de las Pulgas, Menlo Park, 94025, USA'], 
['Camper', 'https://guide.michelin.com/us/en/california/menlo-park/restaurant/camper', 'Menlo Park', '$$', 'Californian', '898 Santa Cruz Ave., Menlo Park, 94025, USA'], 
["Selby's", 'https://guide.michelin.com/us/en/california/atherton/restaurant/selby-s', 'Atherton', '$$$$', 'American', '3001 El Camino Real, Atherton, 94061, USA'], 
['The Village Pub', 'https://guide.michelin.com/us/en/california/woodside/restaurant/the-village-pub', 'Woodside', '$$$', 'Contemporary', '2967 Woodside Rd., Woodside, 94062, USA'], 
['La Viga Seafood & Cocina Mexicana', 'https://guide.michelin.com/us/en/california/redwood-city/restaurant/la-viga-seafood-cocina-mexicana', 'Redwood City', '$$', 'Mexican', '1772 Broadway, Redwood City, 94063, USA'], 
['Sushi Shin', 'https://guide.michelin.com/us/en/california/redwood-city/restaurant/sushi-shin-1195403', 'Redwood City', '$$$$', 'Japanese', '312 Arguello St., Redwood City, 94063, USA'], 
['Saffron', 'https://guide.michelin.com/us/en/california/us-san-carlos/restaurant/saffron-1196338', 'San Carlos', '$$', 'Indian', '1143 San Carlos Ave., San Carlos, 94070, USA']]

done!
'''
