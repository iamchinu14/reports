from flask import render_template
import datetime
import requests
import json
from app import mongo

#bluebrint import
from reports.webbr import webbr


#mysql import
from server import mysql
from db_config import mysql1







@webbr.route('/')
def reports_webbr():
	return render_template('reportswebbr.html')


@webbr.route('/engagement')
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



@webbr.route('/all_signups')
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


@webbr.route('/time_onboard')
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


@webbr.route('/registered_vendors', methods=['GET','POST'])
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





@webbr.route('/website-registrations')
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

@webbr.route('/website-onboarding-status')
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





