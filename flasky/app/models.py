# encoding=utf8
from werkzeug.security import generate_password_hash,check_password_hash
from flask import current_app
from flask.ext.login  import UserMixin, AnonymousUserMixin
from .import db,login_manager,log
from sqlalchemy import distinct,asc,desc,and_,func
import time, datetime

errorDict={ 1: "高踏板故障" , 2: "预充电故障", 3:"过流",4: "控制器过热",5:"主回路断电" , 
             6:"电流采样电路故障" , 8:"BMS故障" , 9:"电池组欠压" , 10:"电池组过压" 
            , 11:"电机过热" , 13:"加速器故障 " ,38:"电流传感器硬件故障" ,39:"温度传感器硬件故障" ,
             40:"提升电机过流" ,41:"提升电机过热" ,
            42:"CAN通讯故障" ,43:"喇叭开关正极断路" ,44:"喇叭地线断路" ,45:"提升开关正极断路" ,
            46:"提升接触器线圈地线断路" ,47:"提升接触器硬件故障" ,48:"下降开关正极断路" ,49:"下降电磁阀地线断路" ,
            50:"主接触器线圈正极断路" ,51:"主接触器触点正极断路" ,52:"主接触器硬件故障" ,53:"制动器线圈正极断路" ,54:"制动器离线或线圈硬件故障",55:"开关量输入检测电路故障" ,56:"制动器控制电路故障" ,57:"电流采样电路故障" ,58:"温度测量电路故障" ,59:"CAN总线通信故障" ,60:"EEPROM读写故障" ,61:"Flash读写故障" ,62:"时钟芯片读写故障" ,63:"GPRS模块通信故障" ,64:"WIFI模块通信故障" }

handleDict={ 1: "停止运行，检查踏板并归位" , 2: "停止运行，检查电源板有无明显损坏，检查电源板与控制板之间的排线是否可靠连接", 3:"停机检查：第一步调整控制参数，第二步调整输出力矩，如还不能解决问题则返厂维修",4: "停机检查风扇是否正常工作，风道是否顺畅",5:"停机检查主回路保险、接触器、急停开关等" , 
             6:"停止运行，维修或更换控制器" , 8:"BMS 故障或者电池组异常" , 9:"及时给蓄电池组充电" , 10:"检查电池组是否正常，适当减小能量回馈" 
            , 11:"停机冷却或者增加电机散热方式" , 13:"停机，检查加速器线路是否正常连接。如果已损坏，需返厂维修 " ,38:"停机，检查电流传感器线路是否正常连接，如果已损坏，需维修或更换电流传感器" ,39:"停机，检查温度传感器线路是否正常连接，如果已损坏，需维修或更换温度传感器" ,
             40:"停止运行，检查是否超载" ,41:"停机冷却，检查是否过载" ,
            42:"停机，检查CAN通讯链路。如果已损坏，需返厂维修" ,43:"停机，检查喇叭开关电路" ,44:"检查喇叭开关电路" ,45:"检查提升开关电路" ,
            46:"检查提升接触器线圈电路" ,47:"检查或者更换提升接触器" ,48:"检查下降开关电路" ,49:"检查下降电磁阀电路" ,
            50:"检查主接触器线圈电路" ,51:"检查主接触器电路" ,52:"检查或更换主接触器" ,53:"检查制动器线圈电路" ,54:"检查制动器电路。如果已损坏，需返厂维修",55: "检查开关量检测电路" ,56: "检查制动器控制电路、控制继电器、制动器或者控制信号检测电路" ,57: "检查电流采样电路和电流传感器输入信号" ,58: "检查温度测量的恒流源电路和信号放大电路" ,59: "检查CAN总线通信线路和CAN收发控制芯片" ,60: "检查EEPROM存储芯片" ,61: "检查Flash存储芯片" ,62: "检查时钟芯片" ,63: "检查GPRS通信模块" ,64: "检查WIFI通信模块" }

class Permission:
    VISIT=0x01
    WRITE=0X02
    ADMINISTER=0X80

