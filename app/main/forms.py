from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

'''
为了能够完全修改程序的页面, 表单对象也要移到蓝本中
'''


class NameForm(FlaskForm):
    name = StringField('请输入登录名',
                       validators=[DataRequired(), Length(min=1, message="至少一个字符")])
    submit = SubmitField('提交')
