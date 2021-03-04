#import libraries
from flask import render_template, Response, request
import json
#bluebrint import
from reports.clippr import clippr


#mysql import
from server import mysql


@clippr.route('/')
def reports_clippr():
	return render_template('reports_clippr.html')
    

@clippr.route('/all_requests',methods=['GET'])
def clippr_all_request():
	try:
		user_request = request.args.get('key')
		cursor = mysql.connection.cursor()
		if user_request == "Graph":  
			sql = "select DATE_FORMAT(timestamp, \'%Y-%m\') as month,count(*) as count from clippr_requests where processing_time!=0.0 group by DATE_FORMAT(timestamp, \'%Y-%m\')"
			cursor.execute(sql)
			tabledata = cursor.fetchall()  
			sql = "SELECT DATE_FORMAT(timestamp, \'%Y-%m\') as month, COUNT(DISTINCT authenticated_email_id) as count from clippr_requests where authenticated_email_id!='NULL' AND authenticated_email_id!='None' group by DATE_FORMAT(timestamp, \'%Y-%m\') order by DATE_FORMAT(timestamp, \'%Y-%m\')"
			cursor.execute(sql)
			tabledata2 = cursor.fetchall()
			rows={}
			return render_template('clippr_all_requests.html', rows=rows,tabledata=tabledata, tabledata2=tabledata2)
		else:	
			sql = "SELECT id,product_category,product_subcategory,api_log_source,user_id,free_trail_email,authenticated_email_id,timestamp,image_category,round(processing_time,2),img_resolution,img_size,img_downloaded_low_res,img_downloaded_high_res,feedback,ip_address,browser_name,location,browser_lang,input_image_url,output_image_url,otp_verified from clippr_requests ORDER BY timestamp DESC"  
			cursor.execute(sql)
			rows = cursor.fetchall()
			tabledata={}
			tabledata2={}
			return render_template('clippr_all_requests.html', rows=rows, tabledata=tabledata, tabledata2=tabledata2)
	except Exception as e:
		print(e)
	finally:
		cursor.close()





# @clippr.route('/example-graph-dyamically')
# def example_graph_dyamically():
# 	try:
# 		# user_request = request.args.get('key')
# 		# cursor = mysql.connection.cursor()
# 		# if user_request == "Graph":  
# 		# 	sql = "select DATE_FORMAT(timestamp, \'%Y-%m\') as date,count(*) as count from clippr_requests where processing_time!=0.0 group by DATE_FORMAT(timestamp, \'%Y-%m\')"
# 		# 	cursor.execute(sql)
# 		# 	tabledata = cursor.fetchall()
# 		# 	print(tabledata)
# 		# else:	
# 		# 	sql = "SELECT DATE_FORMAT(timestamp, \'%Y-%m\') as date, COUNT(DISTINCT authenticated_email_id) as count from clippr_requests where authenticated_email_id!='NULL' AND authenticated_email_id!='None' group by DATE_FORMAT(timestamp, \'%Y-%m\') order by DATE_FORMAT(timestamp, \'%Y-%m\')"
# 		# 	cursor.execute(sql)
# 		# 	tabledata = cursor.fetchall()
# 		# 	print(tabledata)
# 		return render_template('example_graph.html')
# 	except Exception as e:
# 		print(e)
# 	finally:
# 		print('hey')



# @clippr.route('/example_grap_dyamically/',methods=['GET', 'POST']) 
# def example_graph_dyamically_():
# 	if request.method == 'POST':
# 		data = request.form.get('timeZone')
# 		print(data) 
# 		return 'hey'
# 	tabledata={}
# 	return render_template('example_graph.html', tabledata=tabledata)




@clippr.route('/all_requests_time_report', methods=['GET', 'POST'])
def clippr_time_report():
	try:
		cursor = mysql.connection.cursor()
		if request.method == 'POST':
			start = request.form.get('start')
			if start=="daily(yyyy-mm-dd)":
				sql = "SELECT DATE_FORMAT(timestamp, \'%Y-%m-%d\') as date, count(*) as count from clippr_requests where processing_time!=0.0 group by DATE_FORMAT(timestamp, \'%Y-%m-%d\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="weekly(yyyy-week_no)":
				sql = "SELECT DATE_FORMAT(timestamp, \'%X-%V\') as date, count(*) as count from clippr_requests where processing_time!=0.0 group by DATE_FORMAT(timestamp, \'%X-%V\')"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			elif start=="monthly(yyyy-mm)":
				sql = "SELECT DATE_FORMAT(timestamp, \'%Y-%m\') as date, count(*) as count from clippr_requests where processing_time!=0.0 group by DATE_FORMAT(timestamp, \'%Y-%m\')" 
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
			else:
				sql = "SELECT YEAR(timestamp) as date, count(*) as count from clippr_requests where processing_time!=0.0 group by YEAR(timestamp)"
				cursor.execute(sql)
				tabledata = cursor.fetchall()
				return Response(json.dumps(tabledata),  mimetype='application/json')
		timezone = request.args.get('key')
		sql = "select count(id), round(sum(processing_time),2), round(sum(processing_time)/count(id),2) from clippr_requests where processing_time!=0.0"
		cursor.execute(sql)
		total_summary = cursor.fetchall()    
		if timezone=="Weekly":
			sql = "SELECT DATE_FORMAT(timestamp, \'%X-%V\') as date, count(id), round(sum(processing_time)/count(id),2), max(browser_name) from clippr_requests where processing_time!=0.0 group by DATE_FORMAT(timestamp, \'%X-%V\') order by DATE_FORMAT(timestamp, \'%X-%V\') desc"
			cursor.execute(sql)
			rows_weekly = cursor.fetchall()  
			return render_template('clippr_time_report.html', total_summary=total_summary, rows_weekly=rows_weekly)
		elif timezone=="Monthly":
			sql = "SELECT DATE_FORMAT(timestamp, \'%Y-%m\') as date, count(id), round(sum(processing_time)/count(id),2), max(browser_name) from clippr_requests where processing_time!=0.0 group by DATE_FORMAT(timestamp, \'%Y-%m\') order by DATE_FORMAT(timestamp, \'%Y-%m\') desc"
			cursor.execute(sql)
			rows_monthly = cursor.fetchall()
			return render_template('clippr_time_report.html', total_summary=total_summary, rows_monthly=rows_monthly)
		elif timezone=="Yearly":
			sql = "SELECT YEAR(timestamp) as date, count(id), round(sum(processing_time)/count(id),2), max(browser_name) from clippr_requests where processing_time!=0.0 group by YEAR(timestamp) order by YEAR(timestamp) desc"
			cursor.execute(sql)
			rows_yearly = cursor.fetchall()
			return render_template('clippr_time_report.html', total_summary=total_summary, rows_yearly=rows_yearly)
		else:
			sql = "SELECT DATE_FORMAT(timestamp, \'%Y-%m-%d\') as date, count(id), round(sum(processing_time)/count(id),2), max(browser_name) from clippr_requests where processing_time!=0.0 group by DATE_FORMAT(timestamp, \'%Y-%m-%d\') order by DATE_FORMAT(timestamp, \'%Y-%m-%d\') desc"
			cursor.execute(sql)
			rows_daily = cursor.fetchall()  
			return render_template('clippr_time_report.html', total_summary=total_summary, rows_daily=rows_daily)
	except Exception as e:
		print(e)
	finally:
		cursor.close()



@clippr.route('/category_report')
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