class RepairInfo(db.Model):
    __tablename__= 'repairinfo'
    number=db.Column(db.Integer ,primary_key=True)
    id = db.Column(db.String(12),primary_key=True)
    repairTime = db.Column(db.Date(),primary_key=True)
    errorType = db.Column(db.Integer,primary_key=True)
    repairType = db.Column(db.String(255))
    repairMan = db.Column(db.String(255))
    remark = db.Column(db.String(255))

    def __repr__(self):
        return '<RepairInfo %r>'% self.id


class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64))
    default=db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)
    users=db.relationship('User',backref='role',lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles={
        'User':(Permission.VISIT|Permission.WRITE,True),
        'Administrator':(0xff,False)


        }
        for r in roles:
            role=Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
                role.permissions=roles[r][0]
                role.default=roles[r][1]
                db.session.add(role)
        db.session.commit()
    def __repr__(self):
        return '<Role %r>'% self.name

class User(UserMixin , db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    rank=db.Column(db.Integer)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    password_hash=db.Column(db.String(128))
    confirmed=db.Column(db.Boolean,default=False)

    @staticmethod
    def insert_admin():
        admin=User(username='admin',password='admin',rank=1)
        db.session.add(admin)
        db.session.commit()
    @staticmethod
    def insert_user():
        user=User(username='yang',password='4657821',rank=0)
        db.session.add(user)
        db.session.commit()

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.rank ==1:
                self.role=Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role=Role.query.filter_by(default=True).first()
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self ,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def can(self,permissions):
        return self.role is not None and (self.role.permissions&permissions)==permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' %self.username

class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def  is_administrator(self):
        return False

login_manager.anonymous_user=AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))






class OnlineDeviceInfo(db.Model):
    __tablename__='onlinedeviceinfo'

    id = db.Column(db.String(12), primary_key=True)
    time = db.Column(db.DateTime(), primary_key=True)
    runningTime = db.Column(db.Text())
    hornSwitch = db.Column(db.Boolean)
    horn = db.Column(db.Boolean)
    hornGround = db.Column(db.Boolean)
    upBtnSwitch = db.Column(db.Boolean)
    upBtnContactorCoilUpper = db.Column(db.Boolean)
    upBtnContactorCoilDown = db.Column(db.Boolean)
    upBtnContactUpper = db.Column(db.Boolean)
    upBtnContactDown = db.Column(db.Boolean)
    downBtnSwitch = db.Column(db.Boolean)
    downBtnsolenoidvalveUpper = db.Column(db.Boolean)
    downBtnsolenoidvalveDown = db.Column(db.Boolean)
    masterContactorCoilUpper = db.Column(db.Boolean)
    masterContactorCoilDown = db.Column(db.Boolean)
    masterContactUpper = db.Column(db.Boolean)
    masterContactDown = db.Column(db.Boolean)
    arresterUpper = db.Column(db.Boolean)
    arresterDown = db.Column(db.Boolean)
    liftMotorCurrent = db.Column(db.Integer)
    liftMotorTemperature = db.Column(db.Integer)
    canDirectionandSpeedMode = db.Column(db.Integer)
    canSpeed = db.Column(db.Integer)
    canError = db.Column(db.Integer)
    canLowPowerMode = db.Column(db.Integer)
    canCourse = db.Column(db.Integer)
    canDirectVoltage = db.Column(db.Integer)
    canMotorCurrent = db.Column(db.Integer)
    canMotorTemperature = db.Column(db.Integer)
    hornCount = db.Column(db.Integer)
    upBtnCount = db.Column(db.Integer)
    upBtnContactorCount = db.Column(db.Integer)
    downBtnCount = db.Column(db.Integer)
    masterContactorCount = db.Column(db.Integer)
    arresterCount = db.Column(db.Integer)




