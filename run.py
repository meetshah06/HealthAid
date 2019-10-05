from healthaid import app
from healthaid import db
from flask_migrate import Migrate

migrate=Migrate(app,db)

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
