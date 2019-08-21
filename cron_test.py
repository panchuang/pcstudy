# _*_ coding:utf-8 _*_
__author__ = 'pan'

from apscheduler.schedulers.background import BackgroundScheduler
import os,time
import pymongo
# from config.settings import STATISTIC_DATA_TYPE,Settings
# from api.db.mongo_client import PymongoClients
import datetime
import logging

class Settings:
    DEBUG = False
    MONGOCLIENT = {
        "host": "127.0.0.1",
        "port": 27017,
        "db": "rom_private"
    }

#数据库连接
class PymongoClient:
    def __init__(self, server_options):
        self.dbName = server_options['db']
        # database in mongodb
        self.pymongoClient = pymongo.MongoClient(host="127.0.0.1",port=27017)[self.dbName]

    def create_id(self, name):
        self.pymongoClient.ids.ensure_index('name', unique=True)
        self.pymongoClient.ids.save({'name': name, 'id': 0})




#数据汇总计算
def dataAggregation():
    server_options = Settings()
    pymongo_client = PymongoClient(server_options.MONGOCLIENT).pymongoClient
    dtime = datetime.date.today()-datetime.timedelta(days=1)
    dtime = dtime.strftime('%Y-%m-%d')
    org_infos = pymongo_client.organization.find({},{'_id':0})
    logging.warning("-------------------开始执行数据统计任务------------------")
    for org in org_infos:
        org_id = org['id']
        get_statistic_data(org_id,dtime)

#计算并保存
def get_statistic_data(org_id,dtime):
    dev_online_num_count = dev_online_num(dtime,org_id)
    dev_online_count = dev_online(dtime,org_id)
    internet_violations_count = internet_violations(dtime,org_id)
    sen_word10_count = sen_word10(dtime,org_id)
    app_using_len5_count = app_using_len5(dtime,org_id)
    safe_hidden_trouble_count = safe_hidden_trouble(dtime,org_id)
    app_using_count = app_using(dtime,org_id)
    violations_fun_count = violations_fun(dtime,org_id)
    pattern_app_count = pattern_app(dtime,org_id)

    id = get_id_by_name("statisticdata")
    if not id:
        pymongo_client.ids.insert({"name": "statisticdata", "id": 0})
        id = get_id_by_name("statisticdata")
    data_counts = {'dev_online_num':dev_online_num_count,'dev_online':dev_online_count,'internet_violations':internet_violations_count,
                   'sen_word10':sen_word10_count,'app_using_len5':app_using_len5_count,'safe_hidden_trouble':safe_hidden_trouble_count,
                   'app_using':app_using_count,'violations_fun':violations_fun_count,'pattern_app':pattern_app_count}
    #判断这一天的数据是否在表中，有则更新，没有则插入
    data_detail = pymongo_client.statistic_mid_data.find_one({'time':dtime,'org_id':org_id},{'_id':0})
    if data_detail:
        data_detail.update({'data_detail':data_counts})
        rtn = pymongo_client.statistic_mid_data.update({'time':dtime,'org_id':org_id},data_detail)
    else:
        data = {'id':id['id'],'time':dtime,'org_id':org_id,'data_detail':data_counts}
        rtn = pymongo_client.statistic_mid_data.insert(data)


#在线设备数
def dev_online_num(datetimes,org_id):
    #获取数据的开始计时时间当天凌晨之后
    start_datetime = datetimes + ' 00:00:00'
    #获取数据的开始计时时间,当天的晚上24点之前
    end_datetime = datetimes + ' 23:59:59'
    online_device_num = pymongo_client.dev.find({"org_id": org_id,'last_online':{'$gt':start_datetime},'login_time':{'$lt':end_datetime}},{'_id':0}).count()
    return online_device_num

#设备在线时长
def dev_online(datetimes,org_id):
    #获取数据的开始计时时间当天凌晨之后
    start_datetime = datetimes + ' 00:00:00'
    #获取数据的开始计时时间,当天的晚上24点之前
    end_datetime = datetimes + ' 23:59:59'
    online_devices = pymongo_client.dev.find({"org_id": org_id,'last_online':{'$gte':start_datetime},'login_time':{'$lt':end_datetime}},{'_id':0})
    dev_online_dict = {}
    for dev in online_devices:
        #上线时间
        login_time = dev['login_time']
        #最后在线时间
        last_online_time = dev['last_online']
        dev_name = dev['dev_name']
        #比较设备上线和离线时间，有些设备是在当天之前上的线或在当天之后下的线
        #此期间一直是登录状态，我将今天之前上线的设备的开始时间设置为凌晨开始计算，下线时间同理
        if login_time < start_datetime:
            login_time = start_datetime
        if last_online_time > end_datetime:
            last_online_time = end_datetime
        #把字符串形式的日期转换为datetime形式并计算
        login_time = datetime.datetime.strptime(login_time,"%Y-%m-%d %H:%M:%S")
        last_online_time = datetime.datetime.strptime(last_online_time,"%Y-%m-%d %H:%M:%S")
        #计算时长，以秒为计算单位，后期如果不合适再改
        online_len = (last_online_time-login_time).seconds
        dev_online_dict['dev_name'] = online_len
    return dev_online_dict

    #上网违规行为
