#Import Libraries
from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import json


# def create_app():
# 	app = Flask(__name__)
# 	app.config['MYSQL_HOST'] = 'eventila1.chlvhxtejl7u.ap-south-1.rds.amazonaws.com'
# 	app.config['MYSQL_USER'] = 'root'
# 	app.config['MYSQL_PASSWORD'] = '$pyn3230819'
# 	app.config['MYSQL_DB'] = 'eventila'
# 	app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# 	return app


def create_app():
	app = Flask(__name__)
	app.config['MYSQL_HOST'] = 'localhost'      
	app.config['MYSQL_USER'] = 'root'     
	app.config['MYSQL_PASSWORD'] = 'password'  
	app.config['MYSQL_DB'] = 'eventila'
	return app
	
app = create_app()
mysql = MySQL(app)

#Import packages
from reports.clippr import clippr
from reports.data_reports import image_data
from reports.webbr import webbr
from reports.albumm import albumm
from reports.spyne import spyne
from framesController import frames


@app.route('/reports/v3')
def reports_home():
	return render_template('index_v3.html')

@app.route('/reports/v2')
def reports_v2():
	return render_template('index_v3.html')

#Register blueprint

app.register_blueprint(clippr)
app.register_blueprint(image_data)
app.register_blueprint(webbr)
app.register_blueprint(albumm)
app.register_blueprint(spyne)
app.register_blueprint(frames)


if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000, debug=True)
