# _*_ coding:utf-8 _*_
__author__ = 'pan'


from project.BaseHandler import BaseHandler
import sys
import logging
import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.web
from tornado.options import options, define
import pymongo
import datetime
import logging
from project.QueryBasic import STATISTIC_DATA_TYPE
from project.GetDataByType import GetDataByType


define("port", default=8080, help="Tornado Server", type=int, metavar="none")



class Settings:
    DEBUG = False
    MONGOCLIENT = {
        "host": "127.0.0.1",
        "port": 27017,
        "db": "rom_private"
    }

class PymongoClient:
    def __init__(self, server_options):
        self.dbName = server_options.pop('db')
        # database in mongodb
        self.pymongoClient = pymongo.MongoClient(**server_options)[self.dbName]

    def create_id(self, name):
        self.pymongoClient.ids.ensure_index('name', unique=True)
        self.pymongoClient.ids.save({'name': name, 'id': 0})






class GetStatisticalDynamicData(BaseHandler):
    def get(self):
        try:
            pymongo_setting = Settings()
            self.pymongo_client = PymongoClient(pymongo_setting.MONGOCLIENT).pymongoClient
            request_param = self.get_and_check_params(['org_id','time_type','data_type'])
            org_id = request_param.getAsInt('org_id')
            time_type = request_param.getAsString('time_type')
            data_type = request_param.getAsString('data_type')
            get_data_by_type = GetDataByType(time_type,data_type,org_id,self.pymongo_client)
            #获取当前机构的机构信息和下级机构的机构id等简略信息
            org_infos = {}
            this_org_info = yield self.base_db.organization.find_one({'id':org_id},{'_id':0})
            if this_org_info:
                child_org_infos = yield self.base_db.organization.find({'parentid':org_id},{'_id':0,'id':1,'longitude':1,'latitude':1,'topic':1}).to_list(10000)
                org_infos['this_org'] = this_org_info
                org_infos['child_org'] = child_org_infos

                if data_type in STATISTIC_DATA_TYPE:
                    data = get_data_by_type.getDataByType()
                else:
                    data = '---->dt_type error!<----'

                result = {'org_infos':org_infos,data_type:data}
            else:
                result = None
                 
        except Exception as e:
            result = ""
            #
              
            #
        self.write(dict(doc=result))








if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    tornado.options.parse_command_line()
    application = tornado.web.Application(
        handlers=[(r'/',Test),]
    )
    http_server = tornado.httpserver.HTTPServer(application,xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()