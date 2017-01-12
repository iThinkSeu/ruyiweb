# encoding=utf8
from flask import render_template,redirect,request,url_for,flash
from flask.ext.login import login_user,logout_user,login_required,current_user
from . import auth
from ..import db
from ..models import User 
from .forms import LoginForm,RegistrationForm,ChangePasswordForm

# no use of confirmed in ruyi ,so // it
# @auth.before_app_request
# def before_request():
#     if current_user.is_authenticated()\
#             and not current_user.confirmed\
#             and request.endpoint[:5]!='auth.'\
#             and request.endpoint != 'static':
#         return redirect(url_for('main.index'))    

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经注销')
    return redirect(url_for('main.index'))

@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remeber_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash ('错误的用户名或密码')
    return render_template('auth/login.html',form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('您的密码已更改')
            return redirect(url_for('main.index'))
        else:
            flash('错误的密码')
    return render_template("auth/change_password.html", form=form)

@auth.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,password=form.password.data,rank=form.rank.data,role_id=(1 if (form.rank.data==1) else 2))
        db.session.add(user)
        db.session.commit()
        if form.rank.data==1:
            flash('注册成功，权限为管理员')
        else:
            flash('注册成功，权限为普通用户')
        return redirect(url_for('main.usermanager'))
    return render_template('auth/register.html', form=form)

# @auth.route('/usermanager')
# @login_required
# def usermanager():
#     return  render_template('auth/usermanager.html')