# _*_ coding:utf-8 _*_
__author__ = 'pan'

import datetime
import time

# a = 3
# b = 10
# c = b/float(a)
# f = round(c,3)
# print(c)
# print(type(c))
# print(f)
# print(type(f))

# now_time = datetime.datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")
# oneday = now_time-datetime.timedelta(days=1)
# print(now_time)
# print(oneday)

# times1 = "2019-07-24 10:00:23"
# times2 = "2019-07-25 18:27:23"
# times1 = datetime.datetime.strptime(times1,"%Y-%m-%d %H:%M:%S")
# times2 = datetime.datetime.strptime(times2,"%Y-%m-%d %H:%M:%S")
# time1 = datetime.datetime(times1[0],times1[1],times1[2],times1[3],times1[4],times1[5])
# time2 = datetime.datetime(times2[0],times2[1],times2[2],times2[3],times2[4],times2[5])
# timea = time2-time1.days
# timeb = time2-time1
# print(timea)
# print(timeb)
# print((times2-times1).days)
# c = (times2-times1).seconds
# print c
# print(c/float(3600))
# if times1 < times2:
#     print('true')
# elif times1 >= times2:
#     print('false')
# a = {'a':1,'b':5,'c':2}
# print(a)
# s = sorted(a.items(), key = lambda x:x[1])
# print(s)


# time = datetime.datetime.now().strftime('%Y-%m-%d')
# print(time)

# time = "2019-07-24 10:00:23"
# tm = time.split(' ')[0]
# print(tm)
#
#
# ﻿{'last_online':{'$gt':'2019-08-06 00:00:00'},'login_time':{'$lt':'2019-08-13 00:00:00'}, "org_id": 76}

# for i in range(3+1):
#     print(i)

# start_time,end_time = "2019-06-01 18:27:23","2019-08-09 18:27:23"
# dicta = {"2019-07-23": 1,
#       "2019-07-18": 2,
#       "2019-07-19": 2,
#       "2019-07-22": 1,
#       "2019-07-12": 0,
#       "2019-07-13": 0,
#       "2019-07-10": 0,}
# dictb = sorted(dicta.items(),key = lambda x:x[1])
# print(dictb)

# a = 3
# b = 5
#
# arra = ['1','2','3','4','5','6',['1','2']]
#
# for i in arra:
#     if i == ['1','2']:
#         a = arra.index(i)
#         arrb = arra.pop(a)
#
# print(arrb)

# org_id =75
#
# a = [
#     {u'topic': u'10167\u90e8\u961f\u603b\u90e8', u'id': 75},
#     {u'topic': u'3\u533a', u'id': 184},
#     {u'topic': u'1\u533a', u'id': 166},
#     {u'topic': u'2\u533a', u'id': 175},
#     {u'topic': u'4\u533a', u'id': 186},
#     {u'topic': u'secspace', u'id': 224},
#     {u'topic': u'testing', u'id': 225}]
#
# area_dev_sum_dict = {}
# for org_info in a:
#     print org_info
#     id = org_info['id']
#     # try:
#     #     child_dev_num = yield self.base_db.dev.find({'org_id':id}).count()
#     # except:
#     #     child_dev_num = 0
#     # if id == org_id:
#     #     index = a.index(org_info)
#     #     print index
#     #     this_org_info = a.pop(index)
#
# this_org_info = [a.pop(a.index(i)) for i in a if i['id'] == org_id]
# area_dev_sum_dict['this_org'] = this_org_info
# area_dev_sum_dict['child_org'] = a
#
# print(area_dev_sum_dict)

# def a():
#     b = 'aaaaaa'
#     return b


# a = '2019-08-15 12:04:19'
# b = '2019-08-14 11:05:19'
# c = b-a
# print c

# timea = time.time()
# num = "{:.2%}".format(35/float(111))
# # num = 3/float(11)
# timeb = time.time()
# time = (timeb-timea)#.microsecond
#
# print 'num:----->',num
# print 'time:----->',time

# print datetime.date.today()
# print datetime.date.today()-datetime.timedelta(days=1)

# def a():
#     print 'aaaaaa'
#
# def b():
#     c = a()
#
# b =b()

arra = ['a','b','c']
online_dev_sum_dict = {}.fromkeys(arra,0)
print online_dev_sum_dict