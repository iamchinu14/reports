from flask import Blueprint

albumm = Blueprint('albumm', __name__, url_prefix='/reports/albumm', template_folder="templates",
                          static_folder="static")

from reports.albumm import application

                          