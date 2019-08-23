# _*_ coding:utf-8 _*_
__author__ = 'pan'

import datetime
from QueryBasic import STATISTIC_DATA_TYPE,QueryBasic



class GetDataByType():
    def __init__(self,tm_type,dt_type,org_id,pymongo):
        self.tm_type = tm_type
        self.dt_type = dt_type
        self.org_id = org_id
        self.pymongo_client = pymongo
        self.result = {}

    def getDataByType(self):
        start_time,end_time,time_list = getDays(int(self.tm_type))

        try:
            calbac = [self.getData(datetimes) for datetimes in time_list]
        except Exception as e:
            self.result = ""
            # logger.exception('ERROR:',exc_info=True)

        return self.result

    def getData(self,datetimes):
        mid_data_details = self.pymongo_client.statistic_mid_data.find_one({'time':datetimes,'org_id':self.org_id},{'_id':0})
        update_mid_data = UpdateMidData(self.dt_type,datetimes,self.org_id,self.pymongo_client)
        data = update_mid_data.data
        if mid_data_details:
            data_detail = mid_data_details['data_detail']
            if self.dt_type in data_detail.keys():
                self.result[datetimes] = data_detail[self.dt_type]
            else:
                update = update_mid_data.data_update(mid_data_details)
                self.result[datetimes] = data
        else:
            insert = update_mid_data.data_insert(mid_data_details)
            self.result[datetimes] = data


class SaveDataBasic():#如何减少if语句
    def __init__(self,dt_type,datetimes,org_id,pymongo_client):
        self.dt_type = dt_type
        self.datetimes = datetimes
        self.org_id = org_id
        self.pymongo_client = pymongo_client
        self.query_basic = QueryBasic(self.datetimes,self.org_id,self.pymongo_client)


        if dt_type == STATISTIC_DATA_TYPE[0]:
            self.data = self.query_basic.dev_online_num()
        elif dt_type == STATISTIC_DATA_TYPE[1]:
            self.data = self.query_basic.dev_online()
        elif dt_type == STATISTIC_DATA_TYPE[2]:
            self.data = self.query_basic.internet_violations()
        elif dt_type == STATISTIC_DATA_TYPE[3]:
            self.data = self.query_basic.sen_word10()
        elif dt_type == STATISTIC_DATA_TYPE[4]:
            self.data = '---->Data not included yet<----'
        elif dt_type == STATISTIC_DATA_TYPE[5]:
            self.data = '---->Data not included yet<----'
        elif dt_type == STATISTIC_DATA_TYPE[6]:
            self.data = self.query_basic.app_using_len5()
        elif dt_type == STATISTIC_DATA_TYPE[7]:
            self.data = self.query_basic.safe_hidden_trouble()
        elif dt_type == STATISTIC_DATA_TYPE[8]:
            self.data = self.query_basic.pattern_app()
        else:
            self.data = '---->dt_type error!<----'

class UpdateMidData(SaveDataBasic):
    def data_update(self,mid_data_details):
        #数据保存到中间表中
        mid_data_details['data_detail'].update({self.dt_type:self.data})
        rtn = self.pymongo_client.statistic_mid_data.update({'time':self.datetimes,'org_id':self.org_id},mid_data_details)

    def data_insert(self,mid_data_details):
        id = get_id_by_name("statisticdata",self.pymongo_client)
        if not id:
            self.pymongo_client.ids.insert({"name": "statisticdata", "id": 0})
            id = get_id_by_name("statisticdata",self.pymongo_client)
        mid_data_details = {'id':id['id'],'time':self.datetimes,'org_id':self.org_id,'data_detail':{'dev_online_num':self.data}}
        rtn = self.pymongo_client.statistic_mid_data.insert(mid_data_details)


def get_id_by_name(name,pymongo_client):
    db_id = pymongo_client.ids.find_and_modify(query={'name': name}, update={'$inc': {'id': 1}}, new=True, fields={'_id': 0, 'id': 1})
    return db_id


def getDays(sdays):
    time_list = []
    today = datetime.datetime.now()
    if sdays == 0:
        days = today-datetime.timedelta(days=sdays)
        end_time = today.strftime('%Y-%m-%d %H:%M:%S')
    else:
        days = today-datetime.timedelta(days=sdays)
        end_time = today.strftime('%Y-%m-%d') + ' 00:00:00'
    start_time = days.strftime('%Y-%m-%d') + ' 00:00:00'

    for i in range(sdays):
        time = (days+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        time_list.append(time)

    return start_time, end_time,time_list
