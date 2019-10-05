from healthaid.models import Algo

def getpercentage(budget, rating, duration, maxduration, severitylevel,
                         no_of_doctors, no_of_nurses, no_of_equipments,no_of_beds):
    # Get all the factor values for the user's severity level
    info = Algo.query.filter_by(level=severitylevel)
    # This is the weightage of budget to be considered
    budget_factor = info[0].budget*100
    # This is the weightage of rating to be considered
    rating_factor = info[0].rating*100
    # This is the weightage of duration to be considered
    duration_factor = info[0].duration*100 
    # This is the weightage of quality to be considered
    quality_factor = info[0].quality*100
    
    # Upper bound of budget range is a multiple of 3
    # Divide user budget by the maximum budget in that range to find % and multiply it by budget factor
    budget_value = budget_factor*(1-(budget/(1000*(3**(severitylevel-1)))))
    # Calc % of difference between duration of current 
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

print(getpercentage(800,5,900,3000,1,30,50,150,200))


# 100,0,900,3000,1,10,25,100,80           72.52734375