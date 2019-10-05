from healthaid.models import Hospital, Algo
import requests,json,random
from healthaid import db


def getpercentage(place_id,budget, rating, duration, maxduration, severitylevel,
                         no_of_doctors, no_of_nurses, no_of_equipments,no_of_beds):
    # Get all the factor values for the user's severity level
    info = Algo.query.filter_by(level=severitylevel)[0]
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
    # Calc % by finding diff b/w max time duration and duration of current hospital and multiply with duration factor
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
    
    return [place_id,budget_value + duration_value + (rating_value+quality_value)/2]

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
    print(req['results'][0])
    data=[]
    percentages = []
    if req['status']=="OK":
        # If results present
        if req['results']:
            a=req['results']
            for i in a:
                print(i['name'])
                # Check if hospital has signed up in database
                hospital=Hospital.query.filter_by(place_id=i['place_id']).first()
                if hospital:
                    # If vacancy is present
                    if hospital.vacancy > 0:
                        b=requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?origins='+str(lat)+','+str(lng)+'&destinations=place_id:'+i['place_id']+'&departure_time=now&key='+api_key).json()
                        if b['rows']:
                            if(severity == 1):
                                sever_bud = hospital.sev1_bud
                            elif(severity == 2):
                                sever_bud = hospital.sev2_bud
                            elif(severity == 3):
                                sever_bud = hospital.sev3_bud
                            elif(severity == 4):
                                sever_bud = hospital.sev4_bud
                            else:
                                sever_bud = hospital.sev5_bud
                            rating = hospital.rating
                            severitylevel = severity
                            doctors = hospital.no_of_doctors
                            nurses = hospital.no_of_nurses
                            equips = hospital.no_of_equipment
                            duration = b['rows'][0]['elements'][0]['duration_in_traffic']['value']
                            data.append([i['place_id'],i['name'],hospital.vacancy,sever_bud,rating,duration,severitylevel,doctors,nurses,equips,hospital.total_beds])
                else:
                    place_id = i['place_id']
                    rating = i['rating']
                    lat = i['geometry']['location']['lat']
                    lng = i['geometry']['location']['lng']
                    user_ratings_total = i['user_ratings_total']
                    name = i['name']
                    address = json.loads(urllib2.urlopen('https://maps.googleapis.com/maps/api/geocode/json?latlng='+str(lat)+','+str(lng)+'&key='+api_key).read())['results'][0]['formatted_address']
                    vacancy = random.randint(0,15)
                    total_beds = random.randint(50,100)
                    sev1_bud = random.randint(1,10)*100
                    sev2_bud = ((sev1_bud*(1+random.random()*2))//100)*100
                    sev3_bud = ((sev2_bud*(1+random.random()*2))//100)*100
                    sev4_bud = ((sev3_bud*(1+random.random()*2))//100)*100
                    sev5_bud = ((sev4_bud*(1+random.random()*2))//100)*100
                    print(place_id)
                    try:
                        h = Hospital(place_id=place_id,name=name,address=address,lat=lat,longi=lng,rating=rating,no_of_users=user_ratings_total,vacancy=vacancy,total_beds=total_beds,sev1_bud=,sev2_bud=int(i[10]),sev3_bud=int(i[11]),sev4_bud=int(i[12]),sev5_bud=int(i[13]),no_of_doctors=random.randint(0,round(0.2*i[9])),no_of_nurses=random.randint(0,round(0.4*i[9])),no_of_equipment=random.randint(0,round(1.5*i[9])))
                        db.session.add(h)
                    except Exception as e:
                        print(e)
                        pass
                db.session.commit()
                    # url = 'https://maps.googleapis.com/maps/api/geocode/json?address=place_id:'+str(i['place_id'])+'&key='+str(api_key)
                    # req=requests.get(url).json()
                    # print(req)
        maxduration = max([i[5] for i in data])
        for i in data:
            percentages.append(getpercentage(i[0],i[3],i[4],i[5],maxduration,i[6],i[7],i[8],i[9],i[10]))
        print(percentages)
# hospital=Hospital.query.all()
# print(len(hospital))
# place_id,b = [],[]
# a=[['ChIJYV-VT6XH5zsR9yROCj6o31o', 'Quali5Care And Consulting Private Limited', 'Surya House, Rd Number 7, Opposite R.N Gandhi High School, Rajawadi Colony, Vidyavihar, Mumbai, Maharashtra 400077, India', 19.07734349999999, 72.9007511, 4.7, 14, 8, 55, 300, 500.0, 1100.0, 2200.0, 4000.0],['ChIJo3p2kSjG5zsRDKHl416JUtk', "Dr. Bhaskar Patel's Hospital", '38, Rd Number 7, Neelkhanth Valley, Ghatkopar East, Mumbai, Maharashtra 400077, India', 19.076975, 72.902692, 5, 1, 7, 57, 100, 200.0, 500.0, 800.0, 800.0],['ChIJq6qqap7I5zsR237YqUbz68g', 'Mumbai Heart Clinic', '37, Pestom Sagar Rd Number 2, Chembur West, Pestom Sagar Colony, Chembur, Mumbai, Maharashtra 400089, India', 19.0694549, 72.903847, 4.4, 70, 9, 98, 1000, 1000.0, 2400.0, 5600.0, 15200.0],['ChIJq6qqqs_H5zsR_kBjsn8Z_7E', 'Rajawadi Hospital', 'B-69, Ramnagar Co. Op.Hsg. Soc.,Rajawadi, Near Rajawadi Hospital, Ghatkopar East, Mumbai, Maharashtra 400077, India', 19.0786838, 72.90120619999999, 3.7, 164, 8, 76, 500, 1000.0, 2700.0, 6200.0, 15800.0],['ChIJqR2AVCHG5zsRHB0aRW-bmbc', 'Sanjeevni Hospital', '35, Shanti Path, Satyalaxmi Society, Chembur West, Pestom Sagar Colony, Ghatkopar East, Mumbai, Maharashtra 400089, India', 19.0701946, 72.9043451, 4, 2, 7, 81, 100, 200.0, 200.0, 300.0, 300.0],['ChIJM-nDGynG5zsRFLLj98iVrgE', 'Vikas Fracture Clinic And Nursing Home', '14, Vasant Rao Bhagwati Marg, Rajawadi Colony, Ghatkopar East, Mumbai, Maharashtra 400077, India', 19.079314, 72.90280249999999, 3.7, 3, 15, 96, 400, 900.0, 900.0, 1900.0, 3700.0],['ChIJJ6h1FNbH5zsRDtvaMOD8t6o', 'Ashirwad Heart Hospital', '1, Vivek, 67, Tilak Road, Ghatkopar East, Mumbai, Maharashtra 400077, India', 19.0761757, 72.9055305, 3.1, 28, 7, 91, 100, 100.0, 200.0, 500.0, 1400.0],['ChIJh4w7MSnG5zsRLjrciu8ky2w', 'Ashwini Maternity (Tank) Hospital', 'Office No.27, Ambika Darshan, MG Road, Ghatkopar East, Mumbai, Maharashtra 400077, India', 19.0799937, 72.90422269999999, 5, 2, 8, 65, 300, 500.0, 500.0, 1300.0, 2100.0],['ChIJQxd1XhrH5zsRrI4ivqAiw-Q', 'Orthos OSC', '7, MG Road, Rajawadi Colony, Ghatkopar East, Mumbai, Maharashtra 400077, India', 19.0808584, 72.9040859, 0, 0, 14, 57, 100, 100.0, 100.0, 200.0, 500.0],['ChIJF72QNw_H5zsRVbc8ENaz_bo', 'Samartha Maternity & Multispeciality Hospital (Dr.Preeti A Shirkande, Dr.Abhay K Shirkande)', 'Neelkanth Market - Ghatkopar (East), Shop No.8, Neelkant Market Co-Operative Housing Society Limited,, M. G Road, Rajawadi Colony, M G Road, Neelkanth Market,, Ghatkopar (East), Mumbai 400077, Mumbai, Maharashtra 400077, India', 19.081161, 72.9041566, 4.9, 83, 4, 52, 1000, 2200.0, 4800.0, 12400.0, 27300.0],['ChIJVxrZfJvH5zsR3n9a5uiqwy0', 'Dr. Preeti A Shirkande (SAMARTHA Maternity and Multispeciality Hospital)', 'Gandhi Market, Ghatkopar East, Mumbai, Maharashtra 400077, India', 19.081239, 72.9041842, 5, 1, 13, 51, 1000, 2700.0, 6500.0, 8300.0, 21800.0],['ChIJSUCnD6HI5zsR-W-4kYylNT8', 'Shrimati Diwaliben Mohanlal Mehta Maa Sarvasadharan Rugnalay', '2, Postal Colony Rd, Postal Colony, Chembur, Mumbai, Maharashtra 400071, India', 19.0619309, 72.89646739999999, 3.3, 30, 5, 90, 800, 900.0, 2300.0, 4000.0, 8400.0],['ChIJU7LJOB_G5zsRbrlJcJfCXBs', 'Dhanvantri Clinic', 'PL Lokhande Marg, Sector 5, New Garib Janta Nagar, Chedda Nagar, Mumbai, Maharashtra 400089, India', 19.0630207, 72.9036399, 0, 0, 0, 90, 1000, 1500.0, 3100.0, 7300.0, 21200.0],['ChIJOzPGTY_I5zsR_lHv0AOGmJs', 'Kohinoor Hospital', 'Kohinoor city,Kirol Road ,Off LBS Marg, Ali Yavar Jung, Kurla West, Kurla, Mumbai, Maharashtra 400070, India', 19.0760717, 72.8862889, 4, 533, 4, 66, 200, 200.0, 200.0, 300.0, 500.0],['ChIJV4oOTBnG5zsRqtKlfLrgbY8', 'Kher Hospital', '57, DK Sandu St, Chembur Gaothan, Chembur, Mumbai, Maharashtra 400071, India', 19.060747, 72.8986541, 4.3, 11, 3, 54, 1000, 2900.0, 3900.0, 11400.0, 32900.0],['ChIJM9niUFbP5zsR6ZEy8YIJ0lo', 'Hegde Hospital', '70-H, 1st Rd, Chembur Gaothan, Chembur, Mumbai, Maharashtra 400071, India', 19.060653, 72.899652, 4.5, 4, 8, 51, 700, 800.0, 2200.0, 3400.0, 8900.0],['ChIJM9niUFbP5zsRXlBT0TTDA2M', 'Dr Das Hospital', 'Gagangiri Building, Rd Number 18, Chembur Gaothan, Chembur, Mumbai, Maharashtra 400071, India', 19.0597426, 72.899776, 3.3, 15, 0, 76, 500, 500.0, 800.0, 2100.0, 2800.0],['ChIJEc0V4C3G5zsRgs3nl63sQRQ', "Vatsal Nicu And Children's Hospital", 'Station Road, Hingwala Ln, Saibaba Nagar, Pant Nagar, Ghatkopar East, Mumbai, Maharashtra 400077, India', 19.082367, 72.909245, 2, 4, 4, 76, 400, 900.0, 1400.0, 3600.0, 4500.0],['ChIJETEdVdXH5zsRM-kCgra76-o', 'New Taj Hospital, Ganesh Maidan Marg, Ghatkopar West, Mumbai, Maharashtra', 'Ganesh Maidan Marg, Chirag Nagar, Ghatkopar West, Mumbai, Maharashtra 400086, India', 19.0872394, 72.8989838, 0, 0, 11, 84, 700, 700.0, 1300.0, 3000.0, 5900.0]]
# for j in hospital:
#     place_id.append(j.place_id)
# for i in a:
#         if i[0] in place_id:
#             pass
#         else:
#             b.append(i)
# print(b)
# for i in b:
#     try:
#         h = Hospital(place_id=i[0],name=i[1],address=i[2],lat=i[3],longi=i[4],rating=i[5] ,no_of_users=i[6],vacancy=i[7],total_beds=i[9],sev1_bud=int(i[9]),sev2_bud=int(i[10]),sev3_bud=int(i[11]),sev4_bud=int(i[12]),sev5_bud=int(i[13]),no_of_doctors=random.randint(0,round(0.2*i[9])),no_of_nurses=random.randint(0,round(0.4*i[9])),no_of_equipment=random.randint(0,round(1.5*i[9])))
#         db.session.add(h)
#     except Exception as e:
#         print(e)
#         pass
# db.session.commit()
# hospital=Hospital.query.all()
# print(len(hospital))
getHospitalDetails('KJ Somaiya',2)