def internet_violations(datetimes,org_id):
    violation_desc = {}
    #获取数据的开始计时时间当天凌晨之后
    start_datetime = datetimes + ' 00:00:00'
    #获取数据的开始计时时间,当天的晚上24点之前
    end_datetime = datetimes + ' 23:59:59'
    url_violation_count = pymongo_client.urlLog.find({'log_type':{"$regex":'^违规URL$'}, 'opt_time':{'$lte':end_datetime, '$gt':start_datetime}, 'org_id': org_id}).count()
    sen_words_count = pymongo_client.senWordLog.find({'opt_time':{'$lte':end_datetime, '$gt':start_datetime}, 'org_id': org_id}).count()
    app_black_count = pymongo_client.clientAppLog.find({'operate':{"$regex":'黑名单'}, 'opt_time':{'$lte':end_datetime, '$gt':start_datetime}, 'org_id': org_id}).count()
    violation_sum = url_violation_count + sen_words_count + app_black_count
    if violation_sum != 0:
        url_percent = "{:.2%}".format(url_violation_count/float(violation_sum))
        sen_word_percent = "{:.2%}".format(sen_words_count/float(violation_sum))
        app_black_percent = "{:.2%}".format(app_black_count/float(violation_sum))
    else:
        url_percent = "0.00%"
        sen_word_percent = "0.00%"
        app_black_percent = "0.00%"
    violation_desc['url_percent'] = url_percent
    violation_desc['sen_word_percent'] = sen_word_percent
    violation_desc['app_black_percent'] = app_black_percent
    return violation_desc

#敏感词TOP10
def sen_word10(datetimes,org_id):
    sen_word_detail = {}
    #获取数据的开始计时时间当天凌晨之后
    start_datetime = datetimes + ' 00:00:00'
    #获取数据的开始计时时间,当天的晚上24点之前
    end_datetime = datetimes + ' 23:59:59'
    sen_words = pymongo_client.senWordLog.find({'opt_time':{'$lt':end_datetime, '$gte':start_datetime}, 'org_id': org_id})
    if sen_words:
        for sen_word in sen_words:
            sensitive_word = sen_word['sensitive_word']
            if sensitive_word not in sen_word_detail.keys():
                sen_word_detail[sensitive_word] = 1
            elif sensitive_word not in sen_word_detail.keys():
                sen_word_detail[sensitive_word] += 1
    sen_word_top10 = sorted(sen_word_detail.items(), key = lambda x:x[1])[:10]
    return sen_word_top10

    #app使用时长TOP5
def app_using_len5(datetimes,org_id):
    app_length_detail = {}
    #获取数据的开始计时时间当天凌晨之后
    start_datetime = datetimes + ' 00:00:00'
    #获取数据的开始计时时间,当天的晚上24点之前
    end_datetime = datetimes + ' 23:59:59'
    app_using_langth_list = pymongo_client.appTimeCount.find({'org_id':org_id,'opt_time':{'$gt':start_datetime},'lastTimeUsed':{'$lt':end_datetime}})
    for app_using_data in app_using_langth_list:
            app_name = app_using_data['appName']
            start_use_time = app_using_data['lastTimeUsed']
            end_use_time = app_using_data['opt_time']
            if start_use_time < start_datetime:
                start_use_time = start_use_time
            if end_use_time > end_datetime:
                end_use_time = end_datetime
            #转成datetime计算
            start_use_time = datetime.datetime.strptime(start_use_time,'%Y-%m-%d %H:%M:%S')
            end_use_time = datetime.datetime.strptime(end_use_time,'%Y-%m-%d %H:%M:%S')
            time_length = ((end_use_time-start_use_time).seconds)/3600
            if app_name not in app_length_detail.keys():
                app_length_detail[app_name] = time_length
            elif app_name in app_length_detail.keys():
                app_length_detail[app_name] += time_length
    app_using_top5 = sorted(app_length_detail.items(),key=lambda x:x[1])[:-6:-1]
    return app_using_top5

