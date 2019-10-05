from healthaid.models import Hospital, Algo
import requests, json


def getpercentage(budget, rating, duration, maxduration, severitylevel,
                         no_of_doctors, no_of_nurses, no_of_equipments,no_of_beds):
    # Get all the factor values for the user's severity level
    info = Algo.query.filter_by(level=severitylevel)
    # This is the weightage of budget to be considered
    budget_factor = info.budget*100
    # This is the weightage of rating to be considered
    rating_factor = info.rating*100
    # This is the weightage of duration to be considered
    duration_factor = info.duration*100 
    # This is the weightage of quality to be considered
    quality_factor = info.quality*100
    
    # Upper bound of budget range is a multiple of 3
    # Divide user budget by the maximum budget in that range to find % and multiply it by budget factor
    budget_value = budget_factor*(1-(budget/(1000*(3**(severitylevel-1)))))
    
    duration_value = duration_factor*((maxduration-duration)/maxduration)
    rating_value = rating_factor*(0.2*rating)
    doctor_value = no_of_doctors/(0.2*no_of_beds)
    if doctor_value > 1:
        doctor_value = 1
    nurse_value = no_of_nurses/(0.4*no_of_beds)
    if nurse_value > 1:
        nurse_value = 1
    equipment_value = no_of_equipments/(1.5*no_of_equipments)
    if equipment_value > 1:
        equipment_value = 1
    quality_value = quality_factor*(0.6*doctor_value + 0.25*nurse_value + 0.15*equipment_value)
    
    return budget_value + duration_value + (rating_value+quality_value)/2

api_key = 'AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM'
def getHospitalDetails(source,severity):
    url='https://maps.googleapis.com/maps/api/geocode/json?address=origins='+source+'&key='+api_key
    while True:
        req=requests.get(url).json()
        if req['status']=="OK":
            # If results present
            if req['results']:
                req=req['results'][0]['geometry']['location']
                # Get the latitude and longitude
                lat,lng=req['lat'],req['lng']
                data=getNearbyData(lat,lng,severity)
                # print(data)
            break

def getNearbyData(lat,lng,severity):
    url='https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(lat)+','+str(lng)+'&rankby=distance&type=hospital&key='+api_key
    req=requests.get(url).json()
    data=[]
    percentages = []
    if req['status']=="OK":
        # If results present
        if req['results']:
            a=req['results']
            for i in a:
                # Check if hospital has signed up in database
                hospital=Hospital.query.filter_by(place_id=i['place_id'])
                print(hospital)
                if hospital:
                    # If vacancy is present
                    if hospital.vacancy > 0:
                        b=requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?origins='+str(lat)+','+str(lng)+'&destinations=place_id:'+i['place_id']+'&departure_time=now&key='+api_key).json()
                        if b['rows']:
                            if severity == 1:
                                sever_bud = hospital.sev1_bud
                            elif(severity == 2):
                                sever_bud = hospital.sev2_bud
                            elif(severity == 3):
                                sever_bud = hospital.sev3_bud
                            elif severity == 4:
                                sever_bud = hospital.sev4_bud
                            else:
                                sever_bud = hospital.sev5_bud
                            rating = hospital.rating
                            severitylevel = severity
                            doctors = hospital.no_of_doctors
                            nurses = hospital.no_of_nurses
                            equips = hospital.no_of_equipments
                            duration = b['rows'][0]['elements'][0]['duration_in_traffic']['value']
                            data.append([i['place_id'],i['name'],hospital.vacancy,sever_bud,rating,duration,severitylevel,doctors,nurses,equips,hospital.beds])
        maxduration = max([i[5] for i in data])
        for i in data:
            percentages.append(getpercentage(i[3],i[4],i[5],maxduration,i[6],i[7],i[8],i[9],i[10]))
        print(percentages)

getHospitalDetails('Oasis Sapphire,Thane',2)