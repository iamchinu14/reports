#import libraries
from flask import render_template, request, Response
import json
import urllib
#bluebrint import
from reports.spyne import spyne


#mysql import
from server import mysql
from db_config import mysql1


@spyne.route('/')
def reports_spyne():
	return render_template('spynesummary.html')

@spyne.route('/spyne_all_freelancers')
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


@spyne.route('/spyne_all_photographers')
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



@spyne.route('/spyne_all_businesses')
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



@spyne.route('/vendors')
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



@spyne.route('/business-signups-time-report',methods=['GET','POST'])
def spynebusiness_signups_time_report():
	try:
		cursor = mysql.connection.cursor()
		if request.method == 'POST':
			start = request.form.get('start')
			if start=="daily(yyyy-mm-dd)":
				sql = "SELECT DATE_FORMAT(created_on, \'%Y-%m-%d\') as date, CAST(COUNT(id) AS CHAR) as count from user_account where email_id not like '%spyne.ai%' and email_id not like '%test%' GROUP BY DATE_FORMAT(created_on, \'%Y-%m-%d\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="weekly(yyyy-week_no)":
				sql = "SELECT DATE_FORMAT(created_on, \'%X-%V\') as date, CAST(COUNT(id) AS CHAR) as count from user_account where email_id not like '%spyne.ai%' and email_id not like '%test%' GROUP BY DATE_FORMAT(created_on, \'%X-%V\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="monthly(yyyy-mm)":
				sql = "SELECT DATE_FORMAT(created_on, \'%Y-%m\') as date, CAST(COUNT(id) AS CHAR) as count from user_account where email_id not like '%spyne.ai%' and email_id not like '%test%' GROUP BY DATE_FORMAT(created_on, \'%Y-%m\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			else:
				sql = "SELECT YEAR(created_on) as date, CAST(COUNT(id) AS CHAR) as count from user_account where email_id not like '%spyne.ai%' and email_id not like '%test%' GROUP BY YEAR(created_on)"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')

		timezone = request.args.get('key')
		sql = "select count(id) from user_account where email_id not like '%spyne.ai%' and email_id not like '%test%'"
		cursor.execute(sql)
		total_summary = cursor.fetchall()
		if timezone=="Weekly":
			sql = "SELECT DATE_FORMAT(created_on, \'%X-%V\') as week, COUNT(id) from user_account where email_id not like '%spyne.ai%' and email_id not like '%test%' GROUP BY DATE_FORMAT(created_on, \'%X-%V\') ORDER BY DATE_FORMAT(created_on, \'%X-%V\') DESC"
			cursor.execute(sql)
			rows_weekly = cursor.fetchall()
			return render_template('spyne_business_signups_time_count_graph.html', total_summary=total_summary, rows_weekly=rows_weekly)
		elif timezone=="Monthly":
			sql = "SELECT DATE_FORMAT(created_on, \'%Y-%m\') as month, COUNT(id) from user_account where email_id not like '%spyne.ai%' and email_id not like '%test%' GROUP BY DATE_FORMAT(created_on, \'%Y-%m\') ORDER BY DATE_FORMAT(created_on, \'%Y-%m\') DESC"
			cursor.execute(sql)
			rows_monthly = cursor.fetchall()
			return render_template('spyne_business_signups_time_count_graph.html', total_summary=total_summary, rows_monthly=rows_monthly)
		elif timezone=="Yearly":
			sql = "SELECT YEAR(created_on) as year, COUNT(id) from user_account where email_id not like '%spyne.ai%' and email_id not like '%test%' GROUP BY YEAR(created_on) ORDER BY YEAR(created_on) DESC"
			cursor.execute(sql)
			rows_yearly = cursor.fetchall()
			return render_template('spyne_business_signups_time_count_graph.html', total_summary=total_summary, rows_yearly=rows_yearly)
		else:
			sql = "SELECT DATE_FORMAT(created_on, \'%Y-%m-%d\') as date, COUNT(id) from user_account where email_id not like '%spyne.ai%' and email_id not like '%test%' GROUP BY DATE_FORMAT(created_on, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(created_on, \'%Y-%m-%d\') DESC"
			cursor.execute(sql)
			rows_daily = cursor.fetchall()
			return render_template('spyne_business_signups_time_count_graph.html', total_summary=total_summary, rows_daily=rows_daily)
	except Exception as e:
		print(e)
	finally:
		cursor.close()



