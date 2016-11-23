# encoding=utf8
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField,RadioField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          '用户名必须由字母、'
                                          '数字、下划线组成.')])
    password = PasswordField('密码', validators=[Required(message='密码不能为空.')])
    remeber_me = BooleanField('记住登录状态')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          '用户名必须由字母、'
                                          '数字、下划线组成.')])
    password = PasswordField('密码', validators=[
        Required(), EqualTo('password2', message='两次密码必须一样.')])
    password2 = PasswordField('确认密码', validators=[Required()])
    rank = RadioField('用户权限', coerce=int,choices=[(0, '普通用户'),(1,'管理员')],default=0)
    submit = SubmitField('注册')

    # def validate_email(self, field):
    #     if User.query.filter_by(email=field.data).first():
    #         raise ValidationError('该邮箱已经注册.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在.')



class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='两次密码必须一样.')])
    password2 = PasswordField('确认新密码', validators=[Required()])
    submit = SubmitField('更改密码')