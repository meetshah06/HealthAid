import requests, json,pprint

#key=AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM
#url='https://maps.googleapis.com/maps/api/distancematrix/json?origins=KJ Somaiya&destinations=19.1867634,72.9750417&departure_time=now&key=AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM'

url='https://maps.googleapis.com/maps/api/geocode/json?address=origins=KJ Somaiya&key=AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM'
a=requests.get(url)

j=a.json()['results'][0]['geometry']['location']

lat,lng=j['lat'],j['lng']
print(j['lat'],j['lng'])

url='https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(lat)+','+str(lng)+'&rankby=distance&type=hospital&key=AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM'
#can use rankby=distance or radius=500
a=requests.get(url).json()['results']
print(len(a))
x=[]
print(a)
''''
for i in a:
    b1=requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?origins=KJ Somaiya&destinations=place_id:'+i['place_id']+'&departure_time=now&key=AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM').json()
    print('b1',b1)
    b1=b1['rows'][0]['elements'][0]['duration_in_traffic']['value']

    x.append([i['place_id'],i['name'],b1])
print(x)

#url='https://maps.googleapis.com/maps/api/distancematrix/json?origins=KJ Somaiya&destinations=19.1867634,72.9750417&departure_time=now&key=AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM'
'''



