# Webscraping and data storage with requests, beautifulsoup, sqlite3, review tkinter
# frontend.py -> GUI: MainWindow, DialogWindow, DisplayWindow

# import modules
import matplotlib
matplotlib.use('TkAgg')
import tkinter as tk
import tkinter.messagebox as messagebox
import sqlite3
import webbrowser


class MainWindow(tk.Tk):
    """
    MainWin Class is the Main Window of the GUI application.
    * The app starts with a main window that has the text to explain the application and 2 buttons
    * The user can press on the buttons to lock in choice to search restaurants by city or by cuisine

    Depending on the selection, MainWindow will call methods to call the DialogWindow
    once selection for restaurants are obtained, MainWindow will call methods to call the DisplayWindow
    """
    def __init__(self):
        super().__init__()
        self.display_windows = []
        self.title("Michelin Restaurant")
        self.geometry("+500+500")
        tk.Label(self, text="Local Michelin Restaurants", font=("Calibri", 15)).grid(pady=5)
        tk.Label(self, text="Search by:", font=("Calibri", 13)).grid(pady=3)

        # Create buttons for user choice
        buttonFrame = tk.Frame(self)
        tk.Button(buttonFrame, text="City", command=self.open_city_dialog).grid(row=2, column=0)
        tk.Button(buttonFrame, text="Cuisine", command=self.open_cuisine_dialog).grid(row=2, column=1)
        buttonFrame.grid(pady=3)
        self.protocol("WM_DELETE_WINDOW", self.mainWinClose)

        self.db_connection = sqlite3.connect("michelin_data_combined.db")

    def open_city_dialog(self):
        '''
        This is the callback function for the "City" button
        The mainWindow will open the DialogWindow while passing in the opened connection as well as the type for the argument
        if there is a selection, then the MainWindow will call the open_restaurant_dialog which will again call the DialogWindow
        '''
        dialog = DialogWindow(self, self.db_connection, "city")
        self.wait_window(dialog)
        if dialog.selection:
            self.open_restaurant_dialog(dialog.selection, "city")

    def open_cuisine_dialog(self):
        '''
         This is the callback function for the "Cuisine" button
         The mainWindow will open the DialogWindow while passing in the opened connection as well as the type for the argument
         if there is a selection, then the MainWindow will call the open_restaurant_dialog which will again call the DialogWindow
         '''
        dialog = DialogWindow(self, self.db_connection, "cuisine")
        self.wait_window(dialog)
        if dialog.selection:
            self.open_restaurant_dialog(dialog.selection, "cuisine")

    def open_restaurant_dialog(self, selection, filter_type):
        '''
        The open_restaurant_dialog method will pass the selection and filter_type to filter out the city and which type
        into the DialogWindow to create a new dialog window with just the restaurants.
        If there is a selection, then the MainWindow will call the open_display_window method to create the Display Window
        '''
        dialog = DialogWindow(self, self.db_connection, "restaurant", selection, filter_type)
        self.wait_window(dialog)
        if dialog.selection:
            self.open_display_window(dialog.selection)

    def open_display_window(self, selection):
        '''
         The open_display_window method will pass in the selection, which is the cursor selection of the restaurants.
         create a display_window list to store references to display multiple windows if the selection is multiple

         The for loop will go through every restaurant in the selection and create a displayWindow for each selection.
         This allows for multiple windows to be created for each restaurant.
         '''
        # List to store references to display windows so that it can be closed later
        display_windows = []
        for restaurant in selection:
            display_window = DisplayWindow(self, self.db_connection, restaurant)
            display_windows.append(display_window)
        self.display_windows = display_windows

    def mainWinClose(self):
        """
        callback function to quit the program and all memory when user clicks "X"
        """
        # If there are more than one displaywindows, close all.
        for display_window in self.display_windows:
            # close all display windows
            display_window.destroy()
        self.destroy()
        self.quit()


