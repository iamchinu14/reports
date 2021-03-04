#Import libraries
from flask import render_template, request, Response
from app import mongo
import time
import json

#bluebrint import
from reports.albumm import albumm

#mysql import
from server import mysql
from db_config import mysql1

@albumm.route('/')
def reports_albumn():
	return render_template('albumn.html')


@albumm.route('/monthly')
def albumn_monthly():
	try:
		cursor = mysql.connection.cursor()
		#new photographer
		# start1 = time.time()
		sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE 'test%' AND va.products_subscribed like '%SHARE%' GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m\') ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m\') DESC"
		cursor.execute(sql)
		new_photographer = cursor.fetchall()
		# print('hey')
		# start2 =  time.time()
		# print("new_photographer ",start2-start1)
		#project data
		sql1 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m\') as date ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) as project_shared ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) as selection_project , COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) as distribution_project , SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE 'test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m\') DESC"
		cursor.execute(sql1)
		project_data = cursor.fetchall()
		# start3 = time.time()
		# print("project data", start3-start2)
		#multiple selection
		sql2 = "SELECT DATE_FORMAT(ss.date_added, '%Y-%m') as date , COUNT(DISTINCT ss.id) FROM spyne_share ss RIGHT JOIN spyne_share_users ssu ON ss.id = ssu.project_id LEFT JOIN vendor_account va ON ss.vendor_user_id = va.user_id WHERE va.vendor_type = 'photographer' AND ss.album_selection = 1 AND ssu.album_selection = 1 AND ss.speciality != 1 AND va.email_id_1 NOT LIKE 'test%' GROUP BY  DATE_FORMAT(ss.date_added, '%Y-%m') HAVING COUNT(ssu.id) > 3 ORDER BY  DATE_FORMAT(ss.date_added, '%Y-%m') DESC"
		cursor.execute(sql2)
		multiple_selection = cursor.fetchall()
		# start4 = time.time()
		# print("multiple selection ", start4-start3)
		#review
		sql3 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m\') as date,COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 and ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m\') DESC"
		cursor.execute(sql3)
		review = cursor.fetchall()
		# start5 = time.time()
		# print("review ", start5-start4)
		#dowanload
		sql4 = "SELECT DATE_FORMAT(sdt.created_date, \'%Y-%m\') as date , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1  AND ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sdt.created_date, \'%Y-%m\') ORDER BY DATE_FORMAT(sdt.created_date, \'%Y-%m\') DESC"
		cursor.execute(sql4)
		download = cursor.fetchall()
		# start6 = time.time()
		# print("download ", start6-start5)
		#contact generated
		# sql6 = "SELECT DATE_FORMAT(sc.date_added, \'%Y-%m\') as date , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id and sel.email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sc.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(sc.date_added, \'%Y-%m\') DESC"
		# cursor.execute(sql6)
		# contact = cursor.fetchall()
		# start7 = time.time()
		# print("contact ", start7-start6)
		#photo upload size
		sql3 = "SELECT DATE_FORMAT(vps.created_on, \'%Y-%m\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE 'test%' GROUP BY DATE_FORMAT(vps.created_on, \'%Y-%m\') ORDER BY DATE_FORMAT(vps.created_on, \'%Y-%m\') DESC"
		cursor.execute(sql3)
		photo_size = cursor.fetchall()
		# start8 = time.time()
		# print("photo_size ", start8-start6)
		cursor.execute("SELECT DATE_FORMAT(created_date,\'%Y-%m\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%Y-%m\') ORDER BY  DATE_FORMAT(created_date,\'%Y-%m\') desc")
		lead_count = cursor.fetchall()
		# end = time.time()
		# print("lead count", end-start8)
		return render_template('albumn_photographer_monthly_summary.html', list1_list2 = zip(new_photographer,project_data,multiple_selection,review,download,photo_size,lead_count))
	except Exception as e:
		print(e)
	finally:
		cursor.close()

