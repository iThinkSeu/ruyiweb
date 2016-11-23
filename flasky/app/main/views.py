#coding=utf-8
import json
from ..import db,log
import time, datetime
from . import main
from flask import render_template,session, redirect, url_for, abort, flash, request,\
    current_app
from .forms import HistoryWarnForm,SingleCountForm,DateCountForm,AllForm,StateFindForm,RepairForm
from flask.ext.login import login_user,logout_user,login_required,current_user
from ..models import Permission, Role, User, DeviceInfo,OnlineDeviceInfo,WarnInfo,faultWarnData,errorDict,handleDict,RepairInfo
from ..decorators import admin_required


# different pages route
@main.route('/')
@login_required
def index():
    # page=request.args.get('page',1,type=int)
    # devices = DeviceInfo.query_basic()
    # devices=alldevices[(page - 1) * per_page: page * per_page]
    # pagination = get_pagination(page=page, per_page=per_page, total=len(devices), record_name='devices',format_total=True,format_number=True)
    devices = OnlineDeviceInfo.query.order_by(OnlineDeviceInfo.id.asc()).all()
    return render_template('onlinestate.html',devices=devices)

@main.route('/onlinestate')
@login_required
def onlinestate():


    devices = OnlineDeviceInfo.query.order_by(OnlineDeviceInfo.id.asc()).all()
    # devices=alldevices[(page - 1) * per_page: page * per_page]
    # pagination = get_pagination(page=page, per_page=per_page, total=len(devices), record_name='devices',format_total=True,format_number=True)
    return render_template('onlinestate.html',devices=devices)

@main.route('/device/<number>')
@login_required
def devicestate(number):
    device = OnlineDeviceInfo.query.filter_by(id=number).first()
    # devices=alldevices[(page - 1) * per_page: page * per_page]
    # pagination = get_pagination(page=page, per_page=per_page, total=len(devices), record_name='devices',format_total=True,format_number=True)
    return render_template('device.html',device=device)

class CCode:
    def str(self, content, encoding='utf-8'):
        # 只支持json格式
        # indent 表示缩进空格数
        return json.dumps(content, encoding=encoding, ensure_ascii=False, indent=4)

cCode = CCode()

@main.route('/todaywarn')
@login_required
def todaywarn():
    warns=WarnInfo.query_today(time.strftime("%Y-%m-%d 00:00:00",time.localtime(time.time())),time.strftime("%Y-%m-%d 23:59:59",time.localtime(time.time())))
    # log.debug(warns)
    begin=time.strftime("%Y-%m-%d",time.localtime(time.time()))
    # log.debug(begin)
    # log.debug(str(datetime.datetime.utcnow()))
    return render_template('todaywarn.html',warns=warns,errorDict=errorDict,current_time=datetime.datetime.utcnow(),begin=begin,end=begin)

@main.route('/historywarn', methods=['GET', 'POST'])
@login_required
def historywarn():
    form=StateFindForm(begin=datetime.datetime.utcnow(),end=datetime.datetime.utcnow())
    if form.validate_on_submit():
        id=int(form.deviceid.data)
        begin=form.begin.data
        end=form.end.data
        log.error(begin)
        warns=WarnInfo.query_history(id,("%s 00:00:00")%begin,("%s 23:59:59")%end)
        return render_template('historywarn.html',warns=warns,errorDict=errorDict,form=form,begin=begin,end=end,id=id)
    return render_template('historywarn.html',form=form)

@main.route('/historyError/<number>/<errorNumber>/<begin>/<end>')
@login_required
def historyError(number,errorNumber,begin,end):

    warns=WarnInfo.query_specific(int(number),int(errorNumber),("%s 00:00:00")%begin,("%s 23:59:59")%end)

    # log.info(warns[0])
    # log.info(warns[1])
    return render_template('error.html',warns=warns,errorDict=errorDict,handleDict=handleDict,number=number,errorNumber=int(errorNumber),begin=begin,end=end)

