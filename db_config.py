from app import app
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy


mysql1 = MySQL()
sql = SQLAlchemy()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '$pyn3230819'
app.config['MYSQL_DATABASE_DB'] = 'eventila'
app.config['MYSQL_DATABASE_HOST'] = 'eventila1.chlvhxtejl7u.ap-south-1.rds.amazonaws.com'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:$pyn3230819@eventila1.chlvhxtejl7u.ap-south-1.rds.amazonaws.com:3306/eventila'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
mysql1.init_app(app)
sql.init_app(app)