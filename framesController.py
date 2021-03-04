from flask import Blueprint, render_template, jsonify
from models.Frames import FramesLandingPage as FLP, AccessLogs as AL, VendorAccount as VA, Projects, ProjectVideos, ProjectsShared
from db_config import sql as db
from app import mongo
from datetime import datetime, date

frames = Blueprint('frames', __name__, url_prefix='/reports/frames', template_folder='template')
FRAMES_START_DATE = datetime(2020, 6, 22)

@frames.route('')
def framesReports():
	return render_template('frames/frames_index.html')

@frames.route('/registrations')
def frames_landing_page():
    all_users = db.session.query(FLP, AL, VA.vendorId, VA.vendorType)\
        .outerjoin(VA, FLP.userId == VA.userId)\
        .outerjoin(AL, FLP.userId == AL.userId)\
        .order_by(FLP.updatedAt.desc())

    return render_template('frames/frames_reg.html', rows = all_users)

@frames.route('/daily-reports')
def frames_daily_reports():

    new_registrations = db.session.query(db.func.count(FLP.id), FLP.createdAt)\
        .group_by(db.func.extract('day', FLP.createdAt))\
        .order_by(FLP.createdAt.desc())\
        .all()

    projects_shared = db.session.query(db.func.count(ProjectsShared.id), ProjectsShared.createdAt)\
        .group_by(db.func.extract('day',ProjectsShared.createdAt))\
        .order_by(ProjectsShared.createdAt.desc())\
        .all()
        #.filter(db.func.extract('day',ProjectsShared.createdAt) >= 22)\
        
    videos_in_review = db.session.query(db.func.count(ProjectVideos.id), ProjectVideos.updatedAt)\
        .group_by(db.func.extract('day', ProjectVideos.updatedAt))\
        .filter_by(approved = False)\
        .order_by(ProjectVideos.updatedAt.desc())\
        .all()
        #.filter(db.func.extract('day',ProjectVideos.createdAt) >= 22)\
        
    videos_approved = db.session.query(db.func.count(ProjectVideos.id), ProjectVideos.updatedAt)\
        .group_by(db.func.extract('day', ProjectVideos.updatedAt))\
        .filter_by(approved = True)\
        .order_by(ProjectVideos.updatedAt.desc())\
        .all()
        #.filter(db.func.extract('day',ProjectVideos.createdAt) >= 22)\
        
    size_uploaded = db.session.query(db.func.sum(ProjectVideos.size).label('size'), ProjectVideos.createdAt)\
        .group_by(db.func.extract('day',ProjectVideos.createdAt))\
        .order_by(ProjectVideos.createdAt.desc())\
        .all()
        #.filter(db.func.extract('day', ProjectVideos.createdAt) >= 22)\
    # videos = []
    # for i in range(len(videos_in_review)):
    #     tup = list((videos_in_review[i][0], videos_in_review[i][1]))
    #     if len(videos_approved) > i:
    #         tup.append(videos_approved[i][0])
    #     else:
    #         tup.append(0)
    #     videos.append(tup)
        
    return render_template('frames/frames_daily_reports.html', reg=new_registrations, shared=projects_shared, size=size_uploaded, in_review=videos_in_review, in_approved=videos_approved)

@frames.route('/weekly-reports')
def frames_weekly_reports():
    new_registrations = db.session.query(db.func.count(FLP.id), FLP.createdAt)\
        .group_by(db.func.extract('week', FLP.createdAt))\
        .order_by(FLP.createdAt.desc())\
        .all()

    projects_shared = db.session.query(db.func.count(ProjectsShared.id), ProjectsShared.createdAt)\
        .group_by(db.func.extract('week',ProjectsShared.createdAt))\
        .order_by(ProjectsShared.createdAt.desc())\
        .all()
        #.filter(db.func.extract('day',ProjectsShared.createdAt) >= 22)\
        
    videos_in_review = db.session.query(db.func.count(ProjectVideos.id), ProjectVideos.createdAt)\
        .group_by(db.func.extract('week', ProjectVideos.createdAt))\
        .filter_by(approved = False)\
        .order_by(ProjectVideos.createdAt.desc())\
        .all()
        #.filter(db.func.extract('day',ProjectVideos.createdAt) >= 22)\
        
    videos_approved = db.session.query(db.func.count(ProjectVideos.id), ProjectVideos.createdAt)\
        .group_by(db.func.extract('week', ProjectVideos.createdAt))\
        .filter_by(approved = True)\
        .order_by(ProjectVideos.createdAt.desc())\
        .all()
        #.filter(db.func.extract('day',ProjectVideos.createdAt) >= 22)\
        
    size_uploaded = db.session.query(db.func.sum(ProjectVideos.size).label('size'), ProjectVideos.createdAt)\
        .group_by(db.func.extract('week',ProjectVideos.createdAt))\
        .order_by(ProjectVideos.createdAt.desc())\
        .all()
        #.filter(db.func.extract('day', ProjectVideos.createdAt) >= 22)\
    videos = []
    for i in range(len(videos_in_review)):
        tup = list((videos_in_review[i][0], videos_in_review[i][1]))
        if len(videos_approved) > i:
            tup.append(videos_approved[i][0])
        else:
            tup.append(0)
        videos.append(tup)
    return render_template('frames/frames_weekly_reports.html', reg=new_registrations, shared=projects_shared, size=size_uploaded, videos=videos)

@frames.route('/monthly-reports')
def frames_monthly_reports():
    return render_template('frames/frames_monthyl_reports.html')

@frames.route('/shared-projects')
def frames_shared_projects():
    projects_shared = db.session.query(ProjectsShared.projectId, Projects.projectName, VA.businessName, ProjectsShared.createdAt, Projects.createdAt, ProjectsShared.emailId)\
        .join(Projects, ProjectsShared.projectId == Projects.projectId)\
        .join(VA, Projects.vendorId == VA.vendorId)\
        .order_by(ProjectsShared.createdAt.desc())
    return render_template('frames/frames_shared.html', rows = projects_shared)