@albumm.route("/vendor-project-delete-summary")
def albumm_vendor_project_delete_summary():
	try:
		cursor = mysql.connection.cursor()
		sql = "select ua.user_name,ua.email_id,spdt.user_id,spdt.project_id,spdt.project_size,spdt.project_created_date,spdt.deleted_date,spdt.photo_count FROM share_project_delete_tracker spdt LEFT JOIN user_account ua ON spdt.user_id = ua.user_id"
		cursor.execute(sql)
		rows = cursor.fetchall()
		return render_template('vendor_project_delete_summary.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close()






@albumm.route('/daily')
def albumn_daily():
	try:
		cursor = mysql.connection.cursor()
		#new photographer		
		sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m-%d\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.email_id_1 NOT LIKE 'test%' AND va.vendor_type = 'photographer' AND va.products_subscribed like '%SHARE%' GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\')  ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\')  DESC"
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
		# sql6 = "SELECT DATE_FORMAT(sc.date_added, \'%Y-%m-%d\') as date , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id WHERE sel.email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sc.date_added, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(sc.date_added, \'%Y-%m-%d\') DESC"
		# cursor.execute(sql6)
		# contact = cursor.fetchall()
		#photo upload size
		sql3 = "SELECT DATE_FORMAT(vps.created_on,\'%Y-%m-%d\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' and va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(vps.created_on,\'%Y-%m-%d\') ORDER BY DATE_FORMAT(vps.created_on, \'%Y-%m-%d\') DESC"
		cursor.execute(sql3)
		photo_size = cursor.fetchall()
		#reference lead
		cursor.execute("SELECT DATE_FORMAT(created_date,\'%Y-%m-%d\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%Y-%m-%d\') ORDER BY  DATE_FORMAT(created_date,\'%Y-%m-%d\') desc")
		lead_count = cursor.fetchall()
		return render_template('albumn_photographer_daily_summary.html', list1_list2 = zip(new_photographer,project_data,multiple_selection,review,download,photo_size,lead_count))
	except Exception as e:
		print(e)
	finally:
		cursor.close()




@albumm.route('/weekly')
def albumn_weekly():
	try:
		cursor = mysql.connection.cursor()
		#new photographer
		sql = "SELECT  DATE_FORMAT(va.created_date, \'%X-%V\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.vendor_type = 'photographer' AND va.products_subscribed like '%SHARE%' GROUP BY DATE_FORMAT(va.created_date, \'%X-%V\')  ORDER BY DATE_FORMAT(va.created_date, \'%X-%V\')  DESC"
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
		# sql6 = "SELECT DATE_FORMAT(sc.date_added, \'%X-%V\') as date , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id AND sel.email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sc.date_added, \'%X-%V\') ORDER BY DATE_FORMAT(sc.date_added, \'%X-%V\') DESC"
		# cursor.execute(sql6)
		# contact = cursor.fetchall()
		#hot leads
		cursor.execute("SELECT DATE_FORMAT(created_date,\'%X-%V\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%X-%V\') ORDER BY  DATE_FORMAT(created_date,\'%X-%V\') desc")
		lead_count = cursor.fetchall()
		return render_template('albumn_photographer_weekly_summary.html', list1_list2 = zip(new_photographer,project_data,multiple_selection,review,download,photo_size,lead_count))
	except Exception as e:
		print(e)
	finally:
		cursor.close()


@albumm.route('/share-registrations')
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


@albumm.route('/albumm-signups-count-time-report',methods=['GET', 'POST'])
def albumm_signups_count_time_report():
	try:
		cursor = mysql.connection.cursor()
		if request.method == 'POST':
			start = request.form.get('start')
			if start=="daily(yyyy-mm-dd)":
				sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m-%d\') as date,count(*) as count FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%' group by DATE_FORMAT(va.created_date, \'%Y-%m-%d\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="weekly(yyyy-week_no)":
				sql = "SELECT DATE_FORMAT(va.created_date, \'%X-%V\') as date,count(*) as count FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%' group by DATE_FORMAT(va.created_date, \'%X-%V\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="monthly(yyyy-mm)":
				sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m\') as date,count(*) as count FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%' group by DATE_FORMAT(va.created_date, \'%Y-%m\')" 
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			else:
				sql = "SELECT YEAR(va.created_date) as date,count(*) as count FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%' group by YEAR(va.created_date)"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
		timezone = request.args.get('key')
		sql = "SELECT count(*) FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%'"
		cursor.execute(sql)
		total_summary = cursor.fetchall()
		if timezone=="Weekly":
			sql = "SELECT DATE_FORMAT(va.created_date, \'%X-%V\') as week,count(*) FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%' group by DATE_FORMAT(va.created_date, \'%X-%V\') order by DATE_FORMAT(va.created_date, \'%X-%V\') DESC"
			cursor.execute(sql)
			rows_weekly = cursor.fetchall()
			return render_template('albumm_signups_count_time_report_with_graph.html', total_summary=total_summary, rows_weekly=rows_weekly)
		elif timezone=="Monthly":
			sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m\') as month,count(*) FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%' group by DATE_FORMAT(va.created_date, \'%Y-%m\') order by DATE_FORMAT(va.created_date, \'%Y-%m\') DESC"
			cursor.execute(sql)
			rows_monthly = cursor.fetchall()
			return render_template('albumm_signups_count_time_report_with_graph.html', total_summary=total_summary, rows_monthly=rows_monthly)
		elif timezone=="Yearly":
			sql = "SELECT YEAR(va.created_date) as year,count(*) FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%' group by YEAR(va.created_date) order by YEAR(va.created_date) DESC"
			cursor.execute(sql)
			rows_yearly = cursor.fetchall()
			return render_template('albumm_signups_count_time_report_with_graph.html', total_summary=total_summary, rows_yearly=rows_yearly)
		else:
			sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m-%d\') as date,count(*) FROM vendor_products_tracker AS vpt INNER JOIN vendor_account  as va ON va.user_id = vpt.user_id INNER JOIN spyne_access_log AS sl ON sl.user_id = vpt.user_id INNER JOIN vendor_landing_page AS vl ON vl.user_id = vpt.user_id  WHERE vpt.product_type ='SHARE' and va.email_id_1 NOT LIKE '%test%' and va.business_name NOT LIKE '%test%' group by DATE_FORMAT(va.created_date, \'%Y-%m-%d\') order by DATE_FORMAT(va.created_date, \'%Y-%m-%d\') DESC"
			cursor.execute(sql)
			rows_daily = cursor.fetchall()
			return render_template('albumm_signups_count_time_report_with_graph.html', total_summary=total_summary, rows_daily=rows_daily)
	except Exception as e:
		print(e)
	finally:
		cursor.close()


@albumm.route("/vendor-project-delete-by-time",methods=['GET','POST'])
def albumm_vendor_project_delete_by_time():
	try:
		cursor = mysql.connection.cursor()
		if request.method == 'POST':
			start = request.form.get('start')
			if start=="daily(yyyy-mm-dd)":
				sql = "select DATE_FORMAT(deleted_date, \'%Y-%m-%d\') as date,CAST(count(*) AS CHAR) as count,CAST(sum(project_size) AS CHAR) as project_size,CAST(sum(photo_count) AS CHAR) as photos_count FROM share_project_delete_tracker group by DATE_FORMAT(deleted_date, \'%Y-%m-%d\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="weekly(yyyy-week_no)":
				sql = "select DATE_FORMAT(deleted_date, \'%X-%V\') as date,CAST(count(*) AS CHAR) as count,CAST(sum(project_size) AS CHAR) as project_size,CAST(sum(photo_count) AS CHAR) as photos_count FROM share_project_delete_tracker group by DATE_FORMAT(deleted_date, \'%X-%V\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="monthly(yyyy-mm)":
				sql = "select DATE_FORMAT(deleted_date, \'%Y-%m\') as date,CAST(count(*) AS CHAR) as count,CAST(sum(project_size) AS CHAR) as project_size,CAST(sum(photo_count) AS CHAR) as photos_count FROM share_project_delete_tracker group by DATE_FORMAT(deleted_date, \'%Y-%m\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			else:
				sql = "select year(deleted_date) as date,CAST(count(*) AS CHAR) as count,CAST(sum(project_size) AS CHAR) as project_size,CAST(sum(photo_count) AS CHAR) as photos_count FROM share_project_delete_tracker group by year(deleted_date)"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
		timezone = request.args.get('key')
		sql = "select count(*) as total FROM share_project_delete_tracker"
		cursor.execute(sql)
		total_summary = cursor.fetchall()
		if timezone=="Weekly":
			sql = "select DATE_FORMAT(deleted_date, \'%X-%V\') as week,count(*),sum(project_size),sum(photo_count) FROM share_project_delete_tracker group by DATE_FORMAT(deleted_date, \'%X-%V\') order by DATE_FORMAT(deleted_date, \'%X-%V\') desc"
			cursor.execute(sql)
			rows_weekly = cursor.fetchall()
			return render_template('vendor_project_delete_by_time_with_graph.html', total_summary=total_summary, rows_weekly=rows_weekly)
		elif timezone=="Monthly":
			sql = "select DATE_FORMAT(deleted_date, \'%Y-%m\') as month,count(*),sum(project_size),sum(photo_count) FROM share_project_delete_tracker group by DATE_FORMAT(deleted_date, \'%Y-%m\') order by DATE_FORMAT(deleted_date, \'%Y-%m\') desc"
			cursor.execute(sql)
			rows_monthly = cursor.fetchall()
			return render_template('vendor_project_delete_by_time_with_graph.html', total_summary=total_summary, rows_monthly=rows_monthly)
		elif timezone=="Yearly":
			sql = "select year(deleted_date) as year,count(*),sum(project_size),sum(photo_count) FROM share_project_delete_tracker group by year(deleted_date) order by year(deleted_date) desc"
			cursor.execute(sql)
			rows_yearly = cursor.fetchall()
			return render_template('vendor_project_delete_by_time_with_graph.html', total_summary=total_summary, rows_yearly=rows_yearly)
		else:
			sql = "select DATE_FORMAT(deleted_date, \'%Y-%m-%d\') as date,count(*),sum(project_size),sum(photo_count) FROM share_project_delete_tracker group by DATE_FORMAT(deleted_date, \'%Y-%m-%d\') order by DATE_FORMAT(deleted_date, \'%Y-%m-%d\') desc"
			cursor.execute(sql)
			rows_daily = cursor.fetchall()
			return render_template('vendor_project_delete_by_time_with_graph.html', total_summary=total_summary, rows_daily=rows_daily)
	except Exception as e:
		print(e)
	finally:
		cursor.close()




@albumm.route("/albumm-reports-by-time", methods=['GET', 'POST'])
def albumm_all_reports_by_time():
	try:
		cursor = mysql.connection.cursor()
		if request.method == 'POST':
			start = request.form.get('start')
			if start=="daily(yyyy-mm-dd)":
				sql ="SELECT DATE_FORMAT(ss.date_added, \'%Y-%m-%d\') as date ,CAST(COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) AS CHAR) as project_shared ,CAST(COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) AS CHAR) as selection_project , CAST(COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) AS CHAR) as distribution_project , CAST(SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) AS CHAR) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer'  AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m-%d\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="weekly(yyyy-week_no)":
				sql ="SELECT DATE_FORMAT(ss.date_added, \'%X-%V\') as date ,CAST(COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) AS CHAR) as project_shared ,CAST(COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) AS CHAR) as selection_project , CAST(COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) AS CHAR) as distribution_project , CAST(SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) AS CHAR) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer'  AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%X-%V\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			else:
				sql ="SELECT DATE_FORMAT(ss.date_added, \'%Y-%m\') as date ,CAST(COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) AS CHAR) as project_shared ,CAST(COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) AS CHAR) as selection_project , CAST(COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) AS CHAR) as distribution_project , CAST(SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) AS CHAR) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer'  AND va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
		timezone = request.args.get('key')
		if timezone=="Weekly":
			#new photographer
			sql = "SELECT  DATE_FORMAT(va.created_date, \'%X-%V\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.vendor_type = 'photographer' AND va.products_subscribed like '%SHARE%' GROUP BY DATE_FORMAT(va.created_date, \'%X-%V\')  ORDER BY DATE_FORMAT(va.created_date, \'%X-%V\')  DESC"
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
			#lead count
			cursor.execute("SELECT DATE_FORMAT(created_date,\'%X-%V\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%X-%V\') ORDER BY  DATE_FORMAT(created_date,\'%X-%V\') desc")
			lead_count = cursor.fetchal()
			return render_template('albumn_photographer_time_summary.html')
			#return render_template('albumn_photographer_time_summary.html', list1_list2_weekly = zip(new_photographer,project_data,multiple_selection,review,download,photo_size,lead_count))
		elif timezone=="Monthly":
			#new photographer
			sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE 'test%' AND va.products_subscribed like '%SHARE%' GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m\') ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m\') DESC"
			cursor.execute(sql)
			new_photographer = cursor.fetchall()
			#project data
			sql1 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m\') as date ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND speciality = 0 THEN ss.id END) as project_shared ,COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 1 AND speciality = 0 THEN ss.id END) as selection_project , COUNT(CASE WHEN (ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT') AND ss.album_selection = 0 AND speciality = 0 THEN ss.id END) as distribution_project , SUM(CASE WHEN ss.stage = 'SHARED_WITH_CLIENT' OR ss.stage = 'SELECTED_BY_CLIENT' THEN ss.photos_count END) as photo_shared FROM spyne_share ss,vendor_account va WHERE va.user_id = ss.vendor_user_id AND va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE 'test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m\') DESC"
			cursor.execute(sql1)
			project_data = cursor.fetchall()
			#multiple selection
			sql2 = "SELECT DATE_FORMAT(ss.date_added, '%Y-%m') as date , COUNT(DISTINCT ss.id) FROM spyne_share ss RIGHT JOIN spyne_share_users ssu ON ss.id = ssu.project_id LEFT JOIN vendor_account va ON ss.vendor_user_id = va.user_id WHERE va.vendor_type = 'photographer' AND ss.album_selection = 1 AND ssu.album_selection = 1 AND ss.speciality != 1 AND va.email_id_1 NOT LIKE 'test%' GROUP BY  DATE_FORMAT(ss.date_added, '%Y-%m') HAVING COUNT(ssu.id) > 3 ORDER BY  DATE_FORMAT(ss.date_added, '%Y-%m') DESC"
			cursor.execute(sql2)
			multiple_selection = cursor.fetchall()
			#review
			sql3 = "SELECT DATE_FORMAT(ss.date_added, \'%Y-%m\') as date,COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 and ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(ss.date_added, \'%Y-%m\') ORDER BY DATE_FORMAT(ss.date_added, \'%Y-%m\') DESC"
			cursor.execute(sql3)
			review = cursor.fetchall()
			#download
			sql4 = "SELECT DATE_FORMAT(sdt.created_date, \'%Y-%m\') as date , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1  AND ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sdt.created_date, \'%Y-%m\') ORDER BY DATE_FORMAT(sdt.created_date, \'%Y-%m\') DESC"
			cursor.execute(sql4)
			download = cursor.fetchall()
			#photo upload size
			sql3 = "SELECT DATE_FORMAT(vps.created_on, \'%Y-%m\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' AND va.email_id_1 NOT LIKE 'test%' GROUP BY DATE_FORMAT(vps.created_on, \'%Y-%m\') ORDER BY DATE_FORMAT(vps.created_on, \'%Y-%m\') DESC"
			cursor.execute(sql3)
			photo_size = cursor.fetchall()
			#lead count
			cursor.execute("SELECT DATE_FORMAT(created_date,\'%Y-%m\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%Y-%m\') ORDER BY  DATE_FORMAT(created_date,\'%Y-%m\') desc")
			lead_count = cursor.fetchall()
			return render_template('albumn_photographer_time_summary.html', list1_list2_monthly = zip(new_photographer,project_data,multiple_selection,review,download,photo_size,lead_count))
		else:
			#new photographer		
			sql = "SELECT DATE_FORMAT(va.created_date, \'%Y-%m-%d\') as date ,COUNT(va.id) as new_photographer FROM vendor_account va  WHERE va.email_id_1 NOT LIKE 'test%' AND va.vendor_type = 'photographer' AND va.products_subscribed like '%SHARE%' GROUP BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\')  ORDER BY DATE_FORMAT(va.created_date, \'%Y-%m-%d\')  DESC"
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
			#download
			sql4 = "SELECT DATE_FORMAT(sdt.created_date, \'%Y-%m-%d\') as date , COUNT(sdt.attempts) AS download_count FROM spyne_download_tracker sdt LEFT JOIN spyne_share ss ON ss.id=sdt.project_id where sdt.status=1 AND ss.client_email_id NOT LIKE '%test%' GROUP BY DATE_FORMAT(sdt.created_date, \'%Y-%m-%d\') ORDER BY DATE_FORMAT(sdt.created_date, \'%Y-%m-%d\') DESC"
			cursor.execute(sql4)
			download = cursor.fetchall()
			#photo upload size
			sql3 = "SELECT DATE_FORMAT(vps.created_on,\'%Y-%m-%d\') , SUM(vps.project_size) FROM vendor_account va RIGHT JOIN spyne_vendor_project_store vps ON va.vendor_id = vps.vendor_id WHERE va.vendor_type = 'photographer' and va.email_id_1 NOT LIKE '%test%' GROUP BY DATE_FORMAT(vps.created_on,\'%Y-%m-%d\') ORDER BY DATE_FORMAT(vps.created_on, \'%Y-%m-%d\') DESC"
			cursor.execute(sql3)
			photo_size = cursor.fetchall()
			#reference lead
			cursor.execute("SELECT DATE_FORMAT(created_date,\'%Y-%m-%d\'), COUNT(*) as count FROM lead_detail WHERE lead_source = 'share' GROUP BY DATE_FORMAT(created_date,\'%Y-%m-%d\') ORDER BY  DATE_FORMAT(created_date,\'%Y-%m-%d\') desc")
			lead_count = cursor.fetchall()
			return render_template('albumn_photographer_time_summary.html')
			#return render_template('albumn_photographer_time_summary.html', list1_list2_daily = zip(new_photographer,project_data,multiple_selection,review,download,photo_size,lead_count))
	except Exception as e:
		print(e)
	finally:
		cursor.close()


@albumm.route('/albumm-app-signups-count-time-report',methods=['GET', 'POST'])
def albumm_app_signups_count_time_report():
	try:
		cursor = mysql.connection.cursor()
		if request.method == 'POST':
			start = request.form.get('start')
			if start=="daily(yyyy-mm-dd)":
				sql = "select DATE_FORMAT(created_at, \'%Y-%m-%d\') as date, count(*) as count from albumm_app_lead where vendor_email not like '%test%' group by DATE_FORMAT(created_at, \'%Y-%m-%d\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="weekly(yyyy-week_no)":
				sql = "select DATE_FORMAT(created_at, \'%X-%V\') as date, count(*) as count from albumm_app_lead where vendor_email not like '%test%' group by DATE_FORMAT(created_at, \'%X-%V\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="monthly(yyyy-mm)":
				sql = "select DATE_FORMAT(created_at, \'%Y-%m\') as date, count(*) as count from albumm_app_lead where vendor_email not like '%test%' group by DATE_FORMAT(created_at, \'%Y-%m\')" 
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			else:
				sql = "select YEAR(created_at) as date, count(*) as count from albumm_app_lead where vendor_email not like '%test%' group by YEAR(created_at)"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
		timezone = request.args.get('key')
		sql = "select count(*) from albumm_app_lead where vendor_email not like '%test%'"
		cursor.execute(sql)
		total_summary = cursor.fetchall() 
		if timezone=="Weekly":
			sql = "select DATE_FORMAT(created_at, \'%X-%V\') as week, count(*) from albumm_app_lead where vendor_email not like '%test%' group by DATE_FORMAT(created_at, \'%X-%V\') order by DATE_FORMAT(created_at, \'%X-%V\') desc"
			cursor.execute(sql)
			rows_weekly = cursor.fetchall()
			return render_template('albumm_app_signups_count_time_report.html', total_summary=total_summary, rows_weekly=rows_weekly)
		elif timezone=="Monthly":
			sql = "select DATE_FORMAT(created_at, \'%Y-%m\') as month, count(*) from albumm_app_lead where vendor_email not like '%test%' group by DATE_FORMAT(created_at, \'%Y-%m\') order by DATE_FORMAT(created_at, \'%Y-%m\') desc"
			cursor.execute(sql)
			rows_monthly = cursor.fetchall()
			return render_template('albumm_app_signups_count_time_report.html', total_summary=total_summary, rows_monthly=rows_monthly)
		elif timezone=="Yearly":
			sql = "select YEAR(created_at) as year, count(*) from albumm_app_lead where vendor_email not like '%test%' group by YEAR(created_at) order by YEAR(created_at) desc"
			cursor.execute(sql)
			rows_yearly = cursor.fetchall()
			return render_template('albumm_app_signups_count_time_report.html', total_summary=total_summary, rows_yearly=rows_yearly)
		else:
			sql = "select DATE_FORMAT(created_at, \'%Y-%m-%d\') as date, count(*) from albumm_app_lead where vendor_email not like '%test%' group by DATE_FORMAT(created_at, \'%Y-%m-%d\') order by DATE_FORMAT(created_at, \'%Y-%m-%d\') desc"
			cursor.execute(sql)
			rows_daily = cursor.fetchall()
			return render_template('albumm_app_signups_count_time_report.html', total_summary=total_summary, rows_daily=rows_daily)
	except Exception as e:
		print(e)
	finally:
		cursor.close()



@albumm.route('/albumm-app-signups')
def albummAppSignups():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()    
		sql = "SELECT created_at, vendor_name, skip as Interested, vendor_email, vendor_phone, source from albumm_app_lead where vendor_email not like '%test%' and vendor_name not like '%test%' and vendor_email not like '%spyne.ai%' order by id desc"
		cursor.execute(sql)
		rows = cursor.fetchall()
		print(rows[0])
		return render_template('albumm_app_signups.html', rows=rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()



@albumm.route('/share-onboarding-status')
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





@albumm.route('/spyne_share_projects')
def spyne_shares():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		start1 = time.time()
		sql = "select a.id as project_id, a.project_name, DATE_FORMAT(a.date_added, \'%Y-%m-%d - %h:%i %p\') as added_date, a.vendor_user_id, c.vendor_id, c.subdomain, c.email_id_1 as vendor_email, a.client_name, a.client_email_id, a.client_whatsapp, a.pin, a.stage, a.list_name,CASE WHEN a.album_selection = 1 THEN 'YES' ELSE 'NO' END  as album_selection, a.link_expiry,CASE WHEN a.privacy =1 THEN 'ON' ELSE 'OFF' END as privacy, CASE WHEN a.download = 1 THEN 'ON' ELSE 'OFF' END as download, a.photos_count, d.project_size, a.resolution, a.updated_date, CASE WHEN e.status = 1 THEN e.attempts ELSE 0 END as download_count from spyne_share a, vendor_account c, spyne_vendor_project_store d left join spyne_download_tracker e on d.project_id = e.project_id where a.id = d.project_id and a.vendor_user_id = c.user_id and c.vendor_type = 'photographer' and a.speciality != 1 group by a.id order by a.id desc"
		cursor.execute(sql)
		project_data = cursor.fetchall()
		start2 = time.time()
		print("project data ", start2-start1)
		sql1 = "SELECT sc.project_id , COUNT(DISTINCT sc.email)FROM share_client as sc LEFT JOIN share_email_list as sel ON sc.email != sel.email_id AND sc.project_id = sel.project_id GROUP BY sc.project_id ORDER BY sc.project_id DESC"
		cursor.execute(sql1)
		contacts = cursor.fetchall()
		start3 = time.time()
		print("contacts ",start3-start2)
		sql2 = "SELECT ss.id, COUNT(vcr.overall_rating) AS total_reviews FROM vendor_customer_review vcr LEFT JOIN spyne_share ss ON vcr.project_id=ss.id WHERE ss.speciality!=1 GROUP BY ss.id ORDER BY ss.id DESC"
		cursor.execute(sql2)
		review = cursor.fetchall()
		start4 = time.time()
		print("review ",start4-start3)
		project_data_list = list (project_data)
		contacts_list = list(contacts)
		review_list = list(review)
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
			data_list.append(tuple(curr))
		rows = tuple(data_list)
		return render_template('spyne_share_projects.html', rows = rows)
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()




@albumm.route("/vendor-wise-data")
def vendorWiseData():
	try:
		cursor = mysql.connection.cursor()
		cursor.execute("select va.subdomain,va.email_id_1,va.mob_1,va.vendor_type,va.stage,va.photo_count,va.event_count,va.thumbnail_status,va.city,va.vendor_url,va.fb_url,va.domain_expiry_date,va.onboard_state,va.products_subscribed from vendor_account va order by created_date desc")
		vendor_data = cursor.fetchall()
		return render_template('vendor_wise_data.html', vendor_data=vendor_data)
	except Exception as e:
		print(e)
	finally:
		cursor.close()


@albumm.route("/vendor-wise-data-raw")
def vendorWiseDataRaw():
	try:
		conn = mysql1.connect()
		cursor = conn.cursor()
		# connection = psycopg2.connect(user = 'eventilla',password = 'support123',host = 'aa1mr1lv33io7i2.chlvhxtejl7u.ap-south-1.rds.amazonaws.com',port = '5432',database = 'ebdb')
		# cursor_pos = connection.cursor()
		#vendor_data
		start = time.time()
		cursor.execute("SELECT va.subdomain,va.email_id_1,va.mob_1,sp.plan_name,DATE_FORMAT((SELECT date_added FROM eventila.spyne_share where vendor_user_id=va.user_id order by date_added desc limit 1),\'%Y-%m\')as last_project_created,DATE_FORMAT((SELECT date_added FROM eventila.spyne_share where vendor_user_id=va.user_id order by date_added asc limit 1),\'%Y-%m\')as first_project_created,DATE_FORMAT(va.created_date,\'%Y-%m\') AS reg_date,(SELECT COUNT(*) FROM spyne_share WHERE vendor_user_id=va.user_id) as total_project,(SELECT COUNT(*) FROM eventila.spyne_share where vendor_user_id= va.user_id AND album_selection = 0 ) as final_delivery, (SELECT SUM(photos_count) FROM spyne_share ss where ss.vendor_user_id = va.user_id)  as photos_count,(SELECT SUM(photos_orig_size+photos_web_size+photos_low_size) FROM spyne_vendor_project_store where vendor_id = va.vendor_id) as total_photo_size,(SELECT SUM(project_size) FROM spyne_vendor_project_store where vendor_id = va.vendor_id) as size,(SELECT COUNT(*) FROM share_invite WHERE user_id = va.user_id) as sent_invite,(SELECT COUNT(*) FROM share_invite WHERE user_id = va.user_id AND is_vendor=1 AND is_subscribed =1 AND shared_project=1) as invite_accepted,va.user_id FROM vendor_account va,spyne_vendor_plan_subscription sp , spyne_vendor_project_store st  WHERE va.vendor_id = sp.vendor_id AND va.vendor_id = st.vendor_id GROUP BY va.user_id ORDER BY total_project DESC")
		vendor_data = cursor.fetchall()
		end=time.time()
		print(end-start)
		#reference lead
		# cursor_pos.execute("SELECT vendor_id,COUNT(*) as hot_lead FROM lead_master WHERE source ='share' GROUP BY vendor_id")
		# reference_lead = cursor_pos.fetchall()
		#soft lead
		
		sql_client_login = "select vendor_account.user_id, count(distinct share_client.email) from vendor_account left join spyne_share on vendor_account.user_id = spyne_share.vendor_user_id left join share_client on spyne_share.id = share_client.project_id WHERE vendor_account.user_id IS NOT NULL and spyne_share.client_email_id != share_client.email group by vendor_account.user_id"
		cursor.execute(sql_client_login)
		client_login = cursor.fetchall()
		end = time.time()

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
		# vendor_data_list = list(vendor_data)
		# reference_lead_list = list(reference_lead)
		client_login_list = list(client_login)
		download_list = list(download)
		review_list = list(review)
		isFreelancer_list = list(isFreelancer)
		invite_list = list(invite)
		for i in range(len(vendor_data_list)):
			curr = list(vendor_data_list[i])


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
		print(data[0])
		return render_template('vendor_wise_data.html')
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()






