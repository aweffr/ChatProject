from flask import Blueprint

main = Blueprint("main", __name__)

from . import views, errors

'''
本工程中views.py和errors.py与__init__.py文件同级

为什么在创建main后才导入:
    为了避免循环依赖, 因为在views.py和errors.py中还要导入蓝本main
'''