class DeviceInfo(object):

    _mapper = {}

    @staticmethod
    def model(device_id):
        table_index = device_id%100
        class_name = 'deviceinfo_%d' % table_index

        ModelClass = DeviceInfo._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(class_name, (db.Model,), {
                '__module__' : __name__,
                '__name__' : class_name,
                '__tablename__' : 'deviceinfo_%d' % table_index,

                'id' : db.Column(db.String(12), primary_key=True),
                'time' : db.Column(db.DateTime(), primary_key=True),
                'runningTime' : db.Column(db.Text()),
                'hornSwitch' : db.Column(db.Boolean),
                'horn' : db.Column(db.Boolean),
                'hornGround' : db.Column(db.Boolean),
                'upBtnSwitch' : db.Column(db.Boolean),
                'upBtnContactorCoilUpper' : db.Column(db.Boolean),
                'upBtnContactorCoilDown' : db.Column(db.Boolean),
                'upBtnContactUpper' : db.Column(db.Boolean),
                'upBtnContactDown' : db.Column(db.Boolean),
                'downBtnSwitch' : db.Column(db.Boolean),
                'downBtnsolenoidvalveUpper' : db.Column(db.Boolean),
                'downBtnsolenoidvalveDown' : db.Column(db.Boolean),
                'masterContactorCoilUpper' : db.Column(db.Boolean),
                'masterContactorCoilDown' : db.Column(db.Boolean),
                'masterContactUpper' : db.Column(db.Boolean),
                'masterContactDown' : db.Column(db.Boolean),
                'arresterUpper' : db.Column(db.Boolean),
                'arresterDown' : db.Column(db.Boolean),
                'liftMotorCurrent' : db.Column(db.Integer),
                'liftMotorTemperature' : db.Column(db.Integer),
                'canDirectionandSpeedMode' : db.Column(db.Integer),
                'canSpeed' : db.Column(db.Integer),
                'canError' : db.Column(db.Integer),
                'canLowPowerMode' : db.Column(db.Integer),
                'canCourse' : db.Column(db.Integer),
                'canDirectVoltage' : db.Column(db.Integer),
                'canMotorCurrent' : db.Column(db.Integer),
                'canMotorTemperature' : db.Column(db.Integer),
                'hornCount' : db.Column(db.Integer),
                'upBtnCount' : db.Column(db.Integer),
                'upBtnContactorCount' : db.Column(db.Integer),
                'downBtnCount' : db.Column(db.Integer),
                'masterContactorCount' : db.Column(db.Integer),
                'arresterCount' : db.Column(db.Integer),


            })
            DeviceInfo._mapper[class_name] = ModelClass

        cls = ModelClass()
        cls.id = device_id
        return cls
    @staticmethod
    def query_state(device_id,begin,end):
        table_index = device_id%100
        device = DeviceInfo.model(table_index)
        
        # devicestates=db.session.query(DeviceInfo._mapper['deviceinfo_%d' % table_index].time,DeviceInfo._mapper['deviceinfo_%d' % table_index].liftMotorCurrent,DeviceInfo._mapper['deviceinfo_%d' % table_index].liftMotorTemperature,DeviceInfo._mapper['deviceinfo_%d' % table_index].canDirectVoltage,DeviceInfo._mapper['deviceinfo_%d' % table_index].canMotorCurrent,DeviceInfo._mapper['deviceinfo_%d' % table_index].canMotorTemperature,func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].hornCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].upBtnCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].upBtnContactorCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].downBtnCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].masterContactorCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].arresterCount)).filter(DeviceInfo._mapper['deviceinfo_%d' % table_index].time.between(begin,end)).filter(DeviceInfo._mapper['deviceinfo_%d' % table_index].id==device_id).order_by('time asc').all()
        devicestates=db.session.query(DeviceInfo._mapper['deviceinfo_%d' % table_index]).filter(DeviceInfo._mapper['deviceinfo_%d' % table_index].time.between(begin,end)).filter(DeviceInfo._mapper['deviceinfo_%d' % table_index].id==device_id).order_by('time asc').limit(1000).all()
        if devicestates:
            endtime=devicestates[len(devicestates)-1].time
            begintime=devicestates[0].time
        else:
            begintime=begin
            endtime=end
        log.debug(endtime)
        devicecounts=db.session.query(func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].hornCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].upBtnCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].upBtnContactorCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].downBtnCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].masterContactorCount),func.sum(DeviceInfo._mapper['deviceinfo_%d' % table_index].arresterCount)).filter(DeviceInfo._mapper['deviceinfo_%d' % table_index].time.between(begin,endtime)).filter(DeviceInfo._mapper['deviceinfo_%d' % table_index].id==device_id).order_by('time asc').all()
        liftMotorCurrentList=[]
        liftMotorTemperatureList=[]
        canDirectVoltageList=[]
        canMotorCurrentList=[]
        canMotorTemperatureList=[]
        countsList=[]
        for state in devicestates:
            liftMotorCurrentList.append([1000*time.mktime(state.time.timetuple()),int(state.liftMotorCurrent)])
            liftMotorTemperatureList.append([1000*time.mktime(state.time.timetuple()),int(state.liftMotorTemperature)])
            canDirectVoltageList.append([1000*time.mktime(state.time.timetuple()),int(state.canDirectVoltage)])
            canMotorCurrentList.append([1000*time.mktime(state.time.timetuple()),int(state.canMotorCurrent)])
            canMotorTemperatureList.append([1000*time.mktime(state.time.timetuple()),int(state.canMotorTemperature)])
        # for item in devicecounts:
        #     log.debug(item)
        #     countsList.append(int(item))

        return [[liftMotorCurrentList,liftMotorTemperatureList,canDirectVoltageList,canMotorCurrentList,canMotorTemperatureList],devicecounts,begintime,endtime]
    @staticmethod
    def query_test(device_id):
        table_index = device_id%100
        device = DeviceInfo.model(table_index)
        print DeviceInfo._mapper['deviceinfo_%d' % table_index]
        devicenumber=db.session.query(DeviceInfo._mapper['deviceinfo_%d' % table_index].id.distinct()).all()
        print devicenumber 
        for item in devicenumber:
            temp= device.query.filter_by(id=item[0]).order_by('time desc').first()
            print temp.id,temp.time
    
    @staticmethod
    def query_basic():
        queryScore=[]
        for i in range(100):
            table_index = i%100
            device = DeviceInfo.model(table_index)
            # print DeviceInfo._mapper['deviceinfo_%d' % table_index]
            devicenumber=db.session.query(DeviceInfo._mapper['deviceinfo_%d' % table_index].id.distinct()).all()
            for item in devicenumber:
                temp= device.query.filter_by(id=item[0]).order_by('time desc').first()
                # print temp.id,temp.time
                queryScore.append(temp)
        # print type(queryScore)
        # for item in queryScore:   
        #     print 'old%d'%int(item.id)
        queryScore.sort(key= lambda x:int(x.id))
        # for item in queryScore:   
        #     print item.id
        return queryScore
    @staticmethod
    def type_test(device_id):
        table_index = device_id%100
        device = DeviceInfo.model(table_index)
        temp= device.query.order_by('time desc').all()
        pagination=device.query.order_by('time desc').paginate(1,per_page=10,error_out=False)
        print pagination
        print temp
        print type(temp)