@spyne.route('/shoot-request-time-report',methods=['GET','POST'])
def shoot_request_time_report():
	try:
		cursor = mysql.connection.cursor()
		if request.method == 'POST':
			start = request.form.get('start')
			if start=="daily(yyyy-mm-dd)":
				sql = "SELECT DATE_FORMAT(created_date, \'%Y-%m-%d\') as date, CAST(COUNT(id) AS CHAR) as count from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%' GROUP BY DATE_FORMAT(created_date, \'%Y-%m-%d\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="weekly(yyyy-week_no)":
				sql = "SELECT DATE_FORMAT(created_date, \'%X-%V\') as date, CAST(COUNT(id) AS CHAR) as count from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%' GROUP BY DATE_FORMAT(created_date, \'%X-%V\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="monthly(yyyy-mm)":
				sql = "SELECT DATE_FORMAT(created_date, \'%Y-%m\') as date, CAST(COUNT(id) AS CHAR) as count from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%' GROUP BY DATE_FORMAT(created_date, \'%Y-%m\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			else:
				sql = "SELECT YEAR(created_date) as date, CAST(COUNT(id) AS CHAR) as count from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%' GROUP BY YEAR(created_date)"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')

		timezone = request.args.get('key')
		sql = "select count(id) from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%'"
		cursor.execute(sql)
		total_summary = cursor.fetchall()    
		if timezone=="Weekly":
			sql = "SELECT DATE_FORMAT(created_date, \'%X-%V\') as week, COUNT(id) from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%' GROUP BY DATE_FORMAT(created_date, \'%X-%V\') ORDER BY DATE_FORMAT(created_date, \'%X-%V\') DESC"
			cursor.execute(sql)
			rows_weekly = cursor.fetchall()
			return render_template('shoot-request-time-report-graph.html', total_summary=total_summary, rows_weekly=rows_weekly)
		elif timezone=="Monthly":
			sql = "SELECT DATE_FORMAT(created_date, \'%Y-%m\') as month, COUNT(id) from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%' GROUP BY DATE_FORMAT(created_date, \'%Y-%m\') ORDER BY DATE_FORMAT(created_date, \'%Y-%m\') DESC"
			cursor.execute(sql)
			rows_monthly = cursor.fetchall()
			return render_template('shoot-request-time-report-graph.html', total_summary=total_summary, rows_monthly=rows_monthly)
		elif timezone=="Yearly":
			sql = "SELECT YEAR(created_date) as year, COUNT(id) from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%' GROUP BY YEAR(created_date) ORDER BY YEAR(created_date) DESC"
			cursor.execute(sql)
			rows_yearly = cursor.fetchall()
			return render_template('shoot-request-time-report-graph.html', total_summary=total_summary, rows_yearly=rows_yearly)
		else:
			sql = "SELECT DATE_FORMAT(created_date, \'%Y-%m-%d\') as date, COUNT(id) from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%' GROUP BY DATE_FORMAT(created_date, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(created_date, \'%Y-%m-%d\') DESC"
			cursor.execute(sql)
			rows_daily = cursor.fetchall()
			return render_template('shoot-request-time-report-graph.html', total_summary=total_summary, rows_daily=rows_daily)
	except Exception as e:
		print(e)
	finally:
		cursor.close()




@spyne.route('/shoot-request-category-report')
def shoot_request_category_report():
	try:
		cursor = mysql.connection.cursor()
		sql = "select category,count(id) from business_project where contact_person_email not like '%test%' and contact_person_name not like '%ABS%' group by category"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('shoot_request_category_report.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close()




@spyne.route('/spyne_valid_shoots')
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
				
@spyne.route('/spyne_all_shoots')
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


@spyne.route('/spyne_assigned_shoots')
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
