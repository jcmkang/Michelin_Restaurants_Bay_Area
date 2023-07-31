# Michelin Guide Restaurants Bay Area

## About
This GUI application allows a user to choose multiple Michelin Guide restauarant from cities surrounding San Francisco, Cupertino, and San Jose. The user will be able to make a selection based on the City or Cuisine. When the user chooses a city or cuisine, a list of restaurants in that city or cuisine will display. When restauarnts are chosen, the application will display to the user with the restrautn's name, address, cost, and cuisine and a button to open a tab on their probser with the Micheile Guide page of the chosen restaurant. <br><br>
The project has two parts: frontend.py and backend.py
- The backend.py will get data by webscraping from the Micheline Guide page. From the extracted data, a JSON file is created to store the data. The data from JSON file is then read into a SQLite Database to be used by frontend.py
- frontend.py interacts with the user while fetching data from SQLite Databse

## Running the Application
- First, run backend.py to get the data, create a JSON file, and write the JSON to a SQLite Database
- After backend.py has created 3 JSON files and 3 DB files for San Jose, Cupertino, and San Francisco, Run frontend.py to start the GUI application

## Source
[Micheline Guide Restaurant- San Jose](https://guide.michelin.com/us/en/california/san-jose/restaurants)
[Micheline Guide Restaurant- Cupertino](https://guide.michelin.com/us/en/california/cupertino/restaurants)
[Micheline Guide Restaurant- San Francisco](https://guide.michelin.com/us/en/california/san-francisco/restaurants)


## Skills
- Requests
- BeautifulSoup
- SQLite 3
- TKinter

## Credit
- Professor: Clare Nguyen
- College: De Anza
- Course: CIS 41B (Advanced Python Programming)
- Author: James Kang, © 2023
