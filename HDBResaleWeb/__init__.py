from flask import Flask

#Initialise app with secret key
app = Flask(__name__)
app.config['SECRET_KEY'] = 'e7d0eaa8168231567e93d4eea521188dbb83b37ccaf576190862a4a2c0c66d80'

#Import routes.py
from HDBResaleWeb import routes