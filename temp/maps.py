import googlemaps, requests, json
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM')
'''  
# Requires cities name 
my_dist = gmaps.distance_matrix('deepak cinema ','dadar railway station')
  
# Printing the result 
print(my_dist) 
'''
geocode_result = gmaps.geocode('Deepak Cinema')
loc='https://maps.googleapis.com/maps/api/geocode/json?address=Deepak Cinema&key=AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM'
#url='https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=deepak cinema&key=AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM'

print(geocode_result)