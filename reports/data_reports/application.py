#import libraries
from flask import render_template
from app import mongo1

#bluebrint import
from reports.data_reports import image_data

#mysql import
from server import mysql




@image_data.route('/')
def reports_image_data():
    return render_template('reports_image_data.html')


@image_data.route('/category/raw')   
def data_category_monthly_report_raw():
	try:
		cursor = mysql.connection.cursor()         
		sql = "SELECT DATE_FORMAT(created_date,\'%Y-%m\') as month, category, sum(photo_num) from business_project group by category,DATE_FORMAT(created_date,\'%Y-%m\') order by DATE_FORMAT(created_date,\'%Y-%m\') desc"
		cursor.execute(sql)
		rows_monthly = cursor.fetchall()
		for j in range(0, len(rows_monthly)):  
			sql = "SELECT shoot_id from business_project where created_date LIKE '%" + str(rows_monthly[j]['month']) + "%' and category='" + str(rows_monthly[j]['category']) + "'"
			cursor.execute(sql)
			monthly_shootid = cursor.fetchall()
			photos_count_raw = int(0)
			for k in range(0, len(monthly_shootid)):
				shoot_id = monthly_shootid[k]['shoot_id']
				try:
					h1 = mongo1.db.shoot_project_photos.find_one({'shootId': shoot_id}, {'photoList':1 ,'photoLabel':1, 'category':1})
					h1 = dict(h1)
					for m in range(0, len(h1['photoList'])):
						if h1['photoList'][m]['photoLabel'] == 'raw':
							photos_count_raw = photos_count_raw +1
				except:
					continue
			rows_monthly[j]['photos_count_raw'] = photos_count_raw
		return render_template('data_category_monthly_report_raw.html', rows_monthly=rows_monthly)
	except Exception as e:
		print(e)
	finally:
		cursor.close()


@image_data.route('/category/v2/raw')   
def data_category_yearly_report_raw():
	try:
		cursor = mysql.connection.cursor()         
		sql = "SELECT YEAR(created_date) as year, category, sum(photo_num) from business_project group by category,YEAR(created_date) order by YEAR(created_date) desc"
		cursor.execute(sql)
		rows_yearly = cursor.fetchall()
		for j in range(0, len(rows_yearly)):  
			sql = "SELECT shoot_id from business_project where created_date LIKE '%" + str(rows_yearly[j]['year']) + "%' and category='" + str(rows_yearly[j]['category']) + "'"
			cursor.execute(sql)
			yearly_shootid = cursor.fetchall()
			photos_count_raw = int(0)
			for k in range(0, len(yearly_shootid)):
				shoot_id = yearly_shootid[k]['shoot_id']
				try:
					h1 = mongo1.db.shoot_project_photos.find_one({'shootId': shoot_id}, {'photoList':1 ,'photoLabel':1, 'category':1})
					h1 = dict(h1)
					for m in range(0, len(h1['photoList'])):
						if h1['photoList'][m]['photoLabel'] == 'raw':
							photos_count_raw = photos_count_raw +1
				except:
					continue
			rows_yearly[j]['photos_count_raw'] = photos_count_raw
		return render_template('data_category_yearly_report_raw.html', rows_yearly=rows_yearly)
	except Exception as e:
		print(e)
	finally:
		cursor.close()



@image_data.route('/category/edit')   
def data_category_monthly_report_edit():
	try:
		cursor = mysql.connection.cursor()         
		sql = "SELECT DATE_FORMAT(creation_date,\'%Y-%m\') as month, category_name as category, sum(sku_count) from editing_project group by category,DATE_FORMAT(creation_date,\'%Y-%m\') order by DATE_FORMAT(creation_date,\'%Y-%m\') desc"
		cursor.execute(sql)
		rows_monthly = cursor.fetchall()
		for j in range(0, len(rows_monthly)):  
			sql = "SELECT shoot_id from editing_project where creation_date LIKE '%" + str(rows_monthly[j]['month']) + "%' and category_name='" + str(rows_monthly[j]['category']) + "'"
			cursor.execute(sql)
			monthly_shootid = cursor.fetchall()
			photos_count_edit = int(0)
			for k in range(0, len(monthly_shootid)):
				shoot_id = monthly_shootid[k]['shoot_id']
				try:
					h1 = mongo1.db.shoot_project_photos.find_one({'shootId': shoot_id}, {'photoList':1 ,'photoLabel':1, 'category':1})
					h1 = dict(h1)
					for m in range(0, len(h1['photoList'])):
						if h1['photoList'][m]['photoLabel'] != 'raw':
							photos_count_edit = photos_count_edit +1
				except:
					continue
			rows_monthly[j]['photos_count_edit'] = photos_count_edit
		return render_template('data_category_monthly_report_edit.html', rows_monthly=rows_monthly)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 


@image_data.route('/category/v2/edit')   
def data_category_yearly_report_edit():
	try:
		cursor = mysql.connection.cursor()         
		sql = "SELECT YEAR(creation_date) as year, category_name as category, sum(sku_count) from editing_project group by category,YEAR(creation_date) order by YEAR(creation_date) desc"
		cursor.execute(sql)
		rows_yearly = cursor.fetchall()
		for j in range(0, len(rows_yearly)):  
			sql = "SELECT shoot_id from editing_project where creation_date LIKE '%" + str(rows_yearly[j]['year']) + "%' and category_name='" + str(rows_yearly[j]['category']) + "'"
			cursor.execute(sql)
			yearly_shootid = cursor.fetchall()
			photos_count_edit = int(0)
			for k in range(0, len(yearly_shootid)):
				shoot_id = yearly_shootid[k]['shoot_id']
				try:
					h1 = mongo1.db.shoot_project_photos.find_one({'shootId': shoot_id}, {'photoList':1 ,'photoLabel':1, 'category':1})
					h1 = dict(h1)
					for m in range(0, len(h1['photoList'])):
						if h1['photoList'][m]['photoLabel'] != 'raw':
							photos_count_edit = photos_count_edit +1
				except:
					continue
			rows_yearly[j]['photos_count_edit'] = photos_count_edit
		return render_template('data_category_yearly_report_edit.html', rows_yearly=rows_yearly)
	except Exception as e:
		print(e)
	finally:
		cursor.close()


