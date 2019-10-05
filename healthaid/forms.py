from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
# from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
# from recruiter.models import User
# import mysql.connector,json
from flask import session, request

class UpdateProfileForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    picture = FileField('Profile Picture', 
                        validators=[FileAllowed(['jpg','png'])])
    gender = StringField('Gender')
    submit = SubmitField('Update')

    # To check if the username already exists
    def validate_username(self, username):
        cnx = mysql.connector.connect(host='localhost',user='root', database='recruiter')
        cur = cnx.cursor(buffered=True)
        cur.execute("select username from applicants where username=%s;",(username.data,))
        user = cur.fetchone()
        print(user,session['username'])
        if user != session['username']:
            if user:
                raise ValidationError('That username is taken. Please choose another.')
        cur.close()
        cnx.close()


class HospitalRegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=100)])
    address = StringField('Address', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    vacancy = StringField('Vacancy',
                           validators=[DataRequired(), Length(min=2, max=100)])
    total_beds = StringField('Total beds',
                           validators=[DataRequired(), Length(min=2, max=100)])
    sev1_bud = StringField('Enter cost of low severity',validators=[DataRequired()])
    sev2_bud = StringField('Enter cost of level 1 severity',validators=[DataRequired()])
    sev3_bud = StringField('Enter cost of level 2  severity',validators=[DataRequired()])
    sev4_bud = StringField('Enter cost of level 3 severity',validators=[DataRequired()])
    sev5_bud = StringField('Enter cost of high severity',validators=[DataRequired()])

    num_doc = StringField('Number of Doctors',validators=[DataRequired()])
    num_nurse = StringField('Number of Nurses',validators=[DataRequired()])
    num_equip = StringField('Number of Equipment',validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
            
    submit = SubmitField('Sign Up')

    # To check if the email already exists
    def validate_email(self, email):
        cnx = mysql.connector.connect(host='localhost',user='root', database='recruiter')
        cur = cnx.cursor(buffered=True)
        cur.execute("select email from company where email=%s",(email.data,))
        user = cur.fetchone()
        if user:
            raise ValidationError('That email is taken. Please choose another.')
        cur.close()
        cnx.close()