#安全隐患
def safe_hidden_trouble(datetimes,org_id):
    #获取数据的开始计时时间当天凌晨之后
    start_datetime = datetimes + ' 00:00:00'
    #获取数据的开始计时时间,当天的晚上24点之前
    end_datetime = datetimes + ' 23:59:59'
    #失联
    dev_out_contact_count = pymongo_client.violationLog.find({'operate': {"$regex": '失联'}, "state": "成功", 'org_id': org_id,'opt_time':{'$lt':end_datetime, '$gte':start_datetime}}).count()
    #擦除
    eliminate_data_count = pymongo_client.dev_log.find({'operate':{"$regex":'擦除企业'}, "state": "成功",'org_id': org_id,'opt_time':{'$lt':end_datetime, '$gte':start_datetime}}).count()
        # 恢复出厂
    reset_factory_count = pymongo_client.dev_log.find({'operate':{"$regex":'恢复出厂'}, "state": "成功", 'org_id': org_id,'opt_time':{'$lt':end_datetime, '$gte':start_datetime}}).count()
    #淘汰
    dev_elimination_count = pymongo_client.dev_log.find({'operate':{"$regex":'设备淘汰'}, "state": "成功", 'org_id': org_id,'opt_time':{'$lt':end_datetime, '$gte':start_datetime}}).count()
    #sim卡变更
    dev_change_sim_count = pymongo_client.violationLog.find({'operate':{"$regex":'SIM卡'}, "state": "成功", 'org_id': org_id,'opt_time':{'$lt':end_datetime, '$gte':start_datetime}}).count()
    #ROOT设备
    dev_root_count = pymongo_client.violationLog.find({'operate':{"$regex":'root'}, "state": "成功", 'org_id': org_id,'opt_time':{'$lt':end_datetime, '$gte':start_datetime}}).count()
    #版本过低
    dev_version_low_count = pymongo_client.violationLog.find({'operate': {"$regex": '版本过低'}, "state": "成功", 'org_id': org_id,'opt_time':{'$lt':end_datetime, '$gte':start_datetime}}).count()
    #敏感词违规
    sen_words_count = pymongo_client.senWordLog.find({'opt_time':{'$lt':end_datetime, '$gte':start_datetime}, 'org_id': org_id}).count()
    safe_hidden_trouble = {'dev_out_contact_count':dev_out_contact_count,'eliminate_data_count':eliminate_data_count+reset_factory_count,
                'dev_elimination_count':dev_elimination_count,'dev_change_sim_count':dev_change_sim_count,
                'dev_root_count':dev_root_count,'dev_version_low_count':dev_version_low_count,'sen_words_count':sen_words_count}
    return safe_hidden_trouble

#app使用次数、app使用流量
def app_using(datetimes,org_id):
    pass

#违规功能
def violations_fun(datetimes,org_id):
    pass

#模式应用详情（按已下发计算）
def pattern_app(datetimes,org_id):
    pass

def get_id_by_name( name):
    db_id = pymongo_client.ids.find_and_modify(query={'name': name}, update={'$inc': {'id': 1}}, new=True, fields={'_id': 0, 'id': 1})
    return db_id


def run():
    scheduler = BackgroundScheduler()
    scheduler.add_job(dataAggregation, 'cron', year='*', month='*', day='*', hour='00', minute='10', second='00',id='data_statistic')
    # scheduler.add_job(dataAggregation, 'cron', year='*', month='*', day='*', hour='*', minute='*', second='*/10',id='data_statistic')
    scheduler.start()

if __name__ == '__main__':
    # pymongo_setting = Settings()
    # self.pymongo_client = PymongoClients(pymongo_setting.MONGOCLIENTS).pymongoClient

    server_options = Settings()
    pymongo_client = PymongoClient(server_options.MONGOCLIENT).pymongoClient

    # statistic_task = dataAggregation()

    run()

    '''
    year (int|str) – 4-digit year
    month (int|str) – month (1-12)
    day (int|str) – day of the (1-31)
    week (int|str) – ISO week (1-53)
    day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    hour (int|str) – hour (0-23)
    minute (int|str) – minute (0-59)
    econd (int|str) – second (0-59)

    start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)尽早(含)开始工作的日期/时间
    end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
    timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations
    用于日期/时间计算的时区(默认为调度程序时区)(defaults to scheduler timezone)

    *    any    Fire on every value
    */a    any    Fire every a values, starting from the minimum
    a-b    any    Fire on any value within the a-b range (a must be smaller than b)
    a-b/c    any    Fire every c values within the a-b range
    xth y    day    Fire on the x -th occurrence of weekday y within the month
    last x    day    Fire on the last occurrence of weekday x within the month
    last    day    Fire on the last day within the month
    x,y,z    any    Fire on any matching expression; can combine any number of any of the above expressions
    '''
    while True:
        time.sleep(10)
        print '------now time------'

