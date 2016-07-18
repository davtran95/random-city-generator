import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import random
import os
from zipfile import ZipFile
import urllib.request
import shutil


def parse_info(line):
    """Takes in a line with the 'geoname' format and returns the 'name' and 'population'"""
    line = str(line).split("\t")  # splitting the input text by tab characters
    return line[2], line[6], line[10], line[14]  # 1:ascii name, 7:feature class, 10:admin1 code, 14:population


def build_list(file_stream):
    """Takes file stream of 'geonames.org' dump, and builds list with only necessary data"""
    cities = []
    with file_stream as infile:
        for line in infile:
            parsed_line = parse_info(line)  # tuple: (name, feature class, admin1 code, population)
            feature_class = parsed_line[1]
            if feature_class == "P":  # check if feature class is 'P' which denotes a city, village, etc.
                cities.append(parsed_line)

    return cities


def population_filter(city_list, min_pop):
    """Takes in a list of city tuples, and filters them by a minimum population """
    filtered_list = []
    for item in city_list:
        if int(item[3]) >= int(min_pop):
            filtered_list.append(item)
    return filtered_list


def get_file_path():
    """Opens a dialog box for the user to select the 'geonames' dump location"""
    root = tk.Tk()
    root.withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(title="Open built data file")  # show an "Open" dialog box and return file path
    return filename


def get_random_city(city_list):
    """Uses randrange to return the name of a city randomly"""
    return city_list[random.randrange(0, len(city_list))]


def grab_new_data():
    """Downloads the US zip file from the Geonames download server and unzips the US.txt file. Uses build_list
    function to build the list of tuples and saves it to a user specified location"""
    print("Downloading, please wait...")

    url = "http://download.geonames.org/export/dump/US.zip"
    download_file = "US.zip"
    text_file = "US.txt"

    with urllib.request.urlopen(url) as response, open(download_file, 'wb') as out_file:
        # urlopen returns a file-like object, and we save the object to 'download_file'
        shutil.copyfileobj(response, out_file)  # Copy the contents of the file-like object to file-like object
        out_file.close()  # close object so we can unzip it
        print("Download finished")
        with ZipFile(download_file) as zf:
            zf.extract(text_file)  # extracts US.txt to current directory
            print("Building list, please wait... ")
            with open(text_file, encoding="utf8") as us:
                city_list = build_list(us)  # format for output

    ''' #Offline debugging mode
    with ZipFile(download_file) as zf:
        zf.extract(zipped_file)
        print("Building list, please wait... ")
        with open(zipped_file, encoding="utf8") as us:
            city_list = build_list(us)
    '''

    os.remove(download_file)  # remove files that won't be used anymore
    os.remove(text_file)

    root = tk.Tk()
    root.withdraw()  # we don't want a full GUI, so keep the root window from appearing

    filename = ''

    while True:
        filename = asksaveasfilename(title="Save built data file", filetypes=(("Text files", ".txt"),
                                                                              ("All Files", "*.*")))
        # show an "Save" dialog box with default extension .txt and return file path

        if filename is not None:
            break

    with open(filename, 'w') as to_write:
        print("Exporting data, please wait...")
        for item in city_list:
            to_write.write(str(item) + '\n')
    print("Done")
    return filename


def main():
    print("*******************************************")
    print("* Welcome to the Random US City Generator *")
    print("*******************************************\n")

    path_of_data = ''

    while True:  # loops until valid input is detected and data is loaded
        mode_data = input("Enter n to get new data or e to load up an existing built data file: ")
        if mode_data == 'e':  # user wants to use an existing built data file
            path_of_data = get_file_path()
            break
        elif mode_data == 'n':  # user wants to get new data from the Internet
            path_of_data = grab_new_data()
            break
        else:
            print("Invalid input. Please try again.")

    main_list = []

    with open(path_of_data) as data:
        print("Loading data, please wait...")
        for line in data:
            main_list.append(eval(line))  # loads the data into a list as tuples

    filtered_list = main_list  # reserve the main_list as an unfiltered list

    print("Please select a mode:")
    print("Simply press enter for a random city")
    print("Enter p to set a population minimum")
    print("Enter q to quit")

    while True:
        mode = input("Mode: ")
        if mode == "q":  # quit
            break
        elif mode == 'p':  # user wants to set a new population minimum
            filtered_list = population_filter(main_list, input("Please enter minimum population: "))
            print("List has been filtered by population.")
        elif mode == '':  # return a random city
            random_city = get_random_city(filtered_list)
            print(random_city[0] + ", " + random_city[2] + " Population: " + "{:,}".format(int(random_city[3])))
            # print out name of city and population formatted with comma separated thousands place.


if __name__ == "__main__":
    main()
