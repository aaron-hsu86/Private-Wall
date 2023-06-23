from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'do not share'
bcrypt = Bcrypt(app)
schema = 'private_wall_schema'


