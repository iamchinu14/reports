from db_config import sql as db

class FramesLandingPage(db.Model):
    __tablename__ = 'vendor_frames_landing_page'
    id = db.Column(db.Integer, primary_key = True)
    userId = db.Column('user_id', db.String(50), unique = True)
    name = db.Column('name', db.String(50))
    emailId = db.Column('email_id', db.String(50))
    mobileNumber = db.Column('mobile_number', db.String(50))
    city = db.Column('city', db.String(50))
    videoCount = db.Column('video_review_count_per_month', db.String(50))
    industry = db.Column('industry', db.String(50))
    createdAt = db.Column('created_at', db.DateTime)
    updatedAt = db.Column('updated_at', db.DateTime)

class AccessLogs(db.Model):
    __tablename__ = 'spyne_access_log'
    id = db.Column(db.Integer, primary_key = True)
    userId = db.Column('user_id',db.String(50), unique = True)
    service = db.Column(db.String(50))
    sourceUrl = db.Column('source_url', db.String(256))
    visitCount = db.Column('visit_count', db.String(56))
    startDate = db.Column('start_date_in_sec', db.String(56))
    expiryDate = db.Column('expiry_date_in_sec', db.String(56))
    ipAddress = db.Column('ip_address', db.String(56))
    deviceType = db.Column('device_type', db.String(56))
    browser = db.Column(db.String(256))
    createdAt = db.Column('created_date', db.DateTime)
    updatedAt = db.Column('updated_date', db.DateTime)

class VendorAccount(db.Model):
    __tablename__ = 'vendor_account'
    id = db.Column(db.Integer, primary_key = True)
    vendorId = db.Column('vendor_id', db.String(50), unique = True)
    vendorType = db.Column('vendor_type', db.String(50), unique = True)
    userId = db.Column('user_id', db.String(50), unique = True)
    businessName = db.Column('business_name', db.String(255))

class Projects(db.Model):
    __tablename__ = 'spyne_video_project'
    id = db.Column(db.Integer, primary_key = True)
    projectId = db.Column('project_id',db.String(191), unique = True)
    vendorId = db.Column('vendor_id', db.String(191))
    userId = db.Column('user_id', db.String(191))
    projectName = db.Column('project_name', db.String(191))
    createdAt = db.Column('created_date', db.DateTime)
    updatedAt = db.Column('updated_date', db.DateTime)

class ProjectsShared(db.Model):
    __tablename__ = 'spyne_video_users'
    id = db.Column(db.Integer, primary_key = True)
    projectId = db.Column('project_id',db.String(45), unique = True)
    clientName =  db.Column('client_name', db.String(45))
    emailId = db.Column('email_id', db.String(45), unique = True)
    pin = db.Column(db.String(10))
    token = db.Column(db.String(45), unique = True)
    allowDownload = db.Column('allow_download', db.Boolean)
    mailSent = db.Column('mail_sent', db.Boolean)
    createdAt = db.Column('created_added', db.DateTime)
    updatedAt = db.Column('updated_date', db.DateTime)

class ProjectVideos(db.Model):
    __tablename__ = 'spyne_video_list'
    id = db.Column(db.Integer, primary_key = True)
    projectId = db.Column('project_id',db.String(512))
    videoId = db.Column('video_id', db.String(512), unique = True)
    vendorId = db.Column('vendor_id', db.String(512))
    name = db.Column(db.String(512))
    title = db.Column(db.String(512))
    approved = db.Column(db.Boolean)
    size = db.Column(db.Float)
    createdAt = db.Column('created_date', db.DateTime)
    updatedAt = db.Column('updated_date', db.DateTime)


