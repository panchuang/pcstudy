# _*_ coding:utf-8 _*_
__author__ = 'pan'
import pymongo

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


if __name__ == '__main__':
    server_options = Settings()
    pymongo_client = PymongoClient(server_options.MONGOCLIENT).pymongoClient
    # a = pymongo_client.organization.find({"parentid":75})
    # a = pymongo_client.dev.find({"org_id":224},{'_id':0})
    # for i in a:
    #
    #     # print i['update_time']
    #     print i

    # a = {'id':001,
    #      'org_id':75,
    #      'data_detail':{},
    #      'time':'2019-08-13 11:11:11',
    #      }
    # result = pymongo_client.statistic_mid_data.update({'id':001},a)
    # print result


    # a = pymongo_client.ids.find_and_modify(query={'name': 'pattern'}, update={'$inc': {'id': 1}}, new=True, fields={'_id': 0, 'id': 1})
    # a = pymongo_client.ids.find_one({'name': 'pattern'})
    # print(a)
    # {u'_id': ObjectId('5ce61218421aa93ccd9fc956'), u'name': u'pattern', u'id': 208}
    # a = {'name':'statisticdata','id':1}
    # pymongo_client.ids.insert(a)

