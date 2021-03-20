from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'e7d0eaa8168231567e93d4eea521188dbb83b37ccaf576190862a4a2c0c66d80'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

from HDBResaleWeb import routes