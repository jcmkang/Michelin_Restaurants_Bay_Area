# Michelin Guide Restaurants South Bay

## About
This GUI application allows a user to choose multiple Michelin Guide restauarant from Bay Area, California. First, the user will be able to make a selection based on the City or Cuisine. When the user chooses a city or cuisine, a listbox of restaurants in that city or cuisine will display. When restauarnts are chosen, the application will display to the user with the restrautn's name, address, cost, and cuisine and a button to open a tab on their probser with the Micheile Guide page of the restaurant. <br><br>
The project has two parts: frontend.py and backend.py
- The backend.py will get data by webscraping from the Micheline Guide page. From the extracted data, a JSON file is created to store the data. The data from JSON file is then read into a SQLite Database to be used by frontend.py
- frontend.py interacts with the user while fetching data from SQLite Databse

## Source
[Micheline Guide Restaurant- San Jose](https://guide.michelin.com/us/en/california/san-jose/restaurants)

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