class WarnInfo(object):
    _mapper = {}
    @staticmethod
    def model(device_id):
        table_index = device_id%10
        class_name = 'warninfo_%d' % table_index

        ModelClass = WarnInfo._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(class_name, (db.Model,), {
                '__module__' : __name__,
                '__name__' : class_name,
                '__tablename__' : 'warninfo_%d' % table_index,

                'id' : db.Column(db.String(12), primary_key=True),
                'errorNumber' : db.Column(db.Integer,primary_key=True),
                'errorTime' : db.Column(db.DateTime(), primary_key=True),
                'errorValue' : db.Column(db.Integer),
                'errorLevel' : db.Column(db.SmallInteger),
                'errorState' : db.Column(db.SmallInteger,primary_key=True),
                

            })
            WarnInfo._mapper[class_name] = ModelClass

        cls = ModelClass()
        cls.id = device_id
        return cls


    @staticmethod
    def query_specific(device_id,errorNumber,begin,end):
        table_index =device_id%10
        device = WarnInfo.model(table_index)
        
        devicewarns=db.session.query(WarnInfo._mapper['warninfo_%d' % table_index]).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorTime.between(begin,end)).filter(WarnInfo._mapper['warninfo_%d' % table_index].id==device_id).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorState!=2).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorNumber==errorNumber).order_by('errorTime asc').all()
        recoverywarns=db.session.query(WarnInfo._mapper['warninfo_%d' % table_index]).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorTime.between(begin,end)).filter(WarnInfo._mapper['warninfo_%d' % table_index].id==device_id).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorState==2).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorNumber==errorNumber).order_by('errorTime asc').all()
        warnslist=[]
        recoverylist=[]
        for warn in devicewarns:
            # warnslist.append([warn.errorTime,int(warn.errorValue)])
            warnslist.append([1000*time.mktime(warn.errorTime.timetuple()),int(warn.errorValue)])
        for warn in recoverywarns:
            recoverylist.append([1000*time.mktime(warn.errorTime.timetuple()),int(warn.errorValue)])   
            # recoverylist.append([warn.errorTime,int(warn.errorValue)])
        
        # print warnInfoList
        return  [warnslist,recoverylist]    
        
    @staticmethod
    def query_history(device_id,begin,end):
        table_index = device_id%10
        device = WarnInfo.model(table_index)      
        devicewarns=db.session.query(WarnInfo._mapper['warninfo_%d' % table_index].errorNumber,func.count('*')).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorTime.between(begin,end)).filter(WarnInfo._mapper['warninfo_%d' % table_index].id==device_id).order_by('errorNumber asc,errorTime asc').group_by('errorNumber').all()
        return  devicewarns
        
    @staticmethod
    def query_today(begin,end):
        log.info(begin)
        log.info(end)
        queryScore=[]
        for i in range(10):
            table_index = i%10
            warn = WarnInfo.model(table_index)
            todaywarn=db.session.query(WarnInfo._mapper['warninfo_%d' % table_index].id,WarnInfo._mapper['warninfo_%d' % table_index].errorNumber,func.count('*')).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorTime.between(begin,end)).order_by('id asc ,errorNumber asc').group_by('errorNumber,id').all()

            for warn in todaywarn :   
                queryScore.append(warn)

        # log.debug(queryScore)
        
        return  queryScore

    @staticmethod
    def today():
        print time.strftime("%Y-%m-%d 00:00:00",time.localtime(time.time()))

    @staticmethod
    def querySingleWarnCount(s_option,trucktype,device_id):
        table_index=device_id%10
        warn = WarnInfo.model(table_index)
        warnnumbers=db.session.query(WarnInfo._mapper['warninfo_%d' % table_index].errorNumber,func.count('*')).filter(WarnInfo._mapper['warninfo_%d' % table_index].id==device_id).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorNumber.in_(s_option)).group_by('errorNumber').all()
        # log.debug(warnnumbers)
        return warnnumbers
    @staticmethod
    def queryDateWarnCount(s_option,trucktype,begin,end):
        warnCountDict={}
        for i in range(10):
            table_index = i%10
            warn = WarnInfo.model(table_index)
            warnnumbers=db.session.query(WarnInfo._mapper['warninfo_%d' % table_index].errorNumber,func.count('*')).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorTime.between(begin,end)).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorNumber.in_(s_option)).group_by('errorNumber').all()         
            # log.debug(warnnumbers)
            for warnnumber in warnnumbers:
                if warnnumber[0] in warnCountDict: 
                    warnCountDict[warnnumber[0]]+=warnnumber[1]
                else:
                    warnCountDict[warnnumber[0]]=warnnumber[1]
        # log.debug(warnCountDict)
        return warnCountDict
    @staticmethod   
    def queryAllWarnCount(s_option,trucktype):
        warnCountDict={}
        for i in range(10):
            table_index = i%10
            warn = WarnInfo.model(table_index)
            warnnumbers=db.session.query(WarnInfo._mapper['warninfo_%d' % table_index].errorNumber,func.count('*')).filter(WarnInfo._mapper['warninfo_%d' % table_index].errorNumber.in_(s_option)).group_by('errorNumber').all()         
            # log.debug(warnnumbers)
            for warnnumber in warnnumbers:
                if warnnumber[0] in warnCountDict: 
                    warnCountDict[warnnumber[0]]+=warnnumber[1]
                else:
                    warnCountDict[warnnumber[0]]=warnnumber[1]
        # log.debug(warnCountDict)
        return warnCountDict




class faultWarnData:
    def __init__(self):
        self.id=''
        self.errorTime=[]
        self.errorValue=[]
        self.errorState=[]
        self.errorNumber=None
        self.errorLevel=0
        self.errorCount=0