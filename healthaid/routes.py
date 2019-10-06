from healthaid import app,db
import requests, json
import urllib.request as urllib2
from flask import flash, render_template, request, session, url_for, redirect
from healthaid.models import User, Hospital, Algo
from healthaid.forms import HospitalRegistrationForm
api_key= 'AIzaSyCdVpvGO8uGeUlz7o7qQBrMqyWb0P6JkIM'


def getHospitalDetails(source, severity):
    import copy
    severity=int(severity)
    url='https://maps.googleapis.com/maps/api/geocode/json?address=origins='+source+'&key='+api_key
    lat,lng = 0.0,0.0
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
    #overall
    #quality
    #time
    #budget
    d0=copy.deepcopy(data)
    d1=copy.deepcopy(data)
    d2=copy.deepcopy(data)
    d3=copy.deepcopy(data)
    d0.sort(key=lambda x:x[0],reverse=True)
    d1.sort(key=lambda x:x[6],reverse=True)
    d2.sort(key=lambda x:x[10])
    d3.sort(key=lambda x:x[11])
    # print(d0[0],d1[0],d2[0],d3[0])
    return [d0,d1,d2,d3,source,lat,lng]
    #return render_template('index.html', data=json.dumps(data),source=source, source_lat=lat, source_long=lng)
    

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
    equipment_value = no_of_equipments/(1.5*no_of_beds)
    if equipment_value > 1:
        equipment_value = 1
    quality_value = quality_factor*(0.6*doctor_value + 0.25*nurse_value + 0.15*equipment_value)
    hospital=Hospital.query.filter_by(place_id=place_id).first()
    return [budget_value + duration_value + (rating_value+quality_value)/2,place_id,hospital.name,
                    hospital.address,hospital.lat,hospital.longi,hospital.rating,hospital.no_of_users,hospital.vacancy,hospital.total_beds,duration,budget]        


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
                # else:
                #     # print(i)
        try:
            maxduration = max([i[5] for i in data])
        except:
            pass
        for i in data:
            percentages.append(getpercentage(i[0],i[3],i[4],i[5],maxduration,i[6],i[7],i[8],i[9],i[10]))
        # print(percentages)
        return percentages
                    



# Check if hospital with place_id has vacancy or n
'''
def checkVacancy(place_id):
    hospital = Hospital.query.filter_by(place_id=place_id)
    total_beds = hospital.total_beds
    vacancy = hospital.vacancy
    if(vacancy>0):
        # If vacant then return the no of vacancy and the total beds 
        return vacancy, total_beds
    else:
        return False
'''
@app.route('/',methods=['GET','POST'])
@app.route('/home',methods=['GET','POST'])
def home():
    if request.method=="POST":
        print(request.form)
        print("type="+str(request.form['severity']))
        if request.form['search']!= '':
            x=getHospitalDetails(request.form['search'],request.form['severity'])
        else:
            lat = request.args.get('lat')
            lng = request.args.get('lng')
            severity = request.args.get('severity')
            address = json.loads(urllib2.urlopen('https://maps.googleapis.com/maps/api/geocode/json?latlng='+str(lat)+','+str(lng)+'&key='+api_key).read())['results'][0]['formatted_address']
            x=getHospitalDetails(address,request.form['severity'])
        print(type(x[5]))
        print(type(x[6]))
        data = {
            'd0':list(x[0][:min(3,len(x[0]))]),
            'd1':list(x[1][:min(3,len(x[1]))]),
            'd2':list(x[2][:min(3,len(x[2]))]),
            'd3':list(x[3][:min(3,len(x[3]))]),
            'source':x[4],
            'lat':str(x[5]),
            'lng':str(x[6])
        }
        return render_template('index.html',data=data)
  
    return render_template('index.html')


@app.route('/updateusers',methods=['GET'])
def updateUsers():
    id=request.args.get('id')
    uname=request.args.get('name')
    email=request.args.get('email')
    img=request.args.get('image')
    if not User.query.filter_by(id=id).first():
        u=User(id=id,username=uname,email=email,image_file=img)
        db.session.add(u)
        db.session.commit()
        print ('users updated')
        return 'success'


@app.route("/RegisterHospi", methods=['GET', 'POST'])
def registerHospi():
    form = HospitalRegistrationForm()
    if request.method == 'POST':
        print("post")
        # If all form values are valid
        if form.validate_on_submit():
            print("hmm")
            # Get all the form values
            name = form.name.data
            address = form.address.data
            email = form.email.data
            vacancy = form.vacancy.data
            total_beds = form.total_beds.data

            sev1_bud = form.sev1_bud.data
            sev2_bud = form.sev2_bud.data
            sev3_bud = form.sev3_bud.data
            sev4_bud = form.sev4_bud.data
            sev5_bud = form.sev5_bud.data

            num_doc = form.num_doc.data
            num_nurse = form.num_nurse.data
            num_equip = form.num_equip.data

            password = form.password.data
            confirm_password = form.confirm_password.data

            if(confirm_password == password):
                # myloc = json.loads(urllib2.urlopen('https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key='+api_key).read())
                # lat = myloc['results'][0]['geometry']['location']['lat']
                # lng = myloc['results'][0]['geometry']['location']['lng']
                h=Hospital(place_id=placeholder1,name=name,address=addressplaceholder2,lat=lat,longi=lng,rating=placeholder5 ,no_of_users=placeholder6,vacancy=int(vacancy),total_beds=int(total_beds),sev1_bud=int(sev1_bud),sev2_bud=int(sev2_bud),sev3_bud=int(sev3_bud),sev4_bud=int(sev4_bud),sev5_bud=int(sev5_bud),no_of_doctors=int(num_doc),no_of_nurses=int(num_nurse),no_of_equipment=int(num_equip),email=email,password=password)#crypt the password.

                try:
                    db.session.add(h)
                    db.session.commit()#what happens on error.
                except Exception as e:
                    print("error occured:",e)
            return redirect(url_for('home'))
    return render_template('register_hospi.html' ,title='Register', form=form)


@app.route('/HospiProfile/<hid>',methods=["POST","GET"])
def trial(hid):
    obj=Hospital.query.filter_by(place_id=hid).first()
    form = HospitalRegistrationForm()
    print("this is obnj;",obj)
    if form.validate_on_submit():
        vacancy = form.vacancy.data
        total_beds = form.total_beds.data

        sev1_bud = form.sev1_bud.data
        sev2_bud = form.sev2_bud.data
        sev3_bud = form.sev3_bud.data
        sev4_bud = form.sev4_bud.data
        sev5_bud = form.sev5_bud.data

        num_doc = form.num_doc.data
        num_nurse = form.num_nurse.data
        num_equip = form.num_equip.data

        try:
            db.session.add(h)
            db.session.commit()
        except Exception as e:
            print("error occured:",e)
        return render_template('HospiProfile.html',Hospital=obj,form=form)
    else:
        return render_template('HospiProfile.html',Hospital=obj,form=form)

@app.route('/trial2')
def trial2():
    return render_template('userreview.html')
@app.route('/feedback')
def feedback():
    if request.method =="POST":
        quality = request.POST['Quality']
        budget = request.POST['Budget']
        severity =request.POST['Severity']
        algo = Algo.query.filter_by(level=severity)
        algo.quality = algo.quality +(quality-3)*0.01
        algo.rating = algo.quality
        algo.budget = algo.budget + (budget-3)*0.01
        algo.duration = 1-algo.budget-algo.quality
        print("tp")
        db.session.commit()
        return redirect('home')
