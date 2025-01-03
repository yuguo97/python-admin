from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import users  # 导入视图函数 