class DialogWindow(tk.Toplevel):
    """
    The DialogWindow Class checks which type of dialog_type or button was clicked in the mainWindow
    depending on the button, it calls its correct method to fetch data
    """
    def __init__(self, parent, db_connection, dialog_type, selection=None, filter_type=None):
        super().__init__(parent)
        # buttons in mainWindow are de-activated
        self.grab_set()
        self.focus_set()
        self.parent = parent
        self.title(f"Select {dialog_type}")
        self.selection = None
        self.db_connection = db_connection

        # checks to see which selection was made in the MainWindow Button by the argument passed to the call(dialog_type)
        # store fetched data in instance attribute
        if dialog_type == "city":
            self.data = self.fetch_cities()
            self.window = True
        elif dialog_type == "cuisine":
            self.data = self.fetch_cuisines()
            self.window = True
        elif dialog_type == "restaurant":
            self.rest_data = self.fetch_restaurants(selection, filter_type)
            self.window = False

        # SINGLE SELECTION
        # if it was "City" or "cuisine" then,, set SELECTMODE = 'single' (default)
        if self.window:
            CityFrame = tk.Frame(self)
            tk.Label(CityFrame, text=f"Click on a {dialog_type} to select").grid()
            CityLB_scrollbar = tk.Scrollbar(CityFrame)
            self.LB = tk.Listbox(CityFrame, height=6, yscrollcommand=CityLB_scrollbar.set)
            # self.LB.grid(row=1)
            CityLB_scrollbar.config(command=self.LB.yview)
            CityLB_scrollbar.grid(row=1, column=1, sticky='ns')

            # using instance attribute of fetched data self.data insert all the elements in the data
            # fill listbox
            for item in self.data:
                self.LB.insert(tk.END, item)
            self.LB.grid(row=1)
            CityFrame.grid()

            # button to lock in selection, using lambda to pass in a "single"
            select_button = tk.Button(self, text="Select", command=lambda: self.select_item('SINGLE'))
            select_button.grid()

        # MULTIPLE SELECTION
        # if it was after the "CITY" and "CUSINE" then, set SELECTMODE = 'multiple'
        if not self.window:

            CityFrame = tk.Frame(self)
            tk.Label(CityFrame, text=f"Click on a {dialog_type} to select").grid()
            CityLB_scrollbar = tk.Scrollbar(CityFrame)
            self.LB = tk.Listbox(CityFrame, height=6, selectmode='multiple', yscrollcommand=CityLB_scrollbar.set)
            # self.LB.grid(row=1)
            CityLB_scrollbar.config(command=self.LB.yview)
            CityLB_scrollbar.grid(row=1, column=1, sticky='ns')

            for item in self.rest_data:
                self.LB.insert(tk.END, item)
            self.LB.grid(row=1)
            CityFrame.grid()

            select_button = tk.Button(self, text="Select", command=lambda: self.select_item('MULTIPLE'))
            select_button.grid()

    def fetch_cities(self):
        """
        fetch_cities method will query from the connected database,
        and return the locations of all restaurants, in the Locations table.
        """
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT location FROM Locations")
        cities = cursor.fetchall()
        return [city[0] for city in cities]

    def fetch_cuisines(self):
        """
        fetch_cuisines method will query from the connected database,
        and return the cuisine of all restaurants, in the Cuisine table.
        """
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT type FROM Cuisine")
        cuisines = cursor.fetchall()
        return [cuisine[0] for cuisine in cuisines]

    def fetch_restaurants(self, selection, filter_type):
        """
        fetch_restaurants method will query from the connected database,
        and return the cuisine of all restaurants, in the Cuisine table.

        the method receives a filter_type which will determine if we want to JOIN according to the Locations Table or
        the Cuisine table.

        the method will return the restaurants in that selected city, or cuisine.
        """
        cursor = self.db_connection.cursor()
        # print(selection)
        if filter_type == 'city':
            cursor.execute('''SELECT Name FROM RestaurantsDB 
                           JOIN Locations ON RestaurantsDB.Loc = Locations.id
                           WHERE Locations.location = ? ''', (selection,))
            restaurants = cursor.fetchall()
            return [restaurant[0] for restaurant in restaurants]
        elif filter_type == 'cuisine':
            cursor.execute('''SELECT Name FROM RestaurantsDB 
                           JOIN Cuisine ON RestaurantsDB.Type = Cuisine.id
                           WHERE Cuisine.type = ? ''', (selection,))
            restaurants = cursor.fetchall()
            return [restaurant[0] for restaurant in restaurants]

    def select_item(self, query):
        """
        select_item method will check to see if the selection has single or multiple
        * if single, use curselection()[0] to grab the index of the selection & index slice back into data to get choice.
        * if MULTIPLE, use curselection() to grab all selection and make a list using list comp of the selections
        """
        if query == 'SINGLE':
            index = self.LB.curselection()[0]
            self.selection = self.data[index]
        elif query == 'MULTIPLE':
            index = self.LB.curselection()
            # print(index)
            # print(type(index))
            # index = list(index)
            # print(index)
            # print(type(index[0]))
            self.selection = [self.rest_data[i] for i in index]
        self.destroy()

    def get_selection(self):
        """
        This method returns the user selection to be used in the MainWindow
        """
        return self.selection


