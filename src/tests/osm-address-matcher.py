import json
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="osm_test_matching")

addresses = ['130 lower drumcondra road, dublin 9, ireland',
             'abbey road, deansgrange, dublin',
			 'KILMEADEN,waterford', 
			 'FOXWOOD, dungarven,waterford']


with open("test_address.txt","w+") as f:
    
    for i in addresses:

        try:
            location = geolocator.geocode(str(i))
            line_to_add = i + '|' + location.address + '|' + \
			              str(location.latitude) + ',' + \
			              str(location.longitude) + '\n'
        except:
            line_to_add = i + '|' + 'not not found \n'

        print(line_to_add)
        
        f.write(line_to_add)
