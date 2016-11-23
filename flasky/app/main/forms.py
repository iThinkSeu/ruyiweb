# encoding=utf8
from flask.ext.wtf import Form
from wtforms import  SubmitField,SelectField,TextAreaField 
from wtforms.fields.html5 import DateField,DateTimeField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo,NumberRange
from wtforms import validators
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ..models import OnlineDeviceInfo
import datetime
class StateFindForm(Form):
    # ids=OnlineDeviceInfo.query.all()
    def query_factory():
        return [r.id for r in OnlineDeviceInfo.query.all()]

    def get_pk(obj):
        return obj       
    deviceid = QuerySelectField(label='叉车编号', validators=[validators.required()], query_factory=query_factory, get_pk=get_pk)
    begin = DateField('起始时间', format='%Y-%m-%d',default=datetime.datetime.utcnow())
    end = DateField('结束时间', format='%Y-%m-%d',default=datetime.datetime.utcnow())

    submit = SubmitField('查询')

class HistoryWarnForm(Form):
    begin = DateField('起始时间', format='%Y-%m-%d',default=datetime.datetime.utcnow(), validators=[validators.required()])
    end = DateField('结束时间', format='%Y-%m-%d',default=datetime.datetime.utcnow(), validators=[validators.required()])
    submit = SubmitField('确认')

class AllForm(Form):
    submit = SubmitField('查询')
    trucktype=SelectField(label='故障车型', validators=[validators.required()], choices=[('1','CBD20R-II'),('2','其他')])

class DateCountForm(Form):
    begin = DateField('起始时间', format='%Y-%m-%d',default=datetime.datetime.utcnow(), validators=[validators.required()])
    end = DateField('结束时间', format='%Y-%m-%d',default=datetime.datetime.utcnow(), validators=[validators.required()])
    trucktype=SelectField(label='故障车型', validators=[validators.required()], choices=[('1','CBD20R-II'),('2','其他')])
    submit = SubmitField('查询')



class SingleCountForm(Form):
    # ids=OnlineDeviceInfo.query.all()
    def query_factory():
        return [r.id for r in OnlineDeviceInfo.query.all()]

    def get_pk(obj):
        return obj
        
    deviceid = QuerySelectField(label='叉车编号', validators=[validators.required()], query_factory=query_factory, get_pk=get_pk)
    trucktype=SelectField(label='故障车型', validators=[validators.required()], choices=[('1','CBD20R-II'),('2','其他')])
    submit = SubmitField('查询')



class RepairForm(Form):
    # ids=OnlineDeviceInfo.query.all()
  	
    repairtime = DateField('维修时间', format='%Y-%m-%d',default=datetime.datetime.utcnow(), validators=[validators.required()])
    remark = TextAreaField('备注')
    repairman= TextAreaField('维修人员')
    repairtype=SelectField(label='维修类型', validators=[validators.required()], choices=[('1','更换'),('2','保养'),('3','检修'),('4','其他')])
    submit = SubmitField('查询')
    submit =SubmitField('添加')