class DisplayWindow(tk.Toplevel):
    """
    DisplayWindow Class will take a selection(restaurants selected through the Dialog Window) and
    use that to create a window for every restaurant selected.
    - Individual Display window will have
        * restaurant name,
        * address
        * cost
        * cuisine
        * and a button which will open a tab to the url of the website provided by michelin.com

    The call to the DisplayWindow from the MainClass is in a for loop, so every
    restaurant will have its own Display Window Created
    """
    def __init__(self, parent, db_connection, selection):
        super().__init__(parent)
        self.parent = parent
        self.db_connection = db_connection

        # call create_windows method to create each window
        self.create_windows(selection)

    def create_windows(self, selection):
        """
        This method will query all data and store in corresponding variables, according to the selection.
        then, display the data by tk.Label and Button for the URL
        """
        cursor = self.db_connection.cursor()

        # must query from different tables to get information

        # get name, address, url from main RestaurantsDB table
        cursor.execute('''SELECT * FROM RestaurantsDB
                          WHERE Name = ? ''', (selection,))
        restaurant = cursor.fetchone()
        name, address, url = restaurant[0], restaurant[-1], restaurant[1]
        # print(name, address, url)

        # get dollar sign from Costs table
        cursor.execute('''SELECT sign FROM Costs 
                          JOIN RestaurantsDB ON Costs.id = RestaurantsDB.Cost
                          WHERE RestaurantsDB.Name = ?''', (selection,))
        sign = cursor.fetchone()[0]
        # print(sign)


        # get cuisine detail from Cuisine Table
        cursor.execute('''SELECT * FROM Cuisine 
                          JOIN RestaurantsDB ON Cuisine.id = RestaurantsDB.Type
                          WHERE RestaurantsDB.Name = ?''', (selection,))
        cuisine = cursor.fetchone()[1]
        # print(cuisine)

        # display the restaurants data , name, address, cost, cuisine
        # add button to take to URL
        if restaurant:
            self.title(f"{restaurant[0]}")
            # name
            tk.Label(self, text="{}".format(restaurant[0]), font=("Calibri", 14, "bold")).grid()
            # address
            address = restaurant[-1].split(',')[0] + "," + restaurant[-1].split(',')[1]
            tk.Label(self, text=f"{address}", font=("Calibri", 13, "italic")).grid()
            # cost
            tk.Label(self, text=f"Cost: {sign}", font=("Calibri", 12)).grid()
            # cuisine
            tk.Label(self, text=f"Cuisine: {cuisine}", font=("Calibri", 11)).grid()
            # Add a button to get to url; use imported webbroswer to open new tab of the url of the restaurant
            tk.Button(self, text="Visit Webpage", font=("Calibri", 11), fg="blue",
                      command=lambda: webbrowser.open(url)).grid(pady=8)
        else:
            pass
        cursor.close()



if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()


#UNIT TESTING
# when app loads, clicked on City
# then Mountain View
# then both selections
# output to shell was
'''
Mountain View
(0, 1)
<class 'tuple'>
[0, 1]
<class 'int'>
# print(name, address, url) -> Doppio Zero Pizza Napoletana 160 Castro St., Mountain View, 94041, USA https://guide.michelin.com/us/en/california/mountain-view/restaurant/doppio-zero-pizza-napoletana
# print(sign)  -> $$
# print(cuisine) -> Pizza
Chez TJ 938 Villa St., Mountain View, 94041, USA https://guide.michelin.com/us/en/california/mountain-view/restaurant/chez-tj
$$$$
Contemporary
'''
