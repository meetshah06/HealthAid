from healthaid import db#,login_manager
from datetime import datetime

# from flask_login import UserMixin

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')#form google.
    emergency_contact1 = db.Column(db.Integer, nullable=True)
    emergency_contact2 = db.Column(db.Integer, nullable=True)#optional second contact.

    # hospitals = db.relationship("Hospital", backref="user", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Hospital(db.Model):
    place_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    longi = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    no_of_users = db.Column(db.Integer, nullable=True)#number of users who have rated
    vacancy = db.Column(db.Integer, nullable= False)
    total_beds = db.Column(db.Integer, nullable= False )
    sev1_bud = db.Column(db.Integer,nullable=False)
    sev2_bud = db.Column(db.Integer,nullable=False)
    sev3_bud = db.Column(db.Integer,nullable=False)
    sev4_bud = db.Column(db.Integer,nullable=False)
    sev5_bud = db.Column(db.Integer,nullable=False)
    no_of_doctors = db.Column(db.Integer, nullable=False)
    no_of_nurses = db.Column(db.Integer, nullable=False)
    no_of_equipment = db.Column(db.Integer, nullable=False)
    # user_id = Column(db.Integer, db.ForeignKey('User.id'))#for 1 to many realtionships from the user. 
    # email = db.Column(db.String(120), unique=True, nullable=False)
    # password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Hospital('{self.name}', '{self.address}', '{self.rating}')"


class Algo(db.Model):
    level = db.Column(db.Integer, nullable=False, primary_key=True)
    budget = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    quality = db.Column(db.Float, nullable=False)
