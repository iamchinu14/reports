from flask import Blueprint

clippr = Blueprint('clippr', __name__, url_prefix='/reports/clippr', template_folder="templates",
                          static_folder="static")

from reports.clippr import application