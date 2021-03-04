from flask import Flask
from flask_mysqldb import MySQL


def create_app():
	app = Flask(__name__)
	app.config['MYSQL_HOST'] = 'eventila1.chlvhxtejl7u.ap-south-1.rds.amazonaws.com'
	app.config['MYSQL_USER'] = 'root'
	app.config['MYSQL_PASSWORD'] = '$pyn3230819'
	app.config['MYSQL_DB'] = 'eventila'
	app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
	return app

app = create_app()

mysql = MySQL(app)