@main.route('/historystate', methods=['GET', 'POST'])
@login_required
def historystate():
    stateform=StateFindForm(begin=datetime.datetime.utcnow(),end=datetime.datetime.utcnow())
    if stateform.validate_on_submit():
        id=int(stateform.deviceid.data)
        begin=stateform.begin.data
        end=stateform.end.data
        states=DeviceInfo.query_state(id,("%s 00:00:00")%begin,("%s 23:59:59")%end)
        # log.debug(states)
        # templiftcurrentlist={}
        # templifttemperaturelist={}
        # tempcanDirectVoltagelist={}
        # tempcanMotorCurrentlist={}
        # tempcanMotorTemperaturelist={}
        # tempcountvalue={'hornCount':0,'upBtnCount':0,'upBtnContactorCount':0,'downBtnCount':0,'masterContactorCount':0,'arresterCount':0}
        # for item in states:
        #     templiftcurrentlist[str(item.time)]=item.liftMotorCurrent
        #     templifttemperaturelist[str(item.time)]=item.liftMotorTemperature
        #     tempcanDirectVoltagelist[str(item.time)]=item.canDirectVoltage
        #     tempcanMotorCurrentlist[str(item.time)]=item.canMotorCurrent
        #     tempcanMotorTemperaturelist[str(item.time)]=item.canMotorTemperature
        #     tempcountvalue['hornCount']=tempcountvalue['hornCount']+item.hornCount
        #     tempcountvalue['upBtnCount']=tempcountvalue['upBtnCount']+item.upBtnCount
        #     tempcountvalue['upBtnContactorCount']=tempcountvalue['upBtnContactorCount']+item.upBtnContactorCount
        #     tempcountvalue['downBtnCount']=tempcountvalue['downBtnCount']+item.downBtnCount
        #     tempcountvalue['masterContactorCount']=tempcountvalue['masterContactorCount']+item.masterContactorCount
        #     tempcountvalue['arresterCount']=tempcountvalue['arresterCount']+item.arresterCount

        # # tempvalue=[{'data':templiftcurrentlist,'name':'提升电机电流'},{'data':templifttemperaturelist,'name':'提升电机温度'},{'data':tempcanDirectVoltagelist,'name':'电机电压'},{'data':tempcanMotorCurrentlist,'name':'电机电流'},{'data':tempcanMotorTemperaturelist,'name':'电机温度'}]
        # tempvalue=[{'data':templiftcurrentlist,'name':'提升电机电流'}]
        # # value =  [{name: 'Tokyo',data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2,26.5, 23.3, 18.3, 13.9, 9.6] }]
        # # value={'data': [["2016-10-13 22:59:09",0], ["2016-10-13 22:58:47" , 2], ["2016-10-13 22:58:52",0],["2016-10-13 22:59:13" , 1],["2016-10-13 22:59:16",0]],  'name': '电机电压'}
        # # value={'data': [['2013-04-01 00:00:00 UTC', 52.9], ['2013-05-01 00:00:00 UTC', 50.7],['2013-04-01 00:00:00 UTC', 11], ['2013-05-01 00:00:00 UTC', 12]], 'name': 'Chrome'}
        # value=cCode.str(tempvalue)
        # log.debug(templiftcurrentlist)
        return render_template('historystate.html',stateform=stateform,states=states,begin=begin,end=end,id=id)
    return render_template('historystate.html',stateform=stateform)

@main.route('/repair', methods=['GET', 'POST'])
@login_required
def repair():
    devices = OnlineDeviceInfo.query.order_by(OnlineDeviceInfo.id.asc()).all()  
    form=RepairForm()
    if request.method =='POST':
        if request.form.get('key',None)== "保存":
            deviceid=request.values.get("deviceid")
            errorType=int(request.values.get("errortype"))
            repairTime=request.values.get("repairtime")
            repairType=request.values.get("repairtype")
            remark=request.values.get("remark")
            repairMan=request.values.get("repairman")
            repair=RepairInfo(id=deviceid,repairTime=repairTime,repairType=repairType,errorType=errorType,remark=remark,repairMan=repairMan)
            # log.debug(repairinfo)
            db.session.add(repair)
            db.session.commit()
            repairinfoForFind=RepairInfo.query.filter_by(id=deviceid).all()
            log.debug(repairinfoForFind)
            session['deviceid']=deviceid
            return redirect(url_for('main.repair'))
        else:
            deviceid=request.values.get("deviceid")
            repairinfoForFind=RepairInfo.query.filter_by(id=deviceid).order_by(RepairInfo.repairTime.asc()).all()
            log.debug(repairinfoForFind)
            # log.debug(RepairInfo.query.filter_by(id=deviceid).order_by(RepairInfo.repairTime.asc()))
            # log.debug(repairinfoForFind)
            return render_template('repair.html',form=form,devices=devices,errorDict=errorDict,current_time=datetime.datetime.utcnow(),repairinfoForFind=repairinfoForFind)
    deviceid=session.get('deviceid')
    repairinfoForFind=[]
    if deviceid is not None:
        repairinfoForFind=RepairInfo.query.filter_by(id=deviceid).order_by(RepairInfo.repairTime.asc()).all()
    return render_template('repair.html',form=form,devices=devices,errorDict=errorDict,current_time=datetime.datetime.utcnow(),repairinfoForFind=repairinfoForFind)

