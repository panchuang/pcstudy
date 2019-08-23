# _*_ coding:utf-8 _*_
__author__ = 'pan'

import datetime

MINUTES = 60
#违规功能的关键词
VIOLATION_FUN = ['摇一摇','转账','红包','附近的人','电话','短信','相机','位置']
#安全隐患的关键词safe_hidden_trouble
SAFE_HIDDEN_TROUBLE = {'eliminate':'擦除企业','reset_factory':'恢复出厂','elimination':'设备淘汰',
                       'change_sim':'SIM卡','root':'root','version_low':'版本过低',
                       'out_contact':'失联'}
#上网违规行为关键字
VIOLATION_WEB = {'url':'^违规URL$','app_black':'黑名单'}

STATISTIC_DATA_TYPE = ['dev_online_num','dev_online_len','internet_violations',
                       'sen_word10','app_using','violations_fun','app_using_len5',
                       'safe_hidden_trouble','pattern_app']

class QueryBasic():
    def __init__(self,datetimes,org_id,pymongo_client):
        #获取数据的开始计时时间当天凌晨之后
        self.start_datetime = datetimes + ' 00:00:00'
        #获取数据的开始计时时间,当天的晚上24点之前
        self.end_datetime = datetimes + ' 23:59:59'
        self.pymongo_client = pymongo_client
        self.org_id = org_id

    #在线设备数
    def dev_online_num(self):
        try:
            online_device_num = self.pymongo_client.dev.find({"org_id": self.org_id,'last_online':{'$gt':self.start_datetime},'login_time':{'$lt':self.end_datetime}},{'_id':0}).count()
        except Exception as e:
            online_device_num = ''
        return online_device_num

    #设备在线时长
    def dev_online(self):
        try:
            online_devices = self.pymongo_client.dev.find({"org_id": self.org_id,'last_online':{'$gte':self.start_datetime},'login_time':{'$lt':self.end_datetime}},{'_id':0})
            dev_online_dict = {}
            for dev in online_devices:
                #上线时间
                login_time = dev['login_time']
                #最后在线时间
                last_online_time = dev['last_online']
                dev_name = dev['dev_name']
                #比较设备上线和离线时间，有些设备是在当天之前上的线或在当天之后下的线
                #此期间一直是登录状态，我将今天之前上线的设备的开始时间设置为凌晨开始计算，下线时间同理
                if login_time < self.start_datetime:
                    login_time = self.start_datetime
                if last_online_time > self.end_datetime:
                    last_online_time = self.end_datetime
                #把字符串形式的日期转换为datetime形式并计算
                login_time = datetime.datetime.strptime(login_time,"%Y-%m-%d %H:%M:%S")
                last_online_time = datetime.datetime.strptime(last_online_time,"%Y-%m-%d %H:%M:%S")
                #计算时长，以秒为计算单位，后期如果不合适再改
                online_len = (last_online_time-login_time).seconds
                dev_online_dict['dev_name'] = online_len
        except Exception as e:
            dev_online_dict = ''

        return dev_online_dict

    #上网违规行为
    def internet_violations(self):
        try:
            violation_desc = {}
            url_violation_count = self.pymongo_client.urlLog.find({'log_type':{"$regex":VIOLATION_WEB['url']}, 'opt_time':{'$lte':self.end_datetime, '$gt':self.start_datetime}, 'org_id': self.org_id}).count()
            sen_words_count = self.pymongo_client.senWordLog.find({'opt_time':{'$lte':self.end_datetime, '$gt':self.start_datetime}, 'org_id': self.org_id}).count()
            app_black_count = self.pymongo_client.clientAppLog.find({'operate':{"$regex":VIOLATION_WEB['app_black']}, 'opt_time':{'$lte':self.end_datetime, '$gt':self.start_datetime}, 'org_id': self.org_id}).count()
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
        except Exception as e:
            violation_desc = ''

        return violation_desc

    #敏感词TOP10
    def sen_word10(self):
        try:
            sen_word_detail = {}
            sen_words = self.pymongo_client.senWordLog.find({'opt_time':{'$lt':self.end_datetime, '$gte':self.start_datetime}, 'org_id': self.org_id})
            if sen_words:
                for sen_word in sen_words:
                    sensitive_word = sen_word['sensitive_word']
                    if sensitive_word not in sen_word_detail.keys():
                        sen_word_detail[sensitive_word] = 1
                    elif sensitive_word not in sen_word_detail.keys():
                        sen_word_detail[sensitive_word] += 1
            sen_word_top10 = sorted(sen_word_detail.items(), key = lambda x:x[1])[:10]
        except Exception as e:
            sen_word_top10 = ''

        return sen_word_top10

    #app使用时长TOP5
    def app_using_len5(self):
        app_length_detail = {}
        try:
            app_using_langth_list = self.pymongo_client.appTimeCount.find({'org_id':self.org_id,'opt_time':{'$gt':self.start_datetime},'lastTimeUsed':{'$lt':self.end_datetime}})

            for app_using_data in app_using_langth_list:
                app_name = app_using_data['appName']
                app_time = app_using_data['app_time']
                if app_name in app_length_detail.keys():
                    app_length_detail[app_name] += app_time
                else:
                    app_length_detail[app_name] = app_time

            app_using_top5 = sorted(app_length_detail.items(),key=lambda x:x[1])[:-6:-1]
        except Exception as e:
            app_using_top5 = ''

        return app_using_top5

    #安全隐患
    def safe_hidden_trouble(self):
        try:
            #失联
            dev_out_contact_count = self.pymongo_client.dev.find({'out_of_contact':1,'org_id':self.org_id,'dev_loss_time':{'$gt':self.start_datetime,'$lte':self.end_datetime}}).count()

            #擦除
            eliminate_data_count = self.pymongo_client.dev_log.find({'operate':{"$regex":SAFE_HIDDEN_TROUBLE['eliminate']}, "state": "成功",'org_id': self.org_id,'opt_time':{'$lt':self.end_datetime, '$gte':self.start_datetime}}).count()
                # 恢复出厂
            reset_factory_count = self.pymongo_client.dev_log.find({'operate':{"$regex":SAFE_HIDDEN_TROUBLE['reset_factory']}, "state": "成功", 'org_id': self.org_id,'opt_time':{'$lt':self.end_datetime, '$gte':self.start_datetime}}).count()

            #淘汰
            dev_elimination_count = self.pymongo_client.dev_log.find({'operate':{"$regex":SAFE_HIDDEN_TROUBLE['elimination']}, "state": "成功", 'org_id': self.org_id,'opt_time':{'$lt':self.end_datetime, '$gte':self.start_datetime}}).count()

            #sim卡变更
            dev_change_sim_count = self.pymongo_client.violationLog.find({'operate':{"$regex":SAFE_HIDDEN_TROUBLE['change_sim']}, "state": "成功", 'org_id': self.org_id,'opt_time':{'$lt':self.end_datetime, '$gte':self.start_datetime}}).count()

            #ROOT设备
            dev_root_count = self.pymongo_client.violationLog.find({'operate':{"$regex":SAFE_HIDDEN_TROUBLE['root']}, "state": "成功", 'org_id': self.org_id,'opt_time':{'$lt':self.end_datetime, '$gte':self.start_datetime}}).count()

            #版本过低
            dev_version_low_count = self.pymongo_client.violationLog.find({'operate': {"$regex": SAFE_HIDDEN_TROUBLE['version_low']}, "state": "成功", 'org_id': self.org_id,'opt_time':{'$lt':self.end_datetime, '$gte':self.start_datetime}}).count()

            #敏感词违规
            sen_words_count = self.pymongo_client.senWordLog.find({'opt_time':{'$lt':self.end_datetime, '$gte':self.start_datetime}, 'org_id': self.org_id}).count()
            safe_hidden_trouble = {'dev_out_contact_count':dev_out_contact_count,'eliminate_data_count':eliminate_data_count+reset_factory_count,
                        'dev_elimination_count':dev_elimination_count,'dev_change_sim_count':dev_change_sim_count,
                        'dev_root_count':dev_root_count,'dev_version_low_count':dev_version_low_count,'sen_words_count':sen_words_count}
        except Exception as e:
            safe_hidden_trouble = ''


        return safe_hidden_trouble

    #app使用次数、app使用流量
    def app_using(self):
        pass

    #违规功能
    def violations_fun(self):
        pass

    #模式应用详情（按已下发计算）
    def pattern_app(self):
        try:
            org_user = self.pymongo_client.user.find({"available": 1, "org_id": self.org_id},{"_id":0})
            org_user_id = [user['id'] for user in org_user]
            pattern_detail_list = self.pymongo_client.user_pattern.find({'uid':{'$in':org_user_id},'issue_time':{'$gte':self.start_datetime,'$lt':self.end_datetime}},{'_id':0})
            pattern_detail_list = [pattern for pattern in pattern_detail_list]
        except Exception as e:
            pattern_detail_list = ''
            #

        return pattern_detail_list