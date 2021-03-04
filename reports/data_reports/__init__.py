from flask import Blueprint

image_data = Blueprint('image_data', __name__, url_prefix='/reports/image-data', template_folder="templates",
                          static_folder="static")

from reports.data_reports import application