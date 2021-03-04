import pymysql
from functools import reduce
from app import app, mongo,mongo1
from bson.json_util import dumps
from bson.objectid import ObjectId
from db_config import mysql1
from flask import flash, render_template, request, redirect, jsonify, send_file, send_from_directory
import psycopg2
from framesController import frames
import json
import time
import requests
import time
import datetime
from flask import Flask, request
from flask_mysqldb import MySQL
app = Flask(__name__)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '$pyn3230819'
app.config['MYSQL_HOST'] = 'eventila1.chlvhxtejl7u.ap-south-1.rds.amazonaws.com'
app.config['MYSQL_DB'] = 'eventila'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# app.config['MYSQL_HOST'] = 'localhost'      
# app.config['MYSQL_USER'] = 'root'     
# app.config['MYSQL_PASSWORD'] = 'password'  
# app.config['MYSQL_DB'] = 'eventila'


mysql = MySQL(app)


@app.route('/reports/v3')
def reports_home():
	return render_template('index_v3.html')

@app.route('/reports/v2')
def reports_v2():
	return render_template('index_v2.html')

@app.route('/reports/clippr')
def reports_clippr():
	return render_template('reports_clippr.html')

@app.route('/reports/image-data')
def reports_image_data():
	return render_template('reports_image_data.html')

@app.route('/reports/webbr')
def reports_webbr():
	return render_template('reportswebbr.html')

@app.route('/reports/spyne')
def reports_spyne():
	return render_template('spynesummary.html')


@app.route('/reports/albumn')
def reports_albumn():
	return render_template('albumn.html')

