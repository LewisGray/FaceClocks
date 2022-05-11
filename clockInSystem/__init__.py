from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = '6c51abd7b3bd5df1cf5e5cc273c012c0'
db = SQLAlchemy(app)


from clockInSystem import routes