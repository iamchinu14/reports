import json
from app import app, mongo
from bson.json_util import dumps
from db_config import mysql
from flask import flash, render_template, request, redirect, jsonify
from flask import Flask, request, Blueprint


from flask_mysqldb import MySQL
app = Flask(__name__)
mysql = MySQL(app)

sales = Blueprint('sales', __name__, url_prefix='/reports/sales/', template_folder='template')


app.config['MYSQL_HOST'] = 'localhost'      
app.config['MYSQL_USER'] = 'root'          
app.config['MYSQL_PASSWORD'] = 'arun'       
app.config['MYSQL_DB'] = 'flaskapp'  


@app.route('/spyneweb/get_all/')
def getAllEmployees():
	try:
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM sales_lead_tracker")
		rows = cur.fetchall()

		rows = list(rows)
		for i in range(0, len(rows)):
			rows[i] = list(rows[i])
		cur.close()
		lis=[]
		
		for i in range(0, len(rows)):
			dict={}
			dict["id"] = rows[i][0]
			dict["fullName"] = rows[i][2]
			dict["email"] = rows[i][1]
			dict["LeadsAssigned"] = rows[i][5]
			dict["yettopick"] = rows[i][6]
			dict["demoscheduled"] = rows[i][7]
			dict["demodone"] = rows[i][8]
			dict["followup"] = rows[i][9]
			dict["notreachable"] = rows[i][10]
			dict["dead"] = rows[i][11]
			dict["won"] = rows[i][12]
			dict["hireDate"] = rows[i][4]
			lis.append(dict)

 
		return json.dumps(lis, indent=4, sort_keys=False, default=str)


	except Exception as e:
		print(e)


@app.route('/spyneweb/deletion/<int:id>')
def deleteEmployee(id):
	id = int(id)
	try:
		cur = mysql.connection.cursor()
		cur.execute("""DELETE FROM sales_lead_tracker WHERE id=(%s)""",[id])
		mysql.connection.commit()
		cur.close()
		return 'hey'
	except Exception as e:
		print(e)


@app.route('/spyneweb/insertion/', methods=['POST'])   #insertEmployee
def insertEmployee():
	dict1={}
	dict1 = request.json
	var1 = dict1['fullName']
	var2 = dict1['email']
	var3 = dict1['hireDate'][0:10]
	var4 = dict1['LeadsAssigned']
	var5 = dict1['yettopick']
	var6 = dict1['demoscheduled']
	var7 = dict1['demodone']
	var8 = dict1['followup']
	var9 = dict1['notreachable']
	var10 = dict1['dead']
	var11 = dict1['won']
	try:
		cur = mysql.connection.cursor()
		cur.execute("""INSERT INTO sales_lead_tracker(user_name, user_email, date, ls_assigned_count, ls_to_pick_count, ls_demo_scheduled_count, ls_demo_done_count, ls_followup_count, ls_unreachable_count, ls_dead_count, ls_won_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (var1, var2, var3, var4, var5, var6, var7, var8, var9, var10, var11))
		mysql.connection.commit()
		cur.execute("""INSERT INTO sales_agent(email_id, user_name) SELECT (%s),(%s) WHERE NOT EXISTS (SELECT * FROM sales_agent WHERE email_id = (%s))""", [var2, var1, var2])
		mysql.connection.commit()
		cur.close()
		return 'hey'
	except Exception as e:
		print(e)


@app.route('/spyneweb/updatation/', methods=['POST'])  
def updateEmployee():
	dict1={}
	dict1 = request.json
	var1 = dict1['fullName']
	var2 = dict1['email']
	var3 = dict1['hireDate'][0:10]
	var4 = dict1['LeadsAssigned']
	var5 = dict1['yettopick']
	var6 = dict1['demoscheduled']
	var7 = dict1['demodone']
	var8 = dict1['followup']
	var9 = dict1['notreachable']
	var10 = dict1['dead']
	var11 = dict1['won']
	var12 = dict1['id']
	try:
		cur = mysql.connection.cursor()
		cur.execute("""update sales_lead_tracker set user_name=(%s),user_email=(%s), date=(%s), ls_assigned_count=(%s), ls_to_pick_count=(%s), ls_demo_scheduled_count=(%s), ls_demo_done_count=(%s), ls_followup_count=(%s), ls_unreachable_count=(%s), ls_dead_count=(%s), ls_won_count=(%s) where id=(%s)""",[var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12])
		mysql.connection.commit()
		cur.close()
		return 'hey'

	except Exception as e:
		print(e)


if __name__ == '__main__':
	app.run()


