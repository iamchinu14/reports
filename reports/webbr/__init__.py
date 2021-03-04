from flask import Blueprint

webbr = Blueprint('webbr', __name__, url_prefix='/reports/webbr', template_folder="templates",
                          static_folder="static")

from reports.webbr import application