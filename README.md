# Michelin Guide Restaurants Bay Area

## About
This GUI application allows users to choose multiple Michelin Guide restaurants from cities surrounding San Francisco, Cupertino, and San Jose. The user can make a selection based on a city or type of cuisine. When the user chooses a city or cuisine, a list of restaurants in that city or cuisine will be displayed. Upon selecting a number of restaurants, the application will show the restaurant's name, address, cost, and cuisine, along with a button to open a tab in their browser with the Michelin Guide page of the chosen restaurant.

The project consists of two parts: `backend.py` and `frontend.py`.
- `backend.py`: This script creates a database by web scraping data from the Michelin Guide website. 
- `frontend.py`: This script interacts with the user while fetching data from the SQLite Database.

## Running the Application
To run the application, follow these steps:
1. Run `backend.py` to scrape the data, create a JSON file, and combine the JSON into a SQLite Database.
2. Once `backend.py` has created the combined DB file for San Jose, Cupertino, and San Francisco, you are ready to proceed.
3. Run `frontend.py` to start the GUI application and interact with it.

Please ensure you have all the necessary dependencies installed before running the application.

Enjoy exploring the Michelin Guide Restaurants in the Bay Area!

## Source
- [Micheline Guide Restaurant- San Jose](https://guide.michelin.com/us/en/california/san-jose/restaurants)
- [Micheline Guide Restaurant- Cupertino](https://guide.michelin.com/us/en/california/cupertino/restaurants)
- [Micheline Guide Restaurant- San Francisco](https://guide.michelin.com/us/en/california/san-francisco/restaurants)


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