# @main.route('/repair/<number>', methods=['GET', 'POST'])
# @login_required
# def repairfind(number):
#     devices = OnlineDeviceInfo.query.order_by(OnlineDeviceInfo.id.asc()).all()  
#     form=RepairForm()    
#     return render_template('repair.html',form=form,devices=devices,errorDict=errorDict,current_time=datetime.datetime.utcnow())

@main.route('/warncount', methods=['GET', 'POST'])
@login_required
def warncount():
    log.debug("here")

    singlecount=[]
    devices = OnlineDeviceInfo.query.order_by(OnlineDeviceInfo.id.asc()).all()  
    if request.method == 'POST':
        s_option=request.values.getlist("s_option")
        trucktype=request.values.get("trucktype")
        deviceid=int(request.values.get("deviceid"))

        log.debug(s_option)
        log.debug(trucktype)
        log.debug(deviceid)        
        singleWarnCountDict=WarnInfo.querySingleWarnCount(s_option,trucktype,deviceid)
        for warn in singleWarnCountDict:
            singlecount.append(['('+str(warn[0])+') '+str(errorDict[warn[0]]),warn[1]])
        return render_template('warncount1.html',current_time=datetime.datetime.utcnow(),errorDict=errorDict,devices=devices,singlecount=singlecount,deviceid=deviceid)
    return render_template('warncount1.html',current_time=datetime.datetime.utcnow(),errorDict=errorDict,devices=devices,singlecount=singlecount)

@main.route('/datecount', methods=['GET', 'POST'])
@login_required
def datewarncount():
    datecount=[]
    devices = OnlineDeviceInfo.query.order_by(OnlineDeviceInfo.id.asc()).all()  
    if request.method == 'POST':
        s_option=request.values.getlist("s_option")
        trucktype=request.values.get("trucktype")
        begin=request.values.get("begin")
        end=request.values.get("end")
        log.debug(s_option)
        log.debug(trucktype)      
        dateWarnCountDict=WarnInfo.queryDateWarnCount(s_option,trucktype,begin,end)
        for warn in dateWarnCountDict.iteritems():
            datecount.append(['('+str(warn[0])+') '+str(errorDict[warn[0]]),warn[1]])
        return render_template('warncount2.html',current_time=datetime.datetime.utcnow(),errorDict=errorDict,devices=devices,datecount=datecount,begin=begin,end=end)
    return render_template('warncount2.html',current_time=datetime.datetime.utcnow(),errorDict=errorDict,devices=devices)

@main.route('/allcount', methods=['GET', 'POST'])
@login_required
def allwarncount():
    devices = OnlineDeviceInfo.query.order_by(OnlineDeviceInfo.id.asc()).all()
    allcount=[]  
    if request.method == 'POST':
        s_option=request.values.getlist("s_option")
        trucktype=request.values.get("trucktype")
        log.debug(s_option)
        log.debug(trucktype)      
        allWarnCountDict=WarnInfo.queryAllWarnCount(s_option,trucktype)
        for warn in allWarnCountDict.iteritems():
            # log.debug(warn)
            allcount.append(['('+str(warn[0])+') '+str(errorDict[warn[0]]),warn[1]])
        return render_template('warncount3.html',current_time=datetime.datetime.utcnow(),errorDict=errorDict,devices=devices,allcount=allcount)
    return render_template('warncount3.html',current_time=datetime.datetime.utcnow(),errorDict=errorDict,devices=devices)



@main.route('/usermanager', methods=['GET', 'POST'])
@login_required
def usermanager():
    if request.method=='POST':
        username=request.values.get('username',None)
        if username:
            # print username
            
            user=User.query.filter(User.username==username).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('已将该账户删除')
            return redirect(url_for('main.usermanager'))
    else:     
        users=User.query.order_by(User.role_id.asc()).all()
  
        return render_template('usermanager.html',users=users)


