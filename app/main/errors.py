from flask import render_template
from . import main

'''
在蓝本中编写错误处理时, 用app_errorhandler才能注册全局的错误处理程序.
用errorhandler只能在蓝本中的错误触发
'''


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500
