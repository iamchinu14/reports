from flask import Blueprint

spyne = Blueprint('spyne', __name__, url_prefix='/reports/spyne', template_folder="templates",
                          static_folder="static")

from reports.spyne import application

                          