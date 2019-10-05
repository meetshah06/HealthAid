from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '06939c4920daa98a86acb0368d51ad72'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  #'mysql://{username}:{password}@localhost/{databasename}'

db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)
# login_manager = LoginManager(app)
# Where to redirect if a route is clicked where login is required 
# login_manager.login_view = 'login'
# login_manager.login_message_category = 'info'

# To avoid forming a loop
from healthaid import routes