@app.route('/reports/vendors')
def vendors():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(va.created_date, \'%Y-%m-%d - %h:%i %p\') as created_date, va.vendor_type, va.business_name, va.subdomain, va.stage, ua.email_id, va.mob_1, va.vendor_id, va.user_id from vendor_account va, user_account ua where va.user_id = ua.user_id order by va.created_date desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('vendors.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/clippr/all_requests')
def clippr_all_request():
	try:
		cursor = mysql.connection.cursor()
		sql = "SELECT id,user_id,free_trail_email,authenticated_email_id,timestamp,image_category,round(processing_time,2),img_resolution,img_size,img_downloaded_low_res,img_downloaded_high_res,feedback,ip_address,browser_name,location,browser_lang,input_image_url,output_image_url,otp_verified from clippr_requests ORDER BY timestamp DESC"  
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('clippr_all_requests.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close()


@app.route('/reports/webbr/all_signups')
def reportswebbr_all_signups():
	try:
		cursor = mysql.connection.cursor()
		sql = "SELECT va.created_date,va.business_name,va.mob_1,va.vendor_type,vr.device_type, va.user_id,va.vendor_id,va.subdomain,vr.source_url,va.area,va.email_id_1 from vendor_account va LEFT JOIN spyne_access_log vr ON va.user_id = vr.user_id where va.products_subscribed LIKE '%WEB%' AND va.email_id_1 NOT LIKE '%test%' ORDER BY va.created_date DESC"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('reportswebbr_all_signups.html',rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close()
	


@app.route('/reports/clippr/time_report')
def clippr_time_report():
	try:
		cursor = mysql.connection.cursor()
		sql = "select count(id), round(sum(processing_time),2), round(sum(processing_time)/count(id),2) from clippr_requests"
		cursor.execute(sql)
		total_summary = cursor.fetchall()  
		sql = "SELECT DATE_FORMAT(timestamp, \"%Y-%c-%d\"), count(id), round(sum(processing_time)/count(id),2), max(browser_name) from clippr_requests group by DATE_FORMAT(timestamp, \"%Y-%c-%d\");"
		cursor.execute(sql)
		rows_daily = cursor.fetchall()
		sql = "SELECT WEEK(timestamp), count(id), round(sum(processing_time)/count(id),2), max(browser_name) from clippr_requests group by WEEK(timestamp);"
		cursor.execute(sql)
		rows_weekly = cursor.fetchall()
		sql = "SELECT MONTH(timestamp), count(id), round(sum(processing_time)/count(id),2), max(browser_name) from clippr_requests group by MONTH(timestamp);"
		cursor.execute(sql)
		rows_monthly = cursor.fetchall()
		sql = "SELECT YEAR(timestamp), count(id), round(sum(processing_time)/count(id),2), max(browser_name) from clippr_requests group by YEAR(timestamp);"
		cursor.execute(sql)
		rows_yearly = cursor.fetchall()
		return render_template('clippr_time_report.html', total_summary=total_summary, rows_daily=rows_daily, rows_weekly=rows_weekly, rows_monthly=rows_monthly, rows_yearly=rows_yearly)
	except Exception as e:
		print(e)
	finally:
		cursor.close()


@app.route('/reports/image-data/category/raw')   
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


@app.route('/reports/image-data/category/v2/raw')   
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





@app.route('/reports/image-data/category/edit')   
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


@app.route('/reports/image-data/category/v2/edit')   
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



@app.route('/reports/image-data/channel')   
def data_channel_report():
	try:
		cursor = mysql.connection.cursor()   
		sql = "SELECT DATE_FORMAT(STR_TO_DATE(received_date, '%d-%m-%Y'),\'%m-%Y\') as month, channel1, sum(channel1_sku_count), sum(channel1_images_count) from data_organisation group by DATE_FORMAT(STR_TO_DATE(received_date, '%d-%m-%Y'),\'%m-%Y\'),channel1 order by DATE_FORMAT(STR_TO_DATE(received_date, '%d-%m-%Y'),\'%m-%Y\') desc"
		cursor.execute(sql)
		rows_monthly = cursor.fetchall()
		sql = "SELECT YEAR(STR_TO_DATE(received_date, '%d-%m-%Y')) as year, channel1, sum(channel1_sku_count), sum(channel1_images_count) from data_organisation group by YEAR(STR_TO_DATE(received_date, '%d-%m-%Y')),channel1 order by YEAR(STR_TO_DATE(received_date, '%d-%m-%Y')) desc"
		cursor.execute(sql)
		rows_yearly = cursor.fetchall()
		return render_template('data_channel_report.html', rows_monthly=rows_monthly, rows_yearly=rows_yearly)
	except Exception as e:
		print(e)
	finally:
		cursor.close()


@app.route('/reports/image-data/category-channel')   
def data_channel_category_report():
	try:
		cursor = mysql.connection.cursor()   
		sql = "SELECT DATE_FORMAT(STR_TO_DATE(received_date, '%d-%m-%Y'),\'%m-%Y\') as month,category, channel1, sum(channel1_sku_count), sum(channel1_images_count) from data_organisation group by DATE_FORMAT(STR_TO_DATE(received_date, '%d-%m-%Y'),\'%m-%Y\'),category,channel1 order by DATE_FORMAT(STR_TO_DATE(received_date, '%d-%m-%Y'),\'%m-%Y\') desc"
		cursor.execute(sql)
		rows_monthly = cursor.fetchall()
		sql = "SELECT YEAR(STR_TO_DATE(received_date, '%d-%m-%Y')) as year,category, channel1, sum(channel1_sku_count), sum(channel1_images_count) from data_organisation group by YEAR(STR_TO_DATE(received_date, '%d-%m-%Y')),category,channel1 order by YEAR(STR_TO_DATE(received_date, '%d-%m-%Y')) desc"
		cursor.execute(sql)
		rows_yearly = cursor.fetchall()
		return render_template('data_channel_category_report.html', rows_monthly=rows_monthly, rows_yearly=rows_yearly)
	except Exception as e:
		print(e)
	finally:
		cursor.close()




@app.route('/reports/webbr/time_onboard')
def webbr_time_report():
	try:
		cursor = mysql.connection.cursor()
		sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m-%d\') as date, COUNT(vendor_id) as total_vendors,SUM(va.ONBOARD_STATE='THEME') AS theme_selected ,SUM(va.ONBOARD_STATE='WEBSITE_BANNER') AS banner_added,SUM(va.ONBOARD_STATE='SOCIAL_PROFILES') AS social_profile_added,SUM(va.ONBOARD_STATE='COMPLETED') AS completed , (CASE WHEN vr.request_type = 'GET_WEBSITE' THEN COUNT(distinct vr.user_id) ELSE 0 END) AS website_requested FROM vendor_account va LEFT JOIN vendor_request vr ON va.user_id = vr.user_id WHERE (va.products_subscribed = 'WEB' || va.products_subscribed = 'WEB,SHARE') AND DATE_FORMAT(va.created_date, \'%Y-%m-%d\') > '2020-05-16' AND va.email_id_1 NOT LIKE '%test%'  GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\') DESC"
		cursor.execute(sql)
		rows_daily = cursor.fetchall()

		sql = "SELECT WEEK(va.created_date) as date, COUNT(vendor_id) as total_vendors,SUM(va.ONBOARD_STATE='THEME') AS theme_selected ,SUM(va.ONBOARD_STATE='WEBSITE_BANNER') AS banner_added,SUM(va.ONBOARD_STATE='SOCIAL_PROFILES') AS social_profile_added,SUM(va.ONBOARD_STATE='COMPLETED') AS completed , (CASE WHEN vr.request_type = 'GET_WEBSITE' THEN COUNT(distinct vr.user_id) ELSE 0 END) AS website_requested FROM vendor_account va LEFT JOIN vendor_request vr ON va.user_id = vr.user_id WHERE (va.products_subscribed = 'WEB' || va.products_subscribed = 'WEB,SHARE') AND va.email_id_1 NOT LIKE '%test%'  GROUP BY WEEK(va.created_date) ORDER BY WEEK(va.created_date) DESC"
		cursor.execute(sql)
		rows_weekly = cursor.fetchall()

		sql = "SELECT MONTH(va.created_date) as date, COUNT(vendor_id) as total_vendors,SUM(va.ONBOARD_STATE='THEME') AS theme_selected ,SUM(va.ONBOARD_STATE='WEBSITE_BANNER') AS banner_added,SUM(va.ONBOARD_STATE='SOCIAL_PROFILES') AS social_profile_added,SUM(va.ONBOARD_STATE='COMPLETED') AS completed , (CASE WHEN vr.request_type = 'GET_WEBSITE' THEN COUNT(distinct vr.user_id) ELSE 0 END) AS website_requested FROM vendor_account va LEFT JOIN vendor_request vr ON va.user_id = vr.user_id WHERE (va.products_subscribed = 'WEB' || va.products_subscribed = 'WEB,SHARE') AND va.email_id_1 NOT LIKE '%test%'  GROUP BY MONTH(va.created_date) ORDER BY MONTH(va.created_date) DESC"
		cursor.execute(sql)
		rows_monthly = cursor.fetchall()

		sql = "SELECT YEAR(va.created_date) as date, COUNT(vendor_id) as total_vendors,SUM(va.ONBOARD_STATE='THEME') AS theme_selected ,SUM(va.ONBOARD_STATE='WEBSITE_BANNER') AS banner_added,SUM(va.ONBOARD_STATE='SOCIAL_PROFILES') AS social_profile_added,SUM(va.ONBOARD_STATE='COMPLETED') AS completed , (CASE WHEN vr.request_type = 'GET_WEBSITE' THEN COUNT(distinct vr.user_id) ELSE 0 END) AS website_requested FROM vendor_account va LEFT JOIN vendor_request vr ON va.user_id = vr.user_id WHERE (va.products_subscribed = 'WEB' || va.products_subscribed = 'WEB,SHARE') AND va.email_id_1 NOT LIKE '%test%'  GROUP BY YEAR(va.created_date) ORDER BY YEAR(va.created_date) DESC"
		cursor.execute(sql)
		rows_yearly = cursor.fetchall()

		sql = "SELECT COUNT(vendor_id) as total_vendors, SUM(va.ONBOARD_STATE='COMPLETED') AS completed FROM vendor_account va LEFT JOIN vendor_request vr ON va.user_id = vr.user_id WHERE (va.products_subscribed = 'WEB' || va.products_subscribed = 'WEB,SHARE') AND va.email_id_1 NOT LIKE '%test%'"
		cursor.execute(sql)
		total_summary = cursor.fetchall()

		return render_template('webbr_time_report.html', total_summary=total_summary, rows_daily=rows_daily, rows_weekly=rows_weekly, rows_monthly=rows_monthly, rows_yearly=rows_yearly)
	except Exception as e:
		print(e)
	finally:
		cursor.close()

@app.route('/reports/registered_vendors', methods=['GET','POST'])
def reportswebbr_registered_vendors():


	res = requests.post('https://www.spyne.ai/shareservice/admin/status?heartbeat=ok/')
	data = res.json()
	rows = []

	subscriptionLiveCount = int(0)
	subscriptionExpireCount = int(0)
	domainLiveCount = int(0)
	domainExpireCount = int(0)

	for i in range(0, len(data)):
		dict = {}
		try:
			dict['emailId'] = data[i]['emailId']
		except:
			dict['emailId'] = 'None'
		try:
			dict['businessName'] = data[i]['businessName']
		except:
			dict['businessName'] = 'None'
		try:
			dict['businesscategory'] = data[i]['basicDetails']['serviceType']
		except:
			dict['businesscategory'] = 'None'
		try:
			s = float(data[i]['basicDetails']['registrationDate']) / 1000.0
			dict['registrationDate'] = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')[0:10]
		except:
			dict['registrationDate'] = 'None'
		try:
			s = float(data[i]['subscriptionStartDate']) / 1000.0
			dict['subscriptionStartDate'] = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')[0:10]
		except:
			dict['subscriptionStartDate'] = 'None'
		try:
			s = float(data[i]['subscriptionEndDate']) / 1000.0
			dict['subscriptionEndDate'] = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')[0:10]
			ExpectedDate = datetime.datetime.strptime(datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f'), "%Y-%m-%d %H:%M:%S.%f")
			present =  datetime.datetime.now()
			if ExpectedDate < present:
				dict['subscriptionLive'] = 'NO'
				subscriptionExpireCount = subscriptionExpireCount + 1
			else:
				dict['subscriptionLive'] = 'YES'
				subscriptionLiveCount = subscriptionLiveCount +1
		except:
			dict['subscriptionEndDate'] = 'None'
			dict['subscriptionLive'] = 'None'
		try:
			s = float(data[i]['domainCredentials']['domainExpiryDate']) / 1000.0
			dict['domainExpiryDate'] = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')[0:10]
			ExpectedDate1 = datetime.datetime.strptime(datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f'), "%Y-%m-%d %H:%M:%S.%f")
			present1 =  datetime.datetime.now()
			if ExpectedDate1 < present1:
				dict['domainLive'] = 'NO'
				domainExpireCount = domainExpireCount +1
			else:
				dict['domainLive'] = 'YES'
				domainLiveCount = domainLiveCount +1
		except:
			dict['domainExpiryDate'] = 'None'
			dict['domainLive'] = 'None'
		try:
			dict['sslStatus'] = data[i]['sslStatus']
		except:
			dict['sslStatus'] = 'None'
		rows.append(dict)
	return render_template('reportswebbr_registered_vendors.html', rows=rows, subscriptionLiveCount=subscriptionLiveCount, subscriptionExpireCount=subscriptionExpireCount, domainLiveCount=domainLiveCount, domainExpireCount=domainExpireCount)






@app.route('/reports/webbr/engagement')
def reports_webbr_engagements():
	res = requests.post('https://www.spyne.ai/shareservice/admin/status?heartbeat=ok/')
	data = res.json()
	total_registered = len(data)
	rows = []

	subscriptionLiveCount = int(0)
	subscriptionExpireCount = int(0)
	domainLiveCount = int(0)
	domainExpireCount = int(0)
	activeLoginCount = int(0)
	
	for i in range(0, len(data)):
		dict2 = {}
		try:
			s = float(data[i]['subscriptionEndDate']) / 1000.0
			dict2['subscriptionEndDate'] = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')[0:10]
			ExpectedDate = datetime.datetime.strptime(datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f'), "%Y-%m-%d %H:%M:%S.%f")
			present =  datetime.datetime.now()
			if ExpectedDate < present:
				dict2['subscriptionLive'] = 'NO'
				subscriptionExpireCount = subscriptionExpireCount + 1
			else:
				dict2['subscriptionLive'] = 'YES'
				subscriptionLiveCount = subscriptionLiveCount + 1
		except:
			dict2['subscriptionEndDate'] = 'None'
			dict2['subscriptionLive'] = 'None'

		if (dict2['subscriptionLive'] == 'YES'):
			rows.append(dict2)
		else:
			continue

		try:
			dict2['emailId'] = data[i]['emailId']
		except:
			dict2['emailId'] = 'None'
		try:
			dict2['businessName'] = data[i]['businessName']
		except:
			dict2['businessName'] = 'None'
		
		try:
			s = float(data[i]['subscriptionStartDate']) / 1000.0
			dict2['subscriptionStartDate'] = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')[0:10]
		except:
			dict2['subscriptionStartDate'] = 'None'


		user_id = data[i]['userId']
		try:
			cursor = mysql.connection.cursor()
			try:
				cursor.execute("""select login_date from session_manager where user_id=(%s) order by login_date desc LIMIT 1""",[user_id])
				rows2 = cursor.fetchall()
				dict2['last_login_date'] = rows2[0]['login_date']
				present5 =  datetime.datetime.now()
				time_between = present5 - rows2[0]['login_date']
				if time_between.days<=15:
					dict2['recently_login'] = 'YES'
					activeLoginCount = activeLoginCount + 1
				else:
					dict2['recently_login'] = 'NO'
			except:
				dict2['last_login_date'] = 'None'

			try:
				cursor.execute("""select vendor_type from vendor_account where user_id=(%s) order by created_date desc LIMIT 1""",[user_id])
				rows10 = cursor.fetchall()
				if rows10[0]['vendor_type'] == "photographer":
					dict2['businessCategory'] = 'Photography'
				else:
					dict2['businessCategory'] = rows10[0]['vendor_type']
			except:
				dict2['businessCategory'] = 'None'

			try:
				cursor = mysql.connection.cursor()
				cursor.execute("""select count(*) from hashtag_landing_page where vendor_user_id=(%s)""",[user_id])
				rows77 = cursor.fetchall()
				dict2['hashtag_landing'] = rows77[0]['count(*)']
			except:
				dict2['hashtag_landing'] = 'None'
		except:
			pass
		finally:
			cursor.close()

		try:
			h1 = mongo.db.photographer.find_one({'userId': user_id}, {'photos':1, 'videos':1 })
			h1 = dict(h1)
			try:
				photos_count_ = len(h1['photos']['gallery'])
				dict2['photos_count'] = photos_count_
			except:
				dict2['photos_count'] = 'None'
			try:
				videos_count_ = len(h1['videos'])
				dict2['videos_count'] = videos_count_
			except:
				dict2['videos_count'] = 'None'
		except:
			pass

		
		try:
			s = float(data[i]['domainCredentials']['domainExpiryDate']) / 1000.0
			dict2['domainExpiryDate'] = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')[0:10]
			ExpectedDate1 = datetime.datetime.strptime(datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f'), "%Y-%m-%d %H:%M:%S.%f")
			present1 =  datetime.datetime.now()
			if ExpectedDate1 < present1:
				dict2['domainLive'] = 'NO'
				domainExpireCount = domainExpireCount +1
			else:
				dict2['domainLive'] = 'YES'
				domainLiveCount = domainLiveCount +1
		except:
			dict2['domainExpiryDate'] = 'None'
			dict2['domainLive'] = 'None'

	return render_template('reports_webbr_engagements.html', rows=rows, activeLoginCount=activeLoginCount, total_registered=total_registered, subscriptionLiveCount=subscriptionLiveCount, subscriptionExpireCount=subscriptionExpireCount, domainLiveCount=domainLiveCount)



@app.route('/reports/clippr/category_report')
def clippr_category_report():
	try:
		cursor = mysql.connection.cursor()
		sql = "SELECT * from clippr_requests"
		cursor.execute(sql)
		rows = cursor.fetchall()
		print(rows)
		return render_template('clippr_category_report.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close()


# @app.route('/testing_index')
# def testing_index():
# 	try:
# 		start = time.time()
# 		cursor = mysql.connection.cursor()
# 		sql = "SELECT count(*) from vendor_account where vendor_type = 'photographer'"
# 		cursor.execute(sql)
# 		a = cursor.fetchall()
# 		print(a)
# 		end = time.time()
# 		print(end-start)
# 		return 'hey'
# 	except Exception as e:
# 		print(e)
# 	finally:
# 		cursor.close()





@app.route('/reports/albumn/monthly')
def albumn_monthly():
	try:
		start = time.time()
		cursor = mysql.connection.cursor()
		#new photographer
		sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m\')  ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m\') DESC"
		cursor.execute(sql)
		new_photographer = cursor.fetchall()
		#project data
		sql1 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m\') as date ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) as project_shared ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) as selection_project , COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) as distribution_project , SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m\') DESC"
		cursor.execute(sql1)
		project_data = cursor.fetchall()
		#multiple selection
		sql2 = "SELECT DATE_FORMAT(ss.date_added, '%Y-%m') as date , COUNT(DISTINCT ss.id) FROM spyne_share ss RIGHT JOIN spyne_share_users ssu ON ss.id = ssu.project_id LEFT JOIN vendor_account va ON ss.vendor_user_id = va.user_id WHERE va.vendor_type = 'photographer' AND ss.album_selection = 1 AND ssu.album_selection = 1 AND ss.speciality != 1 AND va.email_id_1 NOT LIKE '%test%' GROUP BY  DATE_FORMAT(ss.date_added, '%Y-%m') HAVING COUNT(ssu.id) > 3 ORDER BY  DATE_FORMAT(ss.date_added, '%Y-%m') DESC"
		cursor.execute(sql2)
		multiple_selection = cursor.fetchall()
		#review
		sql3 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m\') as date,COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 and ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m\') DESC"
		cursor.execute(sql3)
		review = cursor.fetchall()
		#dowanload
		sql4 = "SELECT DATE_FORMAT(sdt.created_date, \'%Y-%m\') as date , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1  AND ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sdt.created_date, \'%Y-%m\') ORDER BY DATE_FORMAT(sdt.created_date, \'%Y-%m\') DESC"
		cursor.execute(sql4)
		download = cursor.fetchall()
		#contact generated
		sql6 = "SELECT DATE_FORMAT(sc.date_added, \'%Y-%m\') as date , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id and sel.email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sc.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(sc.date_added, \'%Y-%m\') DESC"
		cursor.execute(sql6)
		contact = cursor.fetchall()
		#photo upload size
		sql3 = "SELECT DATE_FORMAT(vps.created_on, \'%Y-%m\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(vps.created_on, \'%Y-%m\') ORDER BY DATE_FORMAT(vps.created_on, \'%Y-%m\') DESC"
		cursor.execute(sql3)
		photo_size = cursor.fetchall()
		cursor.execute("SELECT DATE_FORMAT(created_date,\'%Y-%m\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%Y-%m\') ORDER BY  DATE_FORMAT(created_date,\'%Y-%m\') desc")
		lead_count = cursor.fetchall()
		end = time.time()
		print("Time taken ", end-start)
		return render_template('albumn_photographer_monthly_summary.html', list1_list2 = zip(new_photographer,project_data,multiple_selection,review,download,contact,photo_size,lead_count))
	except Exception as e:
		print(e)
	finally:
		cursor.close()


@app.route('/reports/albumn/daily')
def albumn_daily():
	try:
		cursor = mysql.connection.cursor()
		#new photographer
		start = time.time()
		sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m-%d\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.email_id_1 NOT LIKE '%test%' AND va.vendor_type = 'photographer' GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\')  ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\')  DESC"
		cursor.execute(sql)
		new_photographer = cursor.fetchall()
		#project data
		sql1 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') as date ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) as project_shared ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) as selection_project , COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) as distribution_project ,SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer'  AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') DESC"
		cursor.execute(sql1)
		project_data = cursor.fetchall()
		#multiple selection
		sql2 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') as date , COUNT(DISTINCT ss.id) FROM spyne_share ss RIGHT JOIN spyne_share_users ssu ON ss.id = ssu.project_id LEFT JOIN vendor_account va ON ss.vendor_user_id = va.user_id WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' AND ss.album_selection = 1 AND ssu.album_selection = 1 AND ss.speciality != 1 GROUP BY  DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') HAVING COUNT(ssu.id) > 3 ORDER BY  DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') DESC"
		cursor.execute(sql2)
		multiple_selection = cursor.fetchall()
		#review
		sql3 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') as date,COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 and vcr.cust_email NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') DESC"
		cursor.execute(sql3)
		review = cursor.fetchall()
		#dowanload
		sql4 = "SELECT DATE_FORMAT(sdt.created_date, \'%Y-%m-%d\') as date , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1 AND ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sdt.created_date, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(sdt.created_date, \'%Y-%m-%d\') DESC"
		cursor.execute(sql4)
		download = cursor.fetchall()
		#contact generated
		sql6 = "SELECT DATE_FORMAT(sc.date_added, \'%Y-%m-%d\') as date , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id WHERE sel.email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sc.date_added, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(sc.date_added, \'%Y-%m-%d\') DESC"
		cursor.execute(sql6)
		contact = cursor.fetchall()
		#photo upload size
		sql3 = "SELECT DATE_FORMAT(vps.created_on,\'%Y-%m-%d\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' and va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(vps.created_on,\'%Y-%m-%d\') ORDER BY DATE_FORMAT(vps.created_on, \'%Y-%m-%d\') DESC"
		cursor.execute(sql3)
		photo_size = cursor.fetchall()
		#reference lead
		cursor.execute("SELECT DATE_FORMAT(created_date,\'%Y-%m-%d\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%Y-%m-%d\') ORDER BY  DATE_FORMAT(created_date,\'%Y-%m-%d\') desc")
		lead_count = cursor.fetchall()

		return render_template('albumn_photographer_daily_summary.html', list1_list2 = zip(new_photographer,project_data,multiple_selection,review,download,contact,photo_size,lead_count))

	except Exception as e:
		print(e)
	finally:
		cursor.close()


@app.route('/reports/albumn/weekly')
def albumn_weekly():
	try:
		cursor = mysql.connection.cursor()
		#new photographer
		sql = "SELECT  DATE_FORMAT(va.created_date, \'%X-%V\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.vendor_type = 'photographer' GROUP BY DATE_FORMAT(va.created_date, \'%X-%V\')  ORDER BY DATE_FORMAT(va.created_date, \'%X-%V\')  DESC"
		cursor.execute(sql)
		new_photographer = cursor.fetchall()
		#project data
		sql1 = "SELECT DATE_FORMAT(ss.date_added, \'%X-%V\') as date ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) as project_shared ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) as selection_project , COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) as distribution_project , SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer'  AND va.email_id_1 NOT LIKE '%test%'  GROUP BY DATE_FORMAT(ss.date_added, \'%X-%V\') ORDER BY DATE_FORMAT(ss.date_added, \'%X-%V\') DESC"
		cursor.execute(sql1)
		project_data = cursor.fetchall()
		#multiple selection
		sql2 = "SELECT DATE_FORMAT(ss.date_added, \'%X-%V\') as date , COUNT(DISTINCT ss.id) FROM spyne_share ss RIGHT JOIN spyne_share_users ssu ON ss.id = ssu.project_id LEFT JOIN vendor_account va ON ss.vendor_user_id = va.user_id WHERE va.vendor_type = 'photographer' AND ss.album_selection = 1 AND ssu.album_selection = 1 AND ss.speciality != 1 AND va.email_id_1 NOT LIKE '%test%' GROUP BY  DATE_FORMAT(ss.date_added,\'%X-%V\') HAVING COUNT(ssu.id) > 3 ORDER BY  DATE_FORMAT(ss.date_added, \'%X-%V\') DESC"
		cursor.execute(sql2)
		multiple_selection = cursor.fetchall()
		#review
		sql3 = "SELECT DATE_FORMAT(ss.date_added, \'%X-%V\') as date,COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 AND vcr.cust_email NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%X-%V\') ORDER BY DATE_FORMAT(ss.date_added, \'%X-%V\') DESC"
		cursor.execute(sql3)
		review = cursor.fetchall()
		#dowanload
		sql4 = "SELECT DATE_FORMAT(sdt.created_date, \'%X-%V\') as date , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1 AND ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sdt.created_date, \'%X-%V\') ORDER BY DATE_FORMAT(sdt.created_date, \'%X-%V\') DESC"
		cursor.execute(sql4)
		download = cursor.fetchall()
		#photo upload size
		sql3 = "SELECT DATE_FORMAT(vps.created_on,\'%X-%V\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(vps.created_on,\'%X-%V\') ORDER BY DATE_FORMAT(vps.created_on, \'%X-%V\') DESC"
		cursor.execute(sql3)
		photo_size = cursor.fetchall()
		#contact generated
		sql6 = "SELECT DATE_FORMAT(sc.date_added, \'%X-%V\') as date , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id AND sel.email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sc.date_added, \'%X-%V\') ORDER BY DATE_FORMAT(sc.date_added, \'%X-%V\') DESC"
		cursor.execute(sql6)
		contact = cursor.fetchall()
		#hot leads
		cursor.execute("SELECT DATE_FORMAT(created_date,\'%X-%V\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%X-%V\') ORDER BY  DATE_FORMAT(created_date,\'%X-%V\') desc")
		lead_count = cursor.fetchall()

		return render_template('albumn_photographer_weekly_summary.html', list1_list2 = zip(new_photographer,project_data,multiple_selection,review,download,contact,photo_size,lead_count))

	except Exception as e:
		print(e)
	finally:
		cursor.close()












@app.route('/reports/hashtags')
def hashtags():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(a.created_date, \'%Y-%m-%d - %h:%i %p\') as created_date, a.name, a.added_by, v.subdomain, b.email_id, a.url_keyword, a.display_name from hashtag a, user_account b, vendor_account v where a.added_by = b.user_id and b.user_id=v.user_id order by a.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('hashtags.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/selection_summary')
def selection_summary():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select b.subdomain, count(*) as weddings, sum(a.photos_count) as photos, DATE_FORMAT(a.date_added, \'%Y-%m\') as onboard_month from vendor_project a, vendor_account b where a.active = 1 and a.vendor_user_id = b.user_id and b.subdomain not in (\'skv-photography\', \'phototest\', \'spyne3\', \'test-4\', \'spyneone\') group by b.subdomain order by count(*) desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('share_selection_summary.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/selection_summary_quarterly')
def share_vendors_quarterly():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select b.subdomain, count(*) as weddings, sum(a.photos_count) as photos, DATE_FORMAT(b.created_date, \'%Y-%m-%d\') as onboard_date from vendor_project a, vendor_account b where a.active = 1 and a.vendor_user_id = b.user_id and b.subdomain not in (\'skv-photography\', \'phototest\', \'spyne3\', \'test-4\', \'spyneone\') and (a.date_added >= NOW() - INTERVAL 90 DAY) group by b.subdomain order by count(*) desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('share_quarterly.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/selection_projects')
def selection_projects():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select b.subdomain, a.project_name, a.client_email_id, a.pin, DATE_FORMAT(a.date_added, \'%Y-%m-%d - %h:%i %p\') as date_added, DATE_FORMAT(a.updated_date, \'%Y-%m-%d\') as updated_date, a.stage, a.link_expiry_date, a.photos_count, a.min_photo_selection, a.max_photo_selection, a.client_name, a.client_whatsapp from vendor_project a, vendor_account b where a.active = 1 and a.vendor_user_id = b.user_id and b.subdomain not in (\'skv-photography\', \'phototest\', \'spyne3\', \'test-4\', \'spyneone\') order by a.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('share_selection_projects.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/distribution_projects')
def distribution_projects():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select b.subdomain, a.project_id, DATE_FORMAT(a.created_date, \'%Y-%m-%d - %h:%i %p\') as created_date, a.title, a.friend_email_id, a.friend_whatsapp, a.pin from vendor_project_friends_sharing a, vendor_account b where a.vendor_user_id = b.user_id and b.subdomain not in (\'skv-photography\', \'phototest\', \'spyne3\', \'test-4\', \'spyneone\') order by a.project_id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('share_distribution_projects.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/share_daily')
def share_daily():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(a.date_added, \'%Y-%m-%d - %h:%i %p\') as day, count(*) as projects, sum(a.photos_count) as photos_shared from vendor_project a, vendor_account b where a.active = 1 and a.vendor_user_id = b.user_id and b.subdomain not in (\'skv-photography\', \'phototest\', \'spyne3\', \'test-4\', \'spyneone\') GROUP BY DATE_FORMAT(a.date_added, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(a.date_added, \'%Y-%m-%d\') desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('share_daily.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/share_monthly')
def share_monthly():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(a.date_added, \'%Y-%m\') as month, count(*) as projects, sum(a.photos_count) as photos_shared from vendor_project a, vendor_account b where a.active = 1 and a.vendor_user_id = b.user_id and b.subdomain not in (\'skv-photography\', \'phototest\', \'spyne3\', \'test-4\', \'spyneone\') GROUP BY DATE_FORMAT(a.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(a.date_added, \'%Y-%m\') desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('share_monthly.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/themes_summary')
def themes_summary():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select d.theme_name, d.theme_title, d.description, count(*) from user_account a, vendor_account b, vendor_website_theme c, website_theme_master d where a.user_id = c.user_id and c.theme_id = d.id and c.active = 1 and a.user_id = b.user_id and b.subdomain != \'NULL\' and b.stage in (\'PROFILE_ACTIVATED\', \'EVENTILA_LIVE\') group by d.theme_name, d.theme_title, d.description order by count(*) desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('themes_summary.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/themes_vendors')
def themes_vendors():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(b.created_date, \'%Y-%m-%d - %h:%i %p\') as created_date, d.subdomain, a.email_id, c.theme_name, c.theme_title, c.description from user_account a, vendor_website_theme b, website_theme_master c, vendor_account d where a.user_id = b.user_id and b.theme_id = c.id and b.active = 1 and a.user_id = d.user_id and d.subdomain != \'NULL\' and d.stage in (\'PROFILE_ACTIVATED\', \'EVENTILA_LIVE\') order by b.created_date desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('themes_vendors.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/spyne_requests')
def spyne_requests():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(a.created_date, \'%Y-%m-%d - %h:%i %p\') as created_date, b.vendor_type, b.subdomain, a.seo, a.ssl_security, a.domain, a.mailbox, a.requested_plan, a.user_id, b.vendor_id, b.stage, a.plan_stage, b.email_id_1, b.mob_1 from spyne_request a, vendor_account b where a.user_id = b.user_id order by a.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_requests.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/reviews_vendors')
def reviews_vendors():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(a.created_date, \'%Y-%m-%d - %h:%i %p\') as created_date, a.vendor_id, b.subdomain, a.vendor_type, a.cust_name, a.project_id, a.event_name, a.event_date, a.overall_rating, a.review_text from vendor_customer_review a, vendor_account b where a.vendor_id = b.vendor_id and a.vendor_id not in (\'1510716120347\', \'1519540586224\') order by a.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('reviews_vendors.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/reviews_monthly')
def reviews_monthly():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(a.created_date, \'%Y-%m\') as month, count(*) as reviews from vendor_customer_review a, vendor_account b where a.vendor_id = b.vendor_id and a.vendor_id not in (\'1510716120347\', \'1519540586224\', \'1537890221180\', \'1538027171743\', \'1550657992037\') GROUP BY DATE_FORMAT(a.created_date, \'%Y-%m\')"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('reviews_monthly.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
 
@app.route('/reports/reviews_vendors_summary')
def reviews_vendors_summary():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select a.vendor_id, b.subdomain, a.vendor_type, ROUND(avg(a.overall_rating),2), count(a.vendor_id) from vendor_customer_review a, vendor_account b where a.vendor_id = b.vendor_id and a.vendor_id not in (\'1510716120347\', \'1519540586224\', \'1537890221180\', \'1538027171743\', \'1550657992037\') group by a.vendor_id, b.subdomain, a.vendor_type order by count(a.vendor_id) desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('reviews_vendors_summary.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

# Spyne V2 related APIs		
		
@app.route('/reports/spyne_plans')
def spyne_plans():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select plan_id, plane_name, plan_cost, share_size, plan_type, fr_photos, plan_desc, active, created_on, updated_on from spyne_vendor_plan_master"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_plans.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/spyne_subscriptions')
def spyne_subscriptions():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(subscription_date, \'%Y-%m-%d - %h:%i %p\') as subscription_date, plan_id, vendor_id, vendor_name, plan_name, plan_orig_cost, plan_discount, plan_final_cost, subscription_date, expiry_date, plan_type, plan_duration, plan_subscription_type, active, created_on, updated_on from spyne_vendor_plan_subscription order by updated_on desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_subscriptions.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/spyne_share_projects')
def spyne_shares():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select a.id as project_id, a.project_name, DATE_FORMAT(a.date_added, \'%Y-%m-%d - %h:%i %p\') as added_date, a.vendor_user_id, c.vendor_id, c.subdomain, c.email_id_1 as vendor_email, a.client_name, a.client_email_id, a.client_whatsapp, a.pin, a.stage, a.list_name,CASE WHEN a.album_selection = 1 THEN 'YES' ELSE 'NO' END  as album_selection, a.link_expiry,CASE WHEN a.privacy =1 THEN 'ON' ELSE 'OFF' END as privacy, CASE WHEN a.download = 1 THEN 'ON' ELSE 'OFF' END as download, a.photos_count, d.project_size, a.resolution, a.updated_date, CASE WHEN e.status = 1 THEN e.attempts ELSE 0 END as download_count from spyne_share a, vendor_account c, spyne_vendor_project_store d left join spyne_download_tracker e on d.project_id = e.project_id where a.id = d.project_id and a.vendor_user_id = c.user_id and c.vendor_type = 'photographer' and a.speciality != 1 group by a.id order by a.id desc"
		cursor.execute(sql)
		project_data = cursor.fetchall()
		sql1 = "SELECT sc.project_id , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id GROUP BY sc.project_id ORDER BY sc.project_id DESC"
		cursor.execute(sql1)
		contacts = cursor.fetchall()
		sql2 = "SELECT ss.id, COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 GROUP BY ss.id ORDER BY ss.id DESC"
		cursor.execute(sql2)
		review = cursor.fetchall()
		connection = psycopg2.connect(user = 'eventilla',password = 'support123',host = 'aa1mr1lv33io7i2.chlvhxtejl7u.ap-south-1.rds.amazonaws.com',port = '5432',database = 'ebdb')
		cursor = connection.cursor()
		cursor.execute("SELECT project_id, COUNT(*) as count FROM lead_master WHERE source = 'share' AND project_id <> 'NA' AND project_id <> 'NONE' GROUP BY project_id ORDER BY  project_id desc")
		lead = cursor.fetchall()
		#print(project_data)
		#print(contacts)
		#print(review)
		#print(lead)
		project_data_list = list (project_data)
		contacts_list = list(contacts)
		review_list = list(review)
		lead_list = list(lead)
		data_list = []
		for i in range (len(project_data)):
			curr = list(project_data[i])
			for j in range(len(contacts_list)):
				if(project_data[i][0] == int(contacts_list[j][0])):
					curr.append(contacts_list[j][1])
					break
				if(j == len(contacts_list)-1):
					curr.append(0)

			for j in range(len(review_list)):
				if(project_data[i][0] == int(review_list[j][0])):
					curr.append(review_list[j][1])
					break
				if(j == len(review_list)-1):
					curr.append(0)

			for j in range(len(lead_list)):
				if(project_data[i][0] == int(lead_list[j][0])):
					curr.append(lead_list[j][1])
					break
				if(j == len(lead_list)-1):
					curr.append(0)
			data_list.append(tuple(curr))
		rows = tuple(data_list)
		#print(new_data_list)
		return render_template('spyne_share_projects.html', rows = rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()
		connection.close()

@app.route('/reports/spyne_share_photographer_monthly_summary')
def spyne_shares_monthly():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		#new photographer
		sql = "SELECT  DATE_FORMAT(va.created_date, \'%Y-%m\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m\')  ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m\')  DESC"
		cursor.execute(sql)
		new_photographer = cursor.fetchall()
		#project data
		sql1 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m\') as date ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) as project_shared ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) as selection_project , COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) as distribution_project , SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m\') DESC"
		cursor.execute(sql1)
		project_data = cursor.fetchall()
		#multiple selection
		sql2 = "SELECT DATE_FORMAT(ss.date_added, '%Y-%m') as date , COUNT(DISTINCT ss.id) FROM spyne_share ss RIGHT JOIN spyne_share_users ssu ON ss.id = ssu.project_id LEFT JOIN vendor_account va ON ss.vendor_user_id = va.user_id WHERE va.vendor_type = 'photographer' AND ss.album_selection = 1 AND ssu.album_selection = 1 AND ss.speciality != 1 AND va.email_id_1 NOT LIKE '%test%' GROUP BY  DATE_FORMAT(ss.date_added, '%Y-%m') HAVING COUNT(ssu.id) > 3 ORDER BY  DATE_FORMAT(ss.date_added, '%Y-%m') DESC"
		cursor.execute(sql2)
		multiple_selection = cursor.fetchall()
		#review
		sql3 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m\') as date,COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 and ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m\') DESC"
		cursor.execute(sql3)
		review = cursor.fetchall()
		#dowanload
		sql4 = "SELECT DATE_FORMAT(sdt.created_date, \'%Y-%m\') as date , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1  AND ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sdt.created_date, \'%Y-%m\') ORDER BY DATE_FORMAT(sdt.created_date, \'%Y-%m\') DESC"
		cursor.execute(sql4)
		download = cursor.fetchall()
		#contact generated
		sql6 = "SELECT DATE_FORMAT(sc.date_added, \'%Y-%m\') as date , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id and sel.email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sc.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(sc.date_added, \'%Y-%m\') DESC"
		cursor.execute(sql6)
		contact = cursor.fetchall()
		#photo upload size
		sql3 = "SELECT DATE_FORMAT(vps.created_on, \'%Y-%m\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(vps.created_on, \'%Y-%m\') ORDER BY DATE_FORMAT(vps.created_on, \'%Y-%m\') DESC"
		cursor.execute(sql3)
		photo_size = cursor.fetchall()
		ReferenceLead = tuple(hotLeadCount())
		data = listAppenderSystemData(new_photographer,download,review,multiple_selection,project_data,contact,ReferenceLead,photo_size)
		return render_template('spyne_share_photographer_monthly_summary.html', rows = data)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

def listAppenderSystemData(new_photographer,download,review,multiple_selection,project_data,contact,ReferenceLead,photo_size):
	download_l, review_l, multiple_selection_l, project_data_l,contact_l,ReferenceLead_l,photo_size_l = 0,0,0,0,0,0,0
	new_photographer_list = []
	for i in range(len(new_photographer)):
		curr = list(new_photographer[i])
		try:            
			if(project_data[project_data_l][0]==curr[0]):
				for j in project_data[project_data_l][1:]:
					curr.append(j)
				project_data_l+=1
			else:
				curr.append(0)
		except IndexError:
			curr.append(0)

		try:       
			if(multiple_selection[multiple_selection_l][0]==curr[0]):
				for j in multiple_selection[multiple_selection_l][1:]:
					curr.append(j)
				multiple_selection_l+=1
			else:
				curr.append(0)
		except IndexError:
			curr.append(0)

		try:       
			if(photo_size[photo_size_l][0]==curr[0]):
				for j in photo_size[photo_size_l][1:]:
					curr.append(j)
				photo_size_l+=1
			else:
				curr.append(0)
		except IndexError:
			curr.append(0)
		try:            
			if(str(ReferenceLead[ReferenceLead_l][0]).strip('-01')==curr[0]):
				for j in ReferenceLead[ReferenceLead_l][1:]:
					curr.append(j)
				ReferenceLead_l+=1
			else:
				curr.append(0)
		except IndexError:
			curr.append(0)

		try:            
			if(contact[contact_l][0]==curr[0]):
				for j in contact[contact_l][1:]:
					curr.append(j)
				contact_l+=1
			else:
				curr.append(0)
		except IndexError:
			curr.append(0)

		try:
			if(download[download_l][0]==curr[0]):
				for j in download[download_l][1:]:
					curr.append(j)
				download_l+=1
			else:
				curr.append(0)
		except IndexError:
			curr.append(0)

		try:       
			if(review[review_l][0]==curr[0]):  
				for j in review[review_l][1:]:
					curr.append(j)
				review_l+=1
			else:
				curr.append(0)
		except IndexError:
			curr.append(0)

		try:
			if(curr[9] != None and curr[4] != None and curr[4] != 0):
				avg_contacts = curr[9] / curr[4]
				curr.append(round(avg_contacts,3))
			else:
				curr.append(0)
			if(curr[8] != None and curr[4] != None and curr[4] != 0):
				avg_lead = curr[8] / curr[4]
				curr.append(round(avg_lead,3))
			else:
				curr.append(0)
		except IndexError:
				curr.append(0)
		new_photographer_list.append(tuple(curr))

	new_photographer = tuple(new_photographer_list)
	return new_photographer

@app.route('/reports/spyne_share_daily_summary')
def spyne_shares_daily():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		#new photographer
		sql = "SELECT  DATE_FORMAT(va.created_date, \'%Y-%m-%d\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.email_id_1 NOT LIKE '%test%' AND va.vendor_type = 'photographer' GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\')  ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\')  DESC"
		cursor.execute(sql)
		new_photographer = cursor.fetchall()
		#project data
		sql1 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') as date ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) as project_shared ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) as selection_project , COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) as distribution_project ,SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer'  AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') DESC"
		cursor.execute(sql1)
		project_data = cursor.fetchall()
		#multiple selection
		sql2 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') as date , COUNT(DISTINCT ss.id) FROM spyne_share ss RIGHT JOIN spyne_share_users ssu ON ss.id = ssu.project_id LEFT JOIN vendor_account va ON ss.vendor_user_id = va.user_id WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' AND ss.album_selection = 1 AND ssu.album_selection = 1 AND ss.speciality != 1 GROUP BY  DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') HAVING COUNT(ssu.id) > 3 ORDER BY  DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') DESC"
		cursor.execute(sql2)
		multiple_selection = cursor.fetchall()
		#review
		sql3 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') as date,COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 and vcr.cust_email NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') DESC"
		cursor.execute(sql3)
		review = cursor.fetchall()
		#dowanload
		sql4 = "SELECT DATE_FORMAT(sdt.created_date, \'%Y-%m-%d\') as date , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1 AND ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sdt.created_date, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(sdt.created_date, \'%Y-%m-%d\') DESC"
		cursor.execute(sql4)
		download = cursor.fetchall()
		#contact generated
		sql6 = "SELECT DATE_FORMAT(sc.date_added, \'%Y-%m-%d\') as date , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id WHERE sel.email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sc.date_added, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(sc.date_added, \'%Y-%m-%d\') DESC"
		cursor.execute(sql6)
		contact = cursor.fetchall()
		#photo upload size
		sql3 = "SELECT DATE_FORMAT(vps.created_on,\'%Y-%m-%d\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' and va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(vps.created_on,\'%Y-%m-%d\') ORDER BY DATE_FORMAT(vps.created_on, \'%Y-%m-%d\') DESC"
		cursor.execute(sql3)
		photo_size = cursor.fetchall()
		#reference lead
		cursor.execute("SELECT DATE_FORMAT(created_date,\'%Y-%m-%d\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%Y-%m-%d\') ORDER BY  DATE_FORMAT(created_date,\'%Y-%m-%d\') desc")
		ReferenceLead = cursor.fetchall()
		new_photographer_list = list(new_photographer)
		new_photographer_list = list(new_photographer)
		project_data_list = list(project_data)
		multiple_selection_list = list(multiple_selection)
		ReferenceLead_list = list(ReferenceLead)
		contact_list = list(contact)
		download_list = list(download)
		review_list = list(review)
		photo_size_l = list(photo_size)
		data_list = []
		for i in range(len(new_photographer_list)):
			curr = list(new_photographer_list[i])
			for j in range(len(project_data_list)):
				if(new_photographer_list[i][0] == project_data[j][0]):
					curr.append(project_data[j][1])
					curr.append(project_data[j][2])
					curr.append(project_data[j][3])
					curr.append(project_data[j][4])
					break
				if(j == len(project_data_list)-1):
					curr.append(0)
					curr.append(0)
					curr.append(0)
					curr.append(0)

			for j in range(len(multiple_selection_list)):
				if(new_photographer_list[i][0] == multiple_selection_list[j][0]):
					curr.append(multiple_selection_list[j][1])
					break
				if(j == len(multiple_selection_list)-1):
					curr.append(0)

			for j in range(len(photo_size)):
				if(new_photographer_list[i][0] == photo_size[j][0]):
					curr.append(photo_size[j][1])
					break
				if(j == len(photo_size)-1):
					curr.append(0)

			for j in range(len(ReferenceLead_list)):
				if(new_photographer_list[i][0] == ReferenceLead_list[j][0]):
					curr.append(ReferenceLead_list[j][1])
					break
				if(j == len(ReferenceLead_list)-1):
					curr.append(0)
						
			for j in range(len(contact_list)):
				if(new_photographer_list[i][0] == contact_list[j][0]):
					curr.append(contact_list[j][1])
					break
				if(j == len(contact_list)-1):
					curr.append(0)

			for j in range(len(download_list)):
				if(new_photographer_list[i][0] == download_list[j][0]):
					curr.append(download_list[j][1])
					break
				if(j == len(download_list)-1):
					curr.append(0)

			for j in range(len(review_list)):
				if(new_photographer_list[i][0] == review_list[j][0]):
					curr.append(review_list[j][1])
					break
				if(j == len(review_list)-1):
					curr.append(0)

			if(curr[9] != None and curr[4] != None and curr[4] != 0):
				avg_contacts = curr[9] / curr[4]
				curr.append(round(avg_contacts,3))
			else:
				curr.append(0)
			if(curr[8] != None and curr[4] != None and curr[4] != 0):
				avg_lead = curr[8] / curr[4]
				curr.append(round(avg_lead,3))
			else:
				curr.append(0)
				
			data_list.append(curr)
		data = tuple(data_list)
		return render_template('spyne_share_daily_summary.html', rows = data)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
@app.route('/reports/spyne_share_weekly_summary')
def spyne_shares_weekly():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		#new photographer
		sql = "SELECT  DATE_FORMAT(va.created_date, \'%X-%V\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.vendor_type = 'photographer' GROUP BY DATE_FORMAT(va.created_date, \'%X-%V\')  ORDER BY DATE_FORMAT(va.created_date, \'%X-%V\')  DESC"
		cursor.execute(sql)
		new_photographer = cursor.fetchall()
		#project data
		sql1 = "SELECT DATE_FORMAT(ss.date_added, \'%X-%V\') as date ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) as project_shared ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) as selection_project , COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) as distribution_project , SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer'  AND va.email_id_1 NOT LIKE '%test%'  GROUP BY DATE_FORMAT(ss.date_added, \'%X-%V\') ORDER BY DATE_FORMAT(ss.date_added, \'%X-%V\') DESC"
		cursor.execute(sql1)
		project_data = cursor.fetchall()
		#multiple selection
		sql2 = "SELECT DATE_FORMAT(ss.date_added, \'%X-%V\') as date , COUNT(DISTINCT ss.id) FROM spyne_share ss RIGHT JOIN spyne_share_users ssu ON ss.id = ssu.project_id LEFT JOIN vendor_account va ON ss.vendor_user_id = va.user_id WHERE va.vendor_type = 'photographer' AND ss.album_selection = 1 AND ssu.album_selection = 1 AND ss.speciality != 1 AND va.email_id_1 NOT LIKE '%test%' GROUP BY  DATE_FORMAT(ss.date_added,\'%X-%V\') HAVING COUNT(ssu.id) > 3 ORDER BY  DATE_FORMAT(ss.date_added, \'%X-%V\') DESC"
		cursor.execute(sql2)
		multiple_selection = cursor.fetchall()
		#review
		sql3 = "SELECT DATE_FORMAT(ss.date_added, \'%X-%V\') as date,COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 AND vcr.cust_email NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%X-%V\') ORDER BY DATE_FORMAT(ss.date_added, \'%X-%V\') DESC"
		cursor.execute(sql3)
		review = cursor.fetchall()
		#dowanload
		sql4 = "SELECT DATE_FORMAT(sdt.created_date, \'%X-%V\') as date , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1 AND ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sdt.created_date, \'%X-%V\') ORDER BY DATE_FORMAT(sdt.created_date, \'%X-%V\') DESC"
		cursor.execute(sql4)
		download = cursor.fetchall()
		#photo upload size
		sql3 = "SELECT DATE_FORMAT(vps.created_on,\'%X-%V\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(vps.created_on,\'%X-%V\') ORDER BY DATE_FORMAT(vps.created_on, \'%X-%V\') DESC"
		cursor.execute(sql3)
		photo_size = cursor.fetchall()
		#contact generated
		sql6 = "SELECT DATE_FORMAT(sc.date_added, \'%X-%V\') as date , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id AND sel.email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sc.date_added, \'%X-%V\') ORDER BY DATE_FORMAT(sc.date_added, \'%X-%V\') DESC"
		cursor.execute(sql6)
		contact = cursor.fetchall()
		#hot leads
		cursor.execute("SELECT DATE_FORMAT(created_date,\'%X-%V\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%X-%V\') ORDER BY  DATE_FORMAT(created_date,\'%X-%V\') desc")
		ReferenceLead = cursor.fetchall()
		new_photographer_list = list(new_photographer)
		new_photographer_list = list(new_photographer)
		project_data_list = list(project_data)
		multiple_selection_list = list(multiple_selection)
		ReferenceLead_list = list(ReferenceLead)
		contact_list = list(contact)
		download_list = list(download)
		review_list = list(review)
		photo_size_l = list(photo_size)
		data_list = []
		for i in range(len(new_photographer_list)):
			curr = list(new_photographer_list[i])
			for j in range(len(project_data_list)):
				if(new_photographer_list[i][0] == project_data[j][0]):
					curr.append(project_data[j][1])
					curr.append(project_data[j][2])
					curr.append(project_data[j][3])
					curr.append(project_data[j][4])
					break
				if(j == len(project_data_list)-1):
					curr.append(0)
					curr.append(0)
					curr.append(0)
					curr.append(0)

			for j in range(len(multiple_selection_list)):
				if(new_photographer_list[i][0] == multiple_selection_list[j][0]):
					curr.append(multiple_selection_list[j][1])
					break
				if(j == len(multiple_selection_list)-1):
					curr.append(0)

			for j in range(len(photo_size)):
				if(new_photographer_list[i][0] == photo_size[j][0]):
					curr.append(photo_size[j][1])
					break
				if(j == len(photo_size)-1):
					curr.append(0)

			for j in range(len(ReferenceLead_list)):
				if(new_photographer_list[i][0] == ReferenceLead_list[j][0]):
					curr.append(ReferenceLead_list[j][1])
					break
				if(j == len(ReferenceLead_list)-1):
					curr.append(0)
						
			for j in range(len(contact_list)):
				if(new_photographer_list[i][0] == contact_list[j][0]):
					curr.append(contact_list[j][1])
					break
				if(j == len(contact_list)-1):
					curr.append(0)

			for j in range(len(download_list)):
				if(new_photographer_list[i][0] == download_list[j][0]):
					curr.append(download_list[j][1])
					break
				if(j == len(download_list)-1):
					curr.append(0)

			for j in range(len(review_list)):
				if(new_photographer_list[i][0] == review_list[j][0]):
					curr.append(review_list[j][1])
					break
				if(j == len(review_list)-1):
					curr.append(0)

			if(curr[9] != None and curr[4] != None and curr[4] != 0):
				avg_contacts = curr[9] / curr[4]
				curr.append(round(avg_contacts,3))
			else:
				curr.append(0)
			if(curr[8] != None and curr[4] != None and curr[4] != 0):
				avg_lead = curr[8] / curr[4]
				curr.append(round(avg_lead,3))
			else:
				curr.append(0)
				
			data_list.append(curr)
		data = tuple(data_list)
		return render_template('spyne_share_weekly_summary.html', rows = data)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
		
@app.route('/reports/spyne_share_vendor_summary')
def spyne_share_summary():
	try: 
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select a.vendor_id, b.subdomain, d.email_id as vendor_email, count(a.project_id) as projects_count, sum(a.photos_orig_count) as photos_count,sum(a.project_size) as share_size, c.plan_name from spyne_vendor_project_store a, vendor_account b, spyne_vendor_plan_subscription c,user_account d, spyne_vendor_plan_master e where a.vendor_id = b.vendor_id and b.user_id = d.user_id and c.plan_id = e.plan_id and b.vendor_id = c.vendor_id and c.active=1 and a.vendor_id not in ('1510716120347', '1570125519621', '1519540586224', '1566017111719', '1510716120347', '1548387217772', '1564323244869', '1565237116486', '1558306912601', '1550104189393') group by a.vendor_id, b.subdomain order by sum(a.project_size) desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		total_project = reduce(lambda sum, b: sum + b[3],rows, 0)
		total_photos = reduce(lambda sum, b: sum + b[4],rows, 0)
		total_size_consumed = reduce(lambda sum, b: sum + b[5],rows, 0)
		total_vendors = len(rows)
		return render_template('spyne_share_vendor_summary.html', rows=rows,total_project=total_project,total_photos=total_photos,total_size_consumed=total_size_consumed,total_vendors=total_vendors)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
		
@app.route('/reports/spyne_all_users')
def spyne_users():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(a.created_on, \'%Y-%m-%d - %h:%i %p\') as created_on, a.email_id, a.contact_no, a.isd_code, a.active, a.email_verified, a.mobile_verified, a.user_id, a.user_name, a.is_vendor, b.city, b.user_type, b.user_skill, b.user_speciality, b.user_camera, b.user_experience from user_account a, user_profile b where a.user_id = b.user_id order by a.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_all_users.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()		

@app.route('/reports/spyne_all_freelancers')
def spyne_all_freelancers():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(a.created_on, \'%Y-%m-%d - %h:%i %p\') as created_on, b.user_type,a.email_id, a.contact_no, a.user_id, c.vendor_id, c.subdomain,a.user_name, a.is_vendor, b.city,b.user_skill,b.user_speciality,b.user_camera, b.user_experience,b.user_real_estate_architecture,b.user_jewellry_accessories,b.user_ecommerce_marketplace,b.user_lifestyle_fashion,b.user_food_restaurant,b.user_portrait,b.user_travel_hospitality,b.user_weddings_events,b.user_beauty_wellness,b.user_commercial_tvc,b.user_corporate_events,b.user_maternity_baby_kids, b.user_experience, b.user_type from user_account a, user_profile b, vendor_account c where a.user_id = b.user_id and a.user_id = c.user_id and b.user_type = 'FREELANCER' order by a.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_all_freelancers.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()		

@app.route('/reports/spyne_all_businesses')
def spyne_all_businesses():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(a.created_on, \'%Y-%m-%d - %h:%i %p\') as created_on, b.user_type, a.email_id, a.contact_no, a.user_id, c.vendor_id, c.subdomain, a.user_name, a.is_vendor , sl.source_url,sl.device_type,sl.browser from  user_profile b, business_account c ,user_account a LEFT JOIN spyne_access_log sl ON a.user_id = sl.user_id where a.user_id = b.user_id and a.user_id = c.user_id and b.user_type = 'CORPORATE' and a.email_id not like '%spyne.ai%' and a.email_id not like '%test%' order by a.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_all_businesses.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()		

@app.route('/reports/spyne_all_photographers')
def spyne_all_photographers():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(user_account.created_on, \'%Y-%m-%d - %h:%i %p\') as created_on, user_account.user_name, vendor_landing_page.work_exp, vendor_landing_page.website_required, vendor_landing_page.city, user_account.email_id, user_account.contact_no, user_profile.user_speciality, vendor_landing_page.expectation_from_spyne, vendor_landing_page.photo_share_platform, user_profile.user_id, vendor_account.vendor_id, vendor_account.subdomain, user_account.is_vendor, user_profile.user_skill, user_profile.user_camera, user_profile.user_experience , sl.source_url , sl.device_type , sl.browser from user_account left join user_profile on user_account.user_id = user_profile.user_id left join vendor_account on user_account.user_id = vendor_account.user_id left join vendor_landing_page on user_account.user_id = vendor_landing_page.user_id LEFT JOIN spyne_access_log sl ON user_account.user_id = sl.user_id  where user_profile.user_type = 'NORMAL' order by user_account.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_all_photographers.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()



@app.route('/reports/spyne_valid_shoots')
def spyne_valid_shoots():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(b.created_date, \'%Y-%m-%d - %h:%i %p\') as created_date, b.project_id, b.industry, a.user_name as raised_by, a.user_id, a.email_id, c.stage, b.shoot_date, b.reporting_time, b.end_time, b.shoot_location, b.exact_address, b.contact_person_name, b.contact_person_number, b.contact_person_email, b.important_note ,b.shoot_frequency,b.product_range , b.source, b.source_url  from user_account a, business_project b, business_project_stage c where a.user_id = b.user_id and b.project_id = c.project_id and a.email_id not like '%spyne.ai%' and a.email_id not like '%test%' and b.contact_person_name not like '%test%' order by b.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_all_shoots.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
				
@app.route('/reports/spyne_all_shoots')
def spyne_all_shoots():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(b.created_date, \'%Y-%m-%d - %h:%i %p\') as created_date, b.project_id, b.industry, a.user_name as raised_by, a.user_id, a.email_id, c.stage, b.shoot_date, b.reporting_time, b.end_time, b.shoot_location, b.exact_address, b.contact_person_name, b.contact_person_number, b.contact_person_email, b.important_note ,b.shoot_frequency,b.product_range , b.source, b.source_url  from user_account a, business_project b, business_project_stage c where a.user_id = b.user_id and b.project_id = c.project_id order by b.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_all_shoots.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/spyne_assigned_shoots')
def spyne_assigned_shoots():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "select DATE_FORMAT(b.created_date, \'%Y-%m-%d - %h:%i %p\') as created_date, b.project_id, b.industry, a.user_name as raised_by, a.user_id as raised_by_user_id, a.email_id as raised_by_email, e.subdomain as assigned_to, e.email_id_1 as assigned_to_email, c.stage, b.shoot_date, b.reporting_time, b.end_time, b.shoot_location, b.exact_address, b.contact_person_name, b.contact_person_number, b.important_note from user_account a, business_project b, business_project_stage c, business_project_assign_tracker d, vendor_account e where a.user_id = b.user_id and b.project_id = c.project_id and c.project_id = d.project_id and d.user_id = e.user_id order by b.id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('spyne_assigned_shoots.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()		
		

# MongoDB reports		
		
@app.route('/photographers')
def users():
	users = mongo.db.photographer.find({}, {'vendorId':1, 'subdomain':1, '_id':0}).limit(200).sort([("$natural",-1)])
	resp = dumps(users)
	return resp
		
@app.route('/projects')
def projects():
	projects = mongo.db.vendor_project.find({}, {'vendorUserId':1, 'projectId':1, 'name':1, 'startDate':1, 'endDate':1}).limit(5).sort([("$natural",-1)])
	resp = dumps(projects)
	return resp

#@app.route('/total-users')
def totalPaidUsers():
	allJson = []
	photographer = mongo.db.photographer.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	bakery 	= mongo.db.bakery.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	beautician = mongo.db.beautician.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	caterer = mongo.db.caterer.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	choreographer = mongo.db.choreographer.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	corporate = mongo.db.corporate.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	decorator = mongo.db.decorator.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	designer = mongo.db.designer.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	event_planner  = mongo.db.event_planner.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	freelancer = mongo.db.freelancer.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	jewellery = mongo.db.jewellery.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	other = mongo.db.other.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	restaurant = mongo.db.restaurant.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	wedding_cake = mongo.db.wedding_cake.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	wedding_card  = mongo.db.wedding_card.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	wedding_gift = mongo.db.wedding_gift.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])
	wedding_planner  = mongo.db.wedding_planner.find({'featureBook.share':True},{'_id':0,'name':1,'email1':1,'phoneNo':1,'website':1,'subscribedOnPlatform':1,'type':1,'subdomain':1,'vendorId':1}).sort([("$natural",-1)])

	allJson.append(photographer)
	allJson.append(bakery)
	allJson.append(beautician)
	allJson.append(caterer)
	allJson.append(choreographer)
	allJson.append(corporate)
	allJson.append(decorator)
	allJson.append(designer)
	allJson.append(event_planner)
	allJson.append(freelancer)
	allJson.append(jewellery)
	allJson.append(other)
	allJson.append(restaurant)
	allJson.append(wedding_cake)
	allJson.append(wedding_card)
	allJson.append(wedding_gift)
	allJson.append(wedding_planner)
	return allJson
	#return render_template('total_users.html', rows=allJson)

@app.route('/reports/total-users')
def totalPaidUsersRoute():
    resp = totalPaidUsers()
    return render_template('total_users.html', rows=resp)
    		
# @app.route('/reports/project-share-hot-lead')			
# def projectShareCount():
# 		try:
# 			conn = mysql.connect()
# 			cursor = conn.cursor()
# 			sql1 = "SELECT COUNT(*) FROM vendor_project WHERE stage = 'SELECTED_BY_CLIENT' OR stage = 'SHARED_WITH_CLIENT'"
# 			cursor.execute(sql1)
# 			count1 = cursor.fetchone()[0]	
# 			sql2 = "SELECT COUNT(*) FROM spyne_share WHERE stage = 'SELECTED_BY_CLIENT' OR stage = 'SHARED_WITH_CLIENT'"
# 			cursor.execute(sql2)
# 			count2 = cursor.fetchone()[0]
# 			resp = count1 + count2
# 			users = totalPaidUsers()
# 			user_count = 0		
# 			for list in users:
# 					for item in list:
# 							user_count+=1
# 			result = 1	
# 			hotLead = hotLeadCount()
# 			avg_hot_lead = hotLead / resp
# 			share_lead_count = shareLeadCount()	
# 			avg_project_share_by_client = share_lead_count / resp
# 			sql_lead_project = "SELECT COUNT(*) FROM eventila.share_client where lead_submitted  = 1"
# 			cursor.execute(sql_lead_project)
# 			projects_by_lead = cursor.fetchone()[0]
# 			avg_hot_lead_by_lead_projects = hotLead / projects_by_lead 
# 			sql_total_project_visit = "SELECT COUNT(*) FROM eventila.share_client"
# 			cursor.execute(sql_total_project_visit)
# 			total_visit_projects = cursor.fetchone()[0]
# 			avg_projects_visit = total_visit_projects / resp
# 			return render_template('project_share_hot_lead.html',total_project = resp,project_by_pro = count1,project_by_share = count2,paid_users = user_count,average = round(result,3),hotLeadcount = hotLead,average_hot_lead = round(avg_hot_lead,3),share_lead_count = share_lead_count,avg_project_share_by_client=round(avg_project_share_by_client,3),projects_by_lead=projects_by_lead,avg_hot_lead_by_lead_projects=round(avg_hot_lead_by_lead_projects,3),total_visit_projects=total_visit_projects,avg_projects_visit=round(avg_projects_visit,3))				
# 		except Exception as e:
# 			print(e)
# 		finally:
# 			cursor.close() 
# 			conn.close()

		
def hotLeadCount():
	try:
		connection = mysql1.connect()
		cursor = connection.cursor()
		cursor.execute("SELECT DATE_FORMAT(created_date,\'%Y-%m\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%Y-%m\') ORDER BY  DATE_FORMAT(created_date,\'%Y-%m\') desc")
		data = cursor.fetchall()
		return data
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		connection.close()

def shareLeadCount():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "SELECT COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id;"
		cursor.execute(sql)
		count = cursor.fetchone()[0]
		return count
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
		

@app.route("/reports/project-share-hot-lead")
def monthlyHotProjectLead():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		#share by client
		sql = "SELECT DATE_FORMAT(date_added,\'%Y-%m\') as month,COUNT(*) as count FROM eventila.spyne_share WHERE stage = 'SELECTED_BY_CLIENT' OR stage = 'SHARED_WITH_CLIENT' GROUP BY DATE_FORMAT(date_added,\'%Y-%m\') ORDER BY DATE_FORMAT(date_added,\'%Y-%m\') desc"
		cursor.execute(sql)
		row = cursor.fetchall()
		hotLeads = hotLeadCount()
		sql_lead_project = "SELECT COUNT(*) as count,DATE_FORMAT(date_added,\'%Y-%m\') FROM eventila.share_client where lead_submitted  = 1 GROUP BY DATE_FORMAT(date_added,\'%Y-%m\') ORDER BY DATE_FORMAT(date_added,\'%Y-%m\') desc"
		cursor.execute(sql_lead_project)
		projects_by_lead = cursor.fetchall()
		month_projects = "SELECT DATE_FORMAT(date_added,\'%Y-%m\') as month,count(*) as count1 from eventila.spyne_share group by date_format(date_added,\'%Y-%m\') order by date_format(date_added,\'%Y-%m\') desc"
		cursor.execute(month_projects)
		total_monthly_projects = cursor.fetchall()
		sql_photographer_count = "SELECT date_format(created_date,\'%Y-%m\') as month,COUNT(*) FROM eventila.vendor_account where vendor_type='photographer' and created_date >= 20190901 group by date_format(created_date,\'%Y-%m\') order by date_format(created_date,\'%Y-%m\') desc"
		cursor.execute(sql_photographer_count)
		photographer_count = cursor.fetchall()
		average_project = [round(row[i][1] / photographer_count[i][1],3) for i in range(len(min(row,photographer_count)))]
		sql_dis_project = "SELECT date_format(date_added,\'%Y-%m\')as month,COUNT(*) FROM eventila.spyne_share where album_selection = 0 and stage = 'SHARED_WITH_CLIENT' group by date_format(date_added,\'%Y-%m\') order by date_format(date_added,\'%Y-%m\') desc;"
		cursor.execute(sql_dis_project)
		dis_project_count = cursor.fetchall()	
		sql_shareBy_client = "SELECT date_format(date_added,\'%Y-%m\') as month, COUNT(DISTINCT sc.email)FROM eventila.share_client as sc LEFT JOIN eventila.share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id where sc.date_added >= 20190901 group by date_format(date_added,\'%Y-%m\') order by date_format(date_added,\'%Y-%m\') desc"
		cursor.execute(sql_shareBy_client)
		shareBy_client = cursor.fetchall()	
		tup_hotlead = tuple(hotLeads)
		average_ref_lead = [round(tup_hotlead[i][1] / shareBy_client[i][1],3) for i in range(len(tuple(zip(tup_hotlead,shareBy_client))))]
		sql_paid_venodor = "SELECT DATE_FORMAT(created_on,\'%Y-%m\'),COUNT(*) FROM spyne_vendor_plan_subscription WHERE plan_id > 1 GROUP BY DATE_FORMAT(created_on,\'%Y-%m\') ORDER BY DATE_FORMAT(created_on,\'%Y-%m\') desc"
		cursor.execute(sql_paid_venodor)
		total_paid_vendor = cursor.fetchall()
		average_final_delivery = [round(dis_project_count[i][1] / photographer_count[i][1],3) for i in range(len(min(dis_project_count,photographer_count)))]
		sql_invite = "SELECT  DATE_FORMAT(date_added,\'%Y-%m\'),COUNT(*) FROM eventila.share_invite GROUP BY DATE_FORMAT(date_added,\'%Y-%m\') ORDER BY DATE_FORMAT(date_added,\'%Y-%m\') DESC"
		cursor.execute(sql_invite)
		invite_data = cursor.fetchall()
		return render_template('share_hot_lead.html',invite_data=invite_data,average_final_delivery=average_final_delivery,total_paid_vendor=total_paid_vendor,row=row,hotLeads=hotLeads,projects_by_lead=projects_by_lead,total_monthly_projects=total_monthly_projects,photographer_count=photographer_count,average_project=average_project,dis_project_count=dis_project_count,shareBy_client=shareBy_client,average_ref_lead=average_ref_lead)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route("/reports/vendor-wise-data")
def vendorWiseData():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		connection = psycopg2.connect(user = 'eventilla',password = 'support123',host = 'aa1mr1lv33io7i2.chlvhxtejl7u.ap-south-1.rds.amazonaws.com',port = '5432',database = 'ebdb')
		cursor_pos = connection.cursor()
		#vendor_data
		cursor.execute("SELECT va.subdomain,va.email_id_1,va.mob_1,sp.plan_name,DATE_FORMAT((SELECT date_added FROM eventila.spyne_share where vendor_user_id=va.user_id order by date_added desc limit 1),\'%Y-%m\')as last_project_created,DATE_FORMAT((SELECT date_added FROM eventila.spyne_share where vendor_user_id=va.user_id order by date_added asc limit 1),\'%Y-%m\')as first_project_created,DATE_FORMAT(va.created_date,\'%Y-%m\') AS reg_date,(SELECT COUNT(*) FROM spyne_share WHERE vendor_user_id=va.user_id) as total_project,(SELECT COUNT(*) FROM eventila.spyne_share where vendor_user_id= va.user_id AND album_selection = 0 ) as final_delivery, (SELECT SUM(photos_count) FROM spyne_share ss where ss.vendor_user_id = va.user_id)  as photos_count,(SELECT SUM(photos_orig_size+photos_web_size+photos_low_size) FROM spyne_vendor_project_store where vendor_id = va.vendor_id) as total_photo_size,(SELECT SUM(project_size) FROM spyne_vendor_project_store where vendor_id = va.vendor_id) as size,(SELECT COUNT(*) FROM share_invite WHERE user_id = va.user_id) as sent_invite,(SELECT COUNT(*) FROM share_invite WHERE user_id = va.user_id AND is_vendor=1 AND is_subscribed =1 AND shared_project=1) as invite_accepted,va.user_id FROM vendor_account va,spyne_vendor_plan_subscription sp , spyne_vendor_project_store st  WHERE va.vendor_id = sp.vendor_id AND va.vendor_id = st.vendor_id GROUP BY va.user_id ORDER BY total_project DESC")
		vendor_data = cursor.fetchall()
		#reference lead
		cursor_pos.execute("SELECT vendor_id,COUNT(*) as hot_lead FROM lead_master WHERE source ='share' GROUP BY vendor_id")
		reference_lead = cursor_pos.fetchall()
		#soft lead
		sql_client_login = "select vendor_account.user_id, count(distinct share_client.email) from vendor_account left join spyne_share on vendor_account.user_id = spyne_share.vendor_user_id left join share_client on spyne_share.id = share_client.project_id WHERE vendor_account.user_id IS NOT NULL and spyne_share.client_email_id != share_client.email group by vendor_account.user_id"
		cursor.execute(sql_client_login)
		client_login = cursor.fetchall()
		#review
		sql1 = "SELECT vcr.user_id, COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 GROUP BY vcr.user_id ORDER BY vcr.user_id DESC"
		cursor.execute(sql1)
		review = cursor.fetchall()
		#download
		sql2 = "SELECT ss.vendor_user_id , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1 GROUP BY ss.vendor_user_id ORDER BY ss.vendor_user_id DESC"
		cursor.execute(sql2)
		download = cursor.fetchall()
		sql3 = "SELECT user_id , CASE WHEN vendor_type = 'freelancer' THEN 'YES' ELSE 'NO' END as is_freelancer FROM vendor_account group by user_id order by user_id desc"
		cursor.execute(sql3)
		isFreelancer = cursor.fetchall()
		#invite sent
		sql3 = "SELECT user_id , COUNT(id) FROM eventila.share_invite group by user_id order by date_added"
		cursor.execute(sql3)
		invite	 = cursor.fetchall()
		data_list = []
		vendor_data_list = list(vendor_data)
		reference_lead_list = list(reference_lead)
		client_login_list = list(client_login)
		download_list = list(download)
		review_list = list(review)
		isFreelancer_list = list(isFreelancer)
		invite_list = list(invite)
		for i in range(len(vendor_data_list)):
			curr = list(vendor_data_list[i])
			for j in range(len(reference_lead_list)):
				if(vendor_data_list[i][14] == reference_lead_list[j][0]):
					curr.append(reference_lead_list[j][1])
					break
				if(j == len(reference_lead_list)-1):
					curr.append(0)


			for j in range(len(client_login_list)):
				if(vendor_data_list[i][14] == client_login_list[j][0]):
					curr.append(client_login_list[j][1])
					break
				if(j == len(client_login_list)-1):
					curr.append(0)

			for j in range(len(download_list)):
				if(vendor_data_list[i][14] == download_list[j][0]):
					curr.append(download_list[j][1])
					break
				if(j == len(download_list)-1):
					curr.append(0)

			for j in range(len(review_list)):
				if(vendor_data_list[i][14] == review_list[j][0]):
					curr.append(review_list[j][1])
					break
				if(j == len(review_list)-1):
					curr.append(0)

			for j in range(len(isFreelancer_list)):
				if(vendor_data_list[i][14] == isFreelancer_list[j][0]):
					curr.append(isFreelancer_list[j][1])
					break
				if(j == len(isFreelancer_list)-1):
					curr.append('NULL')

			for j in range(len(invite_list)):
				if(vendor_data_list[i][14] == invite_list[j][0]):
					curr.append(invite_list[j][1])
					break
				if(j == len(invite_list)-1):
					curr.append(0)
			data_list.append(curr)
		data = tuple(data_list)
		return render_template('vendor_wise_data.html', data = data)
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		cursor_pos.close() 
		conn.close()
		connection.close()

@app.route('/reports/capturing_wow_report')
def capturing_wow_data():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "SELECT vp.user_id,va.vendor_id,vp.name, vp.email_id, vp.mobile_number,va.subdomain,va.vendor_type, vp.city ,vp.work_exp,vp.expectation_from_spyne,vp.photo_share_platform, CASE WHEN vp.website_required = 1 THEN 'YES' ELSE 'NO' END AS website_requirement,DATE_FORMAT(vp.created_date, \'%Y-%m-%d\') as date FROM spyne_vendor_plan_subscription vps , vendor_landing_page vp LEFT JOIN vendor_account va ON vp.user_id = va.user_id WHERE va.vendor_id = vps.vendor_id AND DATE_FORMAT(vp.created_date, \'%Y-%m-%d\') >= '2020-04-05' AND vps.plan_id = 14 ORDER BY DATE_FORMAT(vp.created_date, \'%Y-%m-%d\') DESC"											
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('capturing_wow_data.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()


@app.route('/reports/website-onboarding-status')
def website_onboarding_status():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m-%d\') as date, COUNT(vendor_id) as total_vendors,SUM(va.ONBOARD_STATE='THEME') AS theme_selected ,SUM(va.ONBOARD_STATE='WEBSITE_BANNER') AS banner_added,SUM(va.ONBOARD_STATE='SOCIAL_PROFILES') AS social_profile_added,SUM(va.ONBOARD_STATE='COMPLETED') AS completed , (CASE WHEN vr.request_type = 'GET_WEBSITE' THEN COUNT(distinct vr.user_id) ELSE 0 END) AS website_requested FROM vendor_account va LEFT JOIN vendor_request vr ON va.user_id = vr.user_id WHERE (va.products_subscribed = 'WEB' || va.products_subscribed = 'WEB,SHARE') AND DATE_FORMAT(va.created_date, \'%Y-%m-%d\') > '2020-05-16' AND va.email_id_1 NOT LIKE '%test%'  GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\') DESC"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('website_onboarding_status.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/website-registrations')
def websiteVendors():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "SELECT vr.request_type AS website_request,vpt.created_date AS reg_date,CASE  WHEN vpt.product_stage = 'COMPLETED' THEN vpt.updated_date ELSE null END AS onboarding_completion_date,va.vendor_type,va.business_name ,va.subdomain, vpt.product_stage AS onboard_stage, va.email_id_1, va.mob_1, va.vendor_id,va.user_id ,vpt.product_type as products_subscribed, sl.source_url , sl.device_type ,sl.browser,vp.existing_website,vp.platform,vp.reason_for_website, vp.duration,vp.why_spyne FROM vendor_products_tracker vpt INNER JOIN vendor_account va ON va.user_id=vpt.user_id LEFT JOIN vendor_web_landing_page vp ON vp.user_id = vpt.user_id LEFT JOIN spyne_access_log sl ON vpt.user_id = sl.user_id LEFT JOIN vendor_request vr ON vr.user_id = va.user_id WHERE product_type='WEB' ORDER BY vpt.created_date desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('vendors_website.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/share-onboarding-status')
def share_onboarding_status():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "SELECT DATE_FORMAT(vpt.created_date, '%Y-%m-%d') as reg_date,COUNT(vpt.user_id) as total_vendors,SUM(product_stage='SHARE_TIPS') AS on_share_tips,SUM(product_stage='SHARE_PROJECT_NAME') AS on_share_project_name,SUM(product_stage='SHARE_COMPLETED') AS on_share_completed from vendor_products_tracker vpt LEFT JOIN vendor_account va ON va.user_id = vpt.user_id where product_type='SHARE' AND va.email_id_1 NOT LIKE '%test%'  GROUP BY DATE_FORMAT(vpt.created_date, '%Y-%m-%d') ORDER BY DATE_FORMAT(vpt.created_date, '%Y-%m-%d') DESC"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('share_onboarding_status.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()


@app.route('/reports/albumm-app-signups')
def albummAppSignups():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "SELECT created_at, vendor_name, vendor_email, vendor_phone from albumm_app_lead where vendor_email not like '%test%' order by id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('albumm_app_signups.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/reports/share-registrations')
def shareVendors():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		sql = "SELECT vpt.created_date AS reg_date,CASE  WHEN vpt.product_stage = 'SHARE_COMPLETED' THEN vpt.updated_date ELSE null END AS onboarding_completion_date,va.vendor_type,va.business_name ,va.subdomain, vpt.product_stage AS onboard_stage, va.email_id_1, va.mob_1, va.vendor_id,va.user_id ,vpt.product_type as products_subscribed,sl.source_url , sl.device_type ,sl.browser,vl.city,vl.work_exp,vl.expectation_from_spyne,vl.photo_share_platform,CASE when vl.website_required='1' then 'Yes' ELSE 'No' END AS website_required FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%'  order by va.created_date DESC"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('share_vendors.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()


@app.route('/reports/sales/')
def reportsales():
	return render_template('/mysalesapp/build/index.html')

@app.route('/reports/sales/static/<path:path>')
def serveStaticFiles(path):
	path = 'templates/mysalesapp/build/static/' + path
	return send_file(path)

@app.route('/spyneweb/get_all/')
def getAllEmployees():
	try:
		conn = mysql1.connect()
		cur = conn.cursor()
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
		conn = mysql1.connect()
		cur = conn.cursor()
		cur.execute("""DELETE FROM sales_lead_tracker WHERE id=(%s)""",[id])
		mysql1.connection.commit()
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
		conn = mysql1.connect()
		cur = conn.cursor()
		cur.execute("""INSERT INTO sales_lead_tracker(user_name, user_email, date, ls_assigned_count, ls_to_pick_count, ls_demo_scheduled_count, ls_demo_done_count, ls_followup_count, ls_unreachable_count, ls_dead_count, ls_won_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (var1, var2, var3, var4, var5, var6, var7, var8, var9, var10, var11))
		mysql1.connection.commit()
		cur.execute("""INSERT INTO sales_agent(email_id, user_name) SELECT (%s),(%s) WHERE NOT EXISTS (SELECT * FROM sales_agent WHERE email_id = (%s))""", [var2, var1, var2])
		mysql1.connection.commit()
		cur.close()
		return 'hey'
	except Exception as e:
		print(e)


# @app.route('/example_grasp_dyamically/',methods=['GET', 'POST']) 
# def example_graph_dyaamically_(): 
# 	data1 = request.form.get('email')
# 	data2 = request.form.get('name')
# 	print(data1)
# 	print(data2)
# 	return 'hey'


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
		conn = mysql1.connect()
		cur = conn.cursor()
		cur.execute("""update sales_lead_tracker set user_name=(%s),user_email=(%s), date=(%s), ls_assigned_count=(%s), ls_to_pick_count=(%s), ls_demo_scheduled_count=(%s), ls_demo_done_count=(%s), ls_followup_count=(%s), ls_unreachable_count=(%s), ls_dead_count=(%s), ls_won_count=(%s) where id=(%s)""",[var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12])
		mysql1.connection.commit()
		cur.close()
		return 'hey'

	except Exception as e:
		print(e)


# Register Frames Blueprint
app.register_blueprint(frames)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)   #Here change   
