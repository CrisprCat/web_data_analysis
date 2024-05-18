# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re
# the URL of the home page of the target website
base_url = 'https://www.makler-bethke.de/vermietung'

# retrieve the data of the URL and store it in a python object
## avoiding bot detection
headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
page = requests.get(base_url, 
                    headers=headers)
## creating a beautiful soup object with page.content 
soup = BeautifulSoup(page.content,
                     "html.parser")
## extracting all links in a list
links = []
for link in soup.find_all('a'):
    links.append(link.get('href'))

# filtering the urls to only ones containing rent flats 
## turning the list into a pandas series
rent_flat_urls = pd.Series(links)
## extracting index of 'https://www.makler-bethke.de/vermietung'
index_start = rent_flat_urls[rent_flat_urls == 'https://www.makler-bethke.de/vermietung'].index.tolist()[0]
## extracting index of 'https://www.makler-bethke.de/10gruende'
index_stop = rent_flat_urls[rent_flat_urls == 'https://www.makler-bethke.de/10gruende'].index.tolist()[0]
## extract all urls between '/vermietung' and '/10gruende'
rent_flat_urls = rent_flat_urls.iloc[index_start+1:index_stop]

# setting up crwaling mechanism
## creating an array where all scraped data will be stored in
flats = []
## looping through every url to extract information about flats available for rent
for url in rent_flat_urls:
    URL = url
    ## retrieving the data of the URL and store it in a python object
    flat_page = requests.get(URL)
    ## creating a beautiful soup object with page.content 
    flat_soup = BeautifulSoup(flat_page.content,
                              "html.parser")
    # extracting specific elements by their ID from the DOM
    ## the ID for the specific element was identified through the dev console in the browser
    flat = flat_soup.find(id="SITE_CONTAINER")
    ## the different attributes of a flat are in multiple elements of a specific class
    ## extracting all elements of that class to safe all attributes of one flat in a list
    flat_elements = flat.find_all("p",
                                  class_ = "font_8 wixui-rich-text__text")
    flat_address = flat.find_all("h3",
                                 class_ = "font_3 wixui-rich-text__text")
    # iterating over the list of flat_elements to extract the flat attributes
    ## defining regex to use them to extract the interesting text
    type_pattern = re.compile(r'^Typ: ')
    floor_pattern = re.compile(r'^Etage: ')
    size_pattern = re.compile(r'^Wohnfläche: ')
    available_date_pattern = re.compile(r'^Bezugsfrei ab: ')
    room_number_pattern = re.compile(r'^Zimmer: ')
    bedroom_number_pattern = re.compile(r'^Schlafzimmer: ')
    bathroom_number_pattern = re.compile(r'^Badezimmer: ')
    base_rent_pattern = re.compile(r'^Kaltmiete: ')
    ancillary_cost_pattern = re.compile(r'^Nebenkosten: ')
    heating_cost_pattern = re.compile(r'^Heizkosten: ')
    total_rent_pattern = re.compile(r'^Gesamtmiete: ')
    heating_pattern = re.compile(r'Heizungsart')
    district_pattern = re.compile(r'^\d{5}')

    type = None
    floor = None
    size = None
    date_available = None
    room_number = None
    bedroom = None
    bathroom = None
    base_rent = None
    ancillary_cost = None
    heating_cost = None
    total_rent = None
    heating = None
    district = None
    ## iterating through the elements
    for flat_element in flat_elements:
        if type_pattern.match(flat_element.text.strip()):
            type = flat_element.text
        elif floor_pattern.match(flat_element.text.strip()):
            floor = flat_element.text
        elif size_pattern.match(flat_element.text.strip()):
            size = flat_element.text    
        elif available_date_pattern.match(flat_element.text.strip()):
            date_available = flat_element.text
        elif room_number_pattern.match(flat_element.text.strip()):
            room_number = flat_element.text
        elif bedroom_number_pattern.match(flat_element.text.strip()):
            bedroom_number = flat_element.text
        elif bathroom_number_pattern.match(flat_element.text.strip()):
            bathroom_number = flat_element.text
        elif base_rent_pattern.match(flat_element.text.strip()):
            base_rent = flat_element.text 
        elif ancillary_cost_pattern.match(flat_element.text.strip()):
            ancillary_cost = flat_element.text
        elif heating_cost_pattern.match(flat_element.text.strip()):
            heating_cost = flat_element.text
        elif total_rent_pattern.match(flat_element.text.strip()):
            total_rent = flat_element.text
        elif heating_pattern.match(flat_element.text.strip()):
            heating = flat_element.text

    street = flat_address[0].text.strip()
    district = flat_address[1].text.strip()
## transforming the scraped data into a dictionary and append it to the flats list
    flats.append(
       {
           'type': type,
           'etage': floor,
           'size': size,
           'date_available': date_available,
           'room_number': room_number,
           'bedroom': bedroom,
           'bathroom': bathroom,
           'base_rent': base_rent,
           'ancillary_cost': ancillary_cost,
           'heating_cost': heating_cost,
           'total_rent': total_rent,
           'heating': heating,
           'street': street,
           'district': district
       }
    )

# saving the extracted information in a .csv file
## reading  the "flats.csv" file and creating it if not present
csv_file = open('flats.csv', 'w', encoding='utf-8', newline='')
## initializing the writer object to insert data into the .csv file
writer = csv.writer(csv_file)

## writing the header of the CSV file
writer.writerow(['type', 
                 'etage', 
                 'size', 
                 'date_available', 
                 'room_number', 
                 'bedroom',
                 'bathroom',
                 'base_rent',
                 'ancillary_cost',
                 'heating_cost',
                 'total_rent',
                 'total_rent',
                 'heating',
                 'street',
                 'district'])

## writing information stored in a list for each flat into the .csv file
for flat in flats:
    writer.writerow(flat.values())
# terminating the operation and releasing the resources
csv_file.close()