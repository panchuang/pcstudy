# -*- coding: utf-8 -*-

import os
import pymongo
import logging
import time
import uuid
import datetime
import copy
import json
import fcntl
import subprocess

from bson.son import SON
from utils.getDateTime import getdays

from utils.formatChange import password
from api.license.license import executeValidTimeTask
from config import config, settings
from utils.send_mail import send_mail
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.memory import MemoryJobStore

host = settings.Settings.MONGOCLIENT.get("host")
# scheduler = None

#
#
# def task(in_fence, out_fence, start_time, stop_time, policy_id, repeat_type, weekday, policy_type, regid_list):
#     start = start_time.split(":")
#     stop = stop_time.split(":")
#     params_in = (in_fence, regid_list, policy_type, policy_id)
#     params_out = (out_fence, regid_list, policy_type, policy_id)
#     try:
#         if repeat_type == "1":
#             if weekday == "":
#                 raise ecode.IPUTERROR
#             week = {"1": "mon", "2": "tue", "3": "wed", "4": "thu", "5": "fri", "6": "sat", "7": "sun"}
#             scheduler.add_job(send, "cron", day_of_week=week[weekday], hour=start[0], minute=start[1], second=start[2], args=params_in, id=str(policy_id) + "_" + policy_type + "_start", jobstore="mongo")
#             scheduler.add_job(send, "cron", day_of_week=week[weekday], hour=stop[0], minute=stop[1], second=stop[2], args=params_out, id=str(policy_id) + "_" + policy_type + "_stop", jobstore="mongo")
#         elif repeat_type == "2" or repeat_type == "4":
#             scheduler.add_job(send, "cron", day="*", month="*", hour=start[0], minute=start[1], second=start[2], args=params_in, id=str(policy_id) + "_" + policy_type + "_start", jobstore="mongo")
#             scheduler.add_job(send, "cron", day="*", month="*", hour=stop[0], minute=stop[1], second=stop[2], args=params_out, id=str(policy_id) + "_" + policy_type + "_stop", jobstore="mongo")
#         elif repeat_type == "3":
#             scheduler.add_job(send, "cron", day="*", month="*", day_of_week="mon-fri", hour=start[0], minute=start[1], second=start[2], args=params_in, id=str(policy_id) + "_" + policy_type + "_start", jobstore="mongo")
#             scheduler.add_job(send, "cron", day="*", month="*", day_of_week="mon-fri", hour=stop[0], minute=stop[1], second=stop[2], args=params_out, id=str(policy_id) + "_" + policy_type + "_stop", jobstore="mongo")
#         else:
#             raise ecode.TIMING_TASK_CREATE_FAILED
#     except Exception as e:
#         logging.exception("error %s" % e)
#         raise e
#
#
# def send(fence_info, regid_list, policy_type, policy_id):
#     try:
#         send_info = {}
#         if policy_type == "timefence":
#             send_info["timefence"] = policy_id
#         elif policy_type == "limitaccess":
#             if fence_info > 0:
#                 send_info["limitaccess"] = abs(fence_info)
#                 send_info["execute"] = 1
#             else:
#                 send_info["limitaccess"] = abs(fence_info)
#                 send_info["execute"] = 0
#         push.send(send_info, regid_list)
#     except Exception as e:
#         raise e
#
#
# def add_task(sched, policy_id, policy_type, regid_list):
#     in_fence = 0
#     out_fence = 0
#     global scheduler
#     scheduler = sched
#     try:
#         mongoClient = pymongo.MongoClient(host=host, port=27017)
#         if policy_type == "timefence":
#             policyInfo = mongoClient["rom_private"].fence_policy.find_one({"id": policy_id, "available": 1})
#             in_fence = policyInfo["in_fence"]
#             out_fence = policyInfo["out_fence"]
#         elif policy_type == "limitaccess":
#             policyInfo = mongoClient["rom_private"].app_policy.find_one({"id": policy_id, "available": 1})
#             in_fence = policy_id
#             out_fence = -policy_id
#         logging.warning(policyInfo)
#         mongoClient.close()
#         if policyInfo["time_limit"]:
#             repeat_type = policyInfo["time_limit"]["repeat_type"]
#             start_date = policyInfo["time_limit"]["start_date"]
#             stop_date = policyInfo["time_limit"]["stop_date"]
#             start_time = policyInfo["time_limit"]["start_time"]
#             stop_time = policyInfo["time_limit"]["stop_time"]
#             weekday = policyInfo["time_limit"].get("weekday", "")
#             now_date = time.strftime("%Y-%m-%d")
#             exec_time = None
#             if start_date <= stop_date:
#                 if start_date <= now_date < stop_date:
#                     new_time = time.time() + 1
#                     dt = time.localtime(new_time)
#                     now_time = time.strftime("%Y-%m-%d %H:%M:%S", dt)
#                     exec_time = now_time
#                 elif start_date > now_date:
#                     exec_time = start_date
#                 elif stop_date < now_date:
#                     raise ecode.CLOSEDATE_FAILED
#                 scheduler.add_job(task, 'date', run_date=exec_time, args=(
#                     in_fence, out_fence, start_time, stop_time, int(policyInfo["id"]), repeat_type, weekday, policy_type,
#                     regid_list), id=str(policy_id) + "_" + policy_type + "_begin", jobstore="mongo")
#                 scheduler.add_job(remove_task, 'date', run_date=stop_date + " 23:59:59", args=(int(policyInfo["id"]), policy_type), id=str(policy_id) + "_" + policy_type + "_end", jobstore="mongo")
#                 return ecode.OK
#             else:
#                 raise ecode.TIMEFENCE_FAILED
#         else:
#             return ecode.OK
#     except Exception as e:
#         logging.exception("error %s" % e)
#         raise e
#
#
# def remove_task(policy_id, policy_type, sched=scheduler):
#     if sched:
#         task_list = sched.get_jobs()
#         task_ids = [task_obj.id for task_obj in task_list]
#         logging.warning("jobs_ids before remove = %s" % task_ids)
#         if str(policy_id) + "_" + policy_type + "_start" in task_ids:
#             sched.remove_job(str(policy_id) + "_" + policy_type + "_start")
#         if str(policy_id) + "_" + policy_type + "_stop" in task_ids:
#             sched.remove_job(str(policy_id) + "_" + policy_type + "_stop")
#         if str(policy_id) + "_" + policy_type + "_end" in task_ids:
#             sched.remove_job(str(policy_id) + "_" + policy_type + "_end")
#         if str(policy_id) + "_" + policy_type + "_begin" in task_ids:
#             sched.remove_job(str(policy_id) + "_" + policy_type + "_begin")
#         logging.warning("jobs_list After remove = %s" % sched.get_jobs())
#     else:
#         id_start = str(policy_id) + "_" + policy_type
#         data = {"_id": {"$in": [id_start + "_start", id_start + "_stop", id_start + "_begin"]}}
#         mongoClient = pymongo.MongoClient(host=host, port=27017)
#         mongoClient["rom_private"].job.remove(data)
#         mongoClient.close()


def begin(port, result, cacheDB, fileCache, confPath):
    """
    Create Timing Object
    """
    log = logging.getLogger('apscheduler.executors.default')
    log.setLevel(logging.INFO)
    fh = logging.FileHandler("/opt/test.logs")
    fh.setLevel(logging.INFO)
    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    fh.setFormatter(fmt)
    log.addHandler(fh)

    # mongo
    jobclient = pymongo.MongoClient(host=host, port=27017)
    job_defaults = {'coalesce': False, 'max_instances': 3}
    jobstores = {
        'mongo': MongoDBJobStore(collection='job', database='rom_private', client=jobclient)
    }
    executors = {'default': ThreadPoolExecutor(20), 'processpool': ProcessPoolExecutor(5)}
    # try:
    #     scheduler = BackgroundScheduler(executors=executors, jobstores=jobstores, job_defaults=job_defaults)
    #     scheduler.start()
    #     return scheduler

    # fp = open('scheduler.lock', 'wb')
    try:
        # fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if port != 7770:
            raise
        scheduler = BackgroundScheduler(executors=executors, jobstores=jobstores, job_defaults=job_defaults)
        scheduler.start()
        # fcntl.flock(fp, fcntl.LOCK_UN)
        # fp.close()
        # 创建定时任务
        control = result["license"]["product"]["validTime"]["Control"]
        if control == "ON":
            if not scheduler.get_job(job_id="ValidTimeTask"):
                scheduler.add_job(executeValidTimeTask, "cron", day_of_week='0-7', hour=3, minute=00, second=00, args=(result, cacheDB), id="ValidTimeTask")
                logging.warning(scheduler.get_job(job_id='ValidTimeTask'))

            if not scheduler.get_job(job_id="Statisticsjob"):
                # scheduler.add_job(func=execute_data_statistics_job, trigger="cron", hour=23, minute=00, second=00, args=(result, cacheDB), id="Statisticsjob")
                #上面为每天23:00跑的正常语句，下面为每10秒钟跑的测试语句
                logging.warning("-------------------开始定时任务------------------")
                scheduler.add_job(func=execute_data_statistics_job, trigger="cron", hour=23, minute=00, second=00,args=(result, cacheDB), id="Statisticsjob")
                # scheduler.add_job(func=execute_data_statistics_job, trigger="cron", second="*/5", args=(result, cacheDB), id="Statisticsjob")
                logging.warning("-------------------结束定时任务------------------")
                #------------------------------------------------------------
                logging.warning(scheduler.get_job(job_id='Statisticsjob'))
        # 配置文件刷新任务
        confFlushTask(fileCache, confPath)
        if not scheduler.get_job(job_id="ConfFlush"):
            scheduler.add_job(confFlushTask, "cron", minute="*/5", args=(fileCache, confPath), id="ConfFlush")
            logging.warning(scheduler.get_job(job_id='ConfFlush'))
        return scheduler
    except Exception as e:
        pass


def confFlushTask(fileCache, path):
    try:
        vals = fileCache.redis.keys("conf*")
        if vals:
            fileCache.redis.delete(*vals)
        cmd = "ls"
        cur_dir = subprocess.Popen(args=cmd, cwd=path, stdout=subprocess.PIPE, shell=True).communicate()[0]
        cur_dir_list = [x for x in cur_dir.split("\n") if x and x != "root"]
        for per in cur_dir_list:
            per_dir_file = subprocess.Popen(args=cmd, cwd=path + per, stdout=subprocess.PIPE, shell=True).communicate()[0]
            per_dir_file = [x for x in per_dir_file.split("\n") if x]
            for per_dir in per_dir_file:
                file_path = os.path.join(path, per, per_dir)
                # file_name = password(per_dir)
                chk_file_cmd = "if [ -f " + per_dir + " ];then echo 'file';elif [ -d " + per_dir + " ];then echo 'directory';else echo 'file';fi"
                chk_file = subprocess.Popen(args=chk_file_cmd, cwd=path + per, stdout=subprocess.PIPE, shell=True).communicate()[0]
                chk_file = [x for x in chk_file.split("\n") if x]
                if len(chk_file) == 1 and chk_file[0] == "file":
                    file_name = password(per_dir)
                    with open(file_path, "rb") as file_content:
                        content = file_content.read()
                        hash_cont = password(content)
                        fileCache.redis.hset("conf" + per, file_name, {"hashcode": hash_cont, "content": content})
                elif len(chk_file) == 1 and chk_file[0] == "directory" and per_dir == "smsconf":
                    dir = subprocess.Popen(args="ls", cwd=file_path, stdout=subprocess.PIPE, shell=True).communicate()[0]
                    dir_list = [x for x in dir.split("\n") if x]
                    file_path = os.path.join(path, per, per_dir, dir_list[0])
                    with open(file_path, "rb") as file_content:
                        fileCache.redis.hset("conf" + per, dir_list[0], file_content.read())
    except Exception as e:
        pass


def addLostDevTask(sched):
    """
    Timing Task：LostDev
    """
    sched.add_job(executeLostDevTask, "cron", day_of_week='0-7', hour=0, minute=0, second=0, id="LostDevTask", jobstore="mongo")


def executeLostDevTask():
    """
    Execute Timing Task：LostDev
    """
    lost_dev = []
    lost_dev_set = []
    lost_pol_id_tmp = []
    content = ""
    admin = config.adminInfo()
    mongoClient = pymongo.MongoClient(host=host, port=27017)
    db = mongoClient["rom_private"]
    com_info = list(db.user_policy.find({"policy_type": "complicance", "status": 1}, {"_id": 0, "status": 0, "id": 0, "policy_type": 0}))
    policy_ids = list(set([int(per["policy_id"]) for per in com_info]))
    # 剔除合规项不是失联的策略
    for per_pol_id in policy_ids:
        policy_info = db.policy.find_one({"id": per_pol_id, "available": 1})
        if int(policy_info["complicance_item"]["lost_contact"]) == 1:
            lost_pol_id_tmp.append(per_pol_id)
    com_info = filter(lambda x: x["policy_id"] in lost_pol_id_tmp, com_info)
    if com_info:
        policy_info = None
        for info_tmp in com_info:
            if not policy_info or int(policy_info["id"]) != int(info_tmp["policy_id"]):
                policy_info = db.policy.find_one({"id": int(info_tmp["policy_id"]), "available": 1})
            lost_day = int(policy_info["complicance_item"]["lost_day"])
            # 在线设备
            dev_info = list(db.dev.find({"uid": int(info_tmp["uid"]), "online": 0}, {"_id": 0, "uid": 1, "dev_id": 1, "dev_name": 1, "last_online": 1}))
            for dev in dev_info:
                now = datetime.datetime.now()
                delta = datetime.timedelta(days=lost_day)
                n_days = (now - delta).strftime('%Y-%m-%d %H:%M:%S')
                if dev["last_online"] < n_days:
                    lost_dev.append(dev)
        for i in lost_dev:
            if i not in lost_dev_set:
                lost_dev_set.append(i)
        logging.warning("lost_dev_set = %s" % lost_dev_set)
        if lost_dev_set:
            for lost_dev_info in lost_dev_set:
                user_info = db.user.find_one({"id": int(lost_dev_info.get('uid')), "available": 1}, {"_id": 0, "account": 1, "name": 1})
                day = datetime.datetime.now() - datetime.datetime.strptime(lost_dev_info.get('last_online'), "%Y-%m-%d %H:%M:%S")
                day = day.days
                content += "<tr><td>" + lost_dev_info.get('dev_name') + "</td><td>" + user_info["account"] + "</td><td>"\
                           + lost_dev_info.get('last_online') + "</td><td>" + str(day) + "</td></tr>"
                # log
                m = {"_id": uuid.uuid1().hex, "account": user_info["account"], "opt_time": time.strftime('%Y-%m-%d %X'),
                     "client_ip": "", "dev_name": lost_dev_info.get('dev_name'), "state": str(day) + "天",
                     "operate": "设备失联", "user_name": user_info["name"].encode("utf8"), "log_type": "违规行为"}
                db.violationLog.insert(m)
                # log
            send_mail([admin.get("manager_email")], "【" + admin.get("company_short") + "】设备失联告警",
                      "<html><body><h4>管理员&nbsp;:&nbsp;您好!</h4></p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                      "经系统检测，如下设备已标识为失联：<p><b><table border='1'><tr><th>设备名称</th><th>登陆用户</th><th>"
                      "离线时间</th><th>失联天数</th></tr>%s</b></body></html>" % content.encode("utf8"))
    mongoClient.close()


def addFailureStrategyTask(sched):
    """
    定时任务：未生效策略
    """
    sched.add_job(executeFailureStrategyTask, "cron", day_of_week='0-7', hour=1, minute=0, second=0, id="FailureStrategy", jobstore="mongo")


def executeFailureStrategyTask():
    """
    执行定时任务: 未生效策略
    """
    _device = []
    _complicance = []
    _fence = []
    _application = []
    _username = ""
    _admin = config.adminInfo()
    _policy_type = {"device": _device, "complicance": _complicance, "fence": _fence, "application": _application}
    content = ""
    data = []
    try:
        mongoClient = pymongo.MongoClient(host=host, port=27017)
        db = mongoClient["rom_private"]
        com_info = list(db.user_policy.find({"policy_type": "complicance", "status": 1}, {"_id": 0, "status": 0, "id": 0, "policy_type": 0}))
        com_info_tmp = copy.deepcopy(com_info)
        # 剔除合规项不是策略未生效的策略
        for info in com_info:
            policy_info = db.policy.find_one({"id": int(info["policy_id"]), "available": 1})
            if int(policy_info["complicance_item"]["strategy"]) != 1:
                com_info_tmp.remove(info)
        if com_info_tmp:
            users = list(set([info["uid"] for info in com_info_tmp]))
            # 未生效的所有策略
            no_execute_strategy = list(db.user_policy.find({"uid": {"$in": users}, "status": 0}, {"_id": 0, "uid": 1, "policy_type": 1, "policy_id": 1}))
            for strategy in no_execute_strategy:
                uid = strategy.get("uid")
                user_info = db.user.find_one({"id": uid}, {"_id": 0, "account": 1, "name": 1})
                tmp = {}
                policy_info = db.policy.find_one({"id": strategy.get("policy_id")}, {"_id": 0, "name": 1})
                tmp["policy_type"] = policy_info["policy_type"]
                tmp["policy_name"] = policy_info["name"]
                tmp["account"] = user_info["account"]
                tmp["name"] = user_info["name"]
                data.append(tmp)
            accounts = list(set([info["account"] for info in data]))
            # logging.warning("所有未生效策略的用户帐号=%s" % accounts)
            for account in accounts:
                for info in data:
                    if account == info.get("account"):
                        _policy_type[info.get("policy_type")].append(info.get("policy_name"))
                        _username = info.get("name")
                single_user = "<tr><td>" + _username + "</td><td>" + account + "</td><td>" + ",".join(
                    _device) + "</td><td>" + ",".join(
                    _complicance) + "</td><td>" + ",".join(
                    _fence) + "</td><td>" + ",".join(_application) + "</td></tr>"
                content += single_user

                del _device[:]
                del _complicance[:]
                del _fence[:]
                del _application[:]
            if content:
                send_mail([_admin.get("manager_email")], "【" + _admin.get("company_short") + "】策略未生效统计",
                          "<html><body><h4>管理员&nbsp;:&nbsp;您好!</h4></p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                          "经系统检测，策略下发后未生效策略详情：<p><b><table border='1'><tr><th>用户名称</th><th>登录账户"
                          "</th><th>设备策略</th><th>合规策略</th><th>围栏策略</th><th>应用策略</th></tr>%s</b></body></html>" % content.encode("utf8"))
        mongoClient.close()
    except Exception as e:
        logging.exception("error %s" % e)
        raise e


def optResult(res, org):
    d = {}
    for r in res:
        if type(org) == list:
            r['_id'] = r['_id'][0]
        d[r['_id']] = r
    aa = haskey(d, org)
    if aa == 0:
        return 0
    else:
        return aa[org]['count']


def haskey(d, k):
    aa = d if d.has_key(k) else 0
    return aa


# class ExecuteDataStatisticsJob:

def execute_data_statistics_job(result, cacheDB):
    """
    Execute data statistics job ：data_statistics
    """
    try:
        today_start, today_end = getdays(-1)
        mongoClient = pymongo.MongoClient(host=host, port=27017)
        db = mongoClient["rom_private"]
        # ---------------以下所有数据都分机构
        org_list = []  # 机构id列表

        orgs = db.organization.find({"available": 1}, {"_id": 0, "id": 1})
        for o in orgs:
            org_list.append(o['id'])
        # print org_list

        users_count = db.user.aggregate([
            {'$match': {'available': 1, 'create_time': {'$lt': today_end}}},
            {"$group": {"_id": "$org_id", "count": {'$sum': 1}}}
        ])
        # print users_count['result']
        logging.info(users_count['result'])
        # usersCount  每天23点之前的用户总数
        active_user_count = db.user.aggregate([
            {'$match': {'available': 1, "status": 1, 'create_time': {'$lt': today_end}}},
            {"$group": {"_id": "$org_id", "count": {'$sum': 1}}}
        ])
        # active_user_count每天23点之前的激活用户数
        # print active_user_count['result']
        device_count = db.dev.aggregate([
            {'$match': {"uid": {"$ne": -1}}},
            {"$group": {"_id": "$org_id", "count": {'$sum': 1}}}
        ])
        # print device_count['result']
        # 每天23点之前的设备数
        dev_complicance_count = db.dev.aggregate([
            {'$match': {"uid": {"$ne": -1}}},
            {"$group": {"_id": "$org_id", "count": {'$sum': 1}}}
        ])
        # print dev_complicance_count['result']  激活状态字段缺省
        # 每天23点激活设备数
        dev_online_count = db.dev.aggregate([
            {'$match': {"online": 0, "uid": {"$ne": -1}}},
            {"$group": {"_id": {'_id': "$org_id", 'dev_id': "$dev_id"}}},
            {'$project': {'_id': 1, 'dev_id': 1}},
        ])
        dev_log_ol_cont = db.clientUserLog.aggregate([
            {'$match': {
                "opt_time": {'$gte': today_start, '$lt': today_end},
                "state": "成功",
                "operate": {"$in": ["登录", '登出', '注销', '设备上线', '设备下线']}
            }},
            {"$group": {"_id": {'_id': "$org_id", 'dev_id': "$dev_id"}}},
            {'$project': {'_id': 1, 'dev_id': 1}},
        ])
        org_arr = []
        devlist = []
        for dev in dev_log_ol_cont['result']:
            devlist.append(dev['_id'])
        # print devlist
        onlineList = {}
        dev_line_count = {}
        for org in org_list:
            onlineList[org] = []
            for d in devlist:
                if d['_id'] == org:
                    onlineList[org].append(d['dev_id'])
            for do in dev_online_count['result']:
                if do['_id'] == org:
                    onlineList[org].append(do['dev_id'])
            dev_line_count[org] = len(list(set(onlineList[org])))
        # print dev_line_count
        # dev_line_count 是返回的字典key为org_id value为今天23点之前在线人数

        pol_total = db.policy.aggregate([
            {'$match': {'available': 1, 'create_time': {'$lt': today_end}}},
            {"$group": {"_id": "$org_id", "count": {'$sum': 1}}}
        ])
        # 所有策略
        # print pol_total['result']
        on_per_content = db.policy.aggregate([
            {'$match': {'available': 1, "status": 1, 'create_time': {'$lt': today_end}}},
            {"$group": {"_id": {"org_id": "$org_id", "id": "$id"}}},
            {'$project': {'id': 1, 'org_id': 1}},
        ])
        # print on_pol_content['result']
        # print len(on_per_content['result'])
        pocc = {}
        for o in org_list:
            # print o
            poc = 0
            for per in on_per_content['result']:
                if per["_id"]['org_id'] == o:
                    poc += 1
            # print poc
            pocc[o] = poc
        # pocc每个机构的启用策略数
        # print pocc

        on_pol_id = [int(per['_id']["id"]) for per in on_per_content['result']]
        # onpolid 所有启用策略的id列表
        # print on_pol_id
        pol_issue = db.user_policy.aggregate([{"$match": {"policy_id": {"$in": on_pol_id}}},
                                              {"$group": {"_id": {"pid": "$policy_id", 'uid': "$uid"}}}])  # 查询所有应用的启用策略
        perlist = [int(info["_id"]['uid']) for info in pol_issue['result']]
        # 所有应用的启用策略的用户id列表
        org_user = db.user.find({'id': {'$in': perlist}}, {'_id': 0, 'id': 1, 'org_id': 1})
        # 所有应用启用策略的用户的对应机构id和用户id
        for ou in org_user:
            for info in pol_issue['result']:
                if info['_id']['uid'] == ou['id']:
                    info["_id"]["org_id"] = ou['org_id']
        # 把机构id添加到查询出的应用启用策略的结果集中
        # print pol_issue['result']
        pol_ousers_count = {}
        for org in org_list:
            pol_issue_tatal = 0
            pidlist = []
            for info in pol_issue['result']:
                if info['_id']["org_id"] == org and info['_id']['pid'] not in pidlist:
                    pidlist.append(info['_id']['pid'])
                    pol_issue_tatal += 1
            # print pol_issue_tatal
            pol_ousers_count[org] = pol_issue_tatal

        # pol_ousers_count 为按机构分应用启用策略的个数

        # print '----------pousers------------'
        # print pol_ousers_count

        # app
        app_list_count = db.app_list.aggregate([
            {"$group": {"_id": "$org_id", "count": {"$sum": 1}}}
        ])  # 黑名单
        # print app_list_count['result']
        app_count = db.app.aggregate([
            {'$group': {"_id": "$org_id", "count": {"$sum": 1}}},
        ])
        # 应用总数 目前app没有分机构所以orgid为None即所有机构都为count值
        # print app_count['result']
        user_app = db.user_application.aggregate([
            {"$lookup": {"from": 'user', 'localField': 'uid', 'foreignField': "id", 'as': "user"}},
            {"$group": {'_id': "$user.org_id", 'count': {'$sum': 1}}},
            # {'$project':{'_id':0,"app_identify":1,'uid':1,'user.org_id':1}},
        ])
        # print user_app['result']
        # 机构已经下发应用数
        dev_out_contact = db.violationLog.aggregate([
            {'$match': {'operate': {"$regex": '失联'}, "state": "成功", 'opt_time': {'$lt': today_end}}},
            {"$group": {"_id": "$org_id", 'count': {"$sum": 1}}},
        ])
        # print dev_out_contact['result']
        # 设备失联
        dev_root_low = db.violationLog.aggregate([
            {'$match': {'operate': {"$regex": 'root'}, "state": "成功", 'opt_time': {'$lt': today_end}}},
            {"$group": {"_id": "$org_id", 'count': {"$sum": 1}}},
        ])
        # print dev_version_low['result']
        # 版本过低
        dev_change_sim = db.violationLog.aggregate([
            {'$match': {'operate': {"$regex": 'SIM卡'}, "state": "成功", 'opt_time': {'$lt': today_end}}},
            {"$group": {"_id": "$org_id", 'count': {"$sum": 1}}},
        ])
        # print dev_change_sim['result']
        # sim卡变更
        dev_elimination = db.dev_log.aggregate([
            {'$match': {'operate': {"$regex": '设备淘汰'}, "state": "成功", 'opt_time': {'$lt': today_end}}},
            {"$group": {"_id": "$org_id", 'count': {"$sum": 1}}},
        ])
        # print dev_elimination['result']
        # 设备淘汰
        # ---------------------------------------------clientAppLog
        app_black_count = db.clientAppLog.aggregate([
            {'$match': {'operate': {"$regex": '黑名单'}, 'opt_time': {'$gte': today_start, '$lt': today_end}}},
            {"$group": {"_id": "$org_id", 'count': {"$sum": 1}}},
        ])
        # print app_black_count['result']
        # 黑名单应用下载
        # print list(app_black_count)
        url_violation_count = db.urlLog.aggregate([
            {'$match': {'log_type': {"$regex": '^违规URL$'}, 'opt_time': {'$gte': today_start, '$lt': today_end}}},
            {"$group": {"_id": "$org_id", 'count': {"$sum": 1}}},
        ])
        # print url_violation_count['result']
        # 违规url
        # print list(url_violation_count)
        sen_words_count = db.senWordLog.aggregate([
            {'$match': {'opt_time': {'$gte': today_start, '$lt': today_end}}},
            {"$group": {"_id": "$org_id", 'count': {"$sum": 1}}},
        ])
        # 敏感词
        # print sen_words_count['result']

        reset_factory_count = db.dev_log.aggregate([
            {'$match': {'operate': {"$regex": '恢复出厂'}, 'opt_time': {
                # '$gte':today_start,
                '$lt': today_end
            }}},
            {"$group": {"_id": "$org_id", 'count': {"$sum": 1}}},
        ])
        # 恢复出厂
        # print reset_factory_count['result']
        eliminate_data_count = db.dev_log.aggregate([
            {'$match': {'operate': {"$regex": '擦除企业'}, 'opt_time': {
                # '$gte':today_start,
                '$lt': today_end
            }}},
            {"$group": {"_id": "$org_id", 'count': {"$sum": 1}}},
        ])
        # 擦除企业数据
        # print eliminate_data_count['result']

        loglist = []
        user_app_dict = {}
        for ua in user_app['result']:
            ua['_id'] = ua['_id'][0]
            user_app_dict[ua['_id']] = ua['count']

        for org in org_list:
            orglog = {}
            orglog['org_id'] = org
            orglog['users_count'] = optResult(users_count['result'], org)
            orglog['active_user_count'] = optResult(active_user_count['result'], org)
            orglog['device_count'] = optResult(device_count['result'], org)
            orglog['dev_complicance_count'] = optResult(dev_complicance_count['result'], org)
            orglog['dev_online_count'] = dev_line_count[org]
            orglog['pol_total'] = optResult(pol_total['result'], org)
            orglog['on_pol_content'] = pocc[org]
            orglog['pol_ousers_count'] = pol_ousers_count[org]
            orglog['app_list_count'] = optResult(app_list_count['result'], org)
            orglog['app_count'] = app_count['result'][0]['count']
            orglog['user_app'] = user_app_dict[org] if user_app_dict.has_key(org) else 0
            orglog['dev_out_contact'] = optResult(dev_out_contact['result'], org)
            orglog['dev_root'] = optResult(dev_root_low['result'], org)
            orglog['dev_change_sim'] = optResult(dev_change_sim['result'], org)
            orglog['dev_elimination'] = optResult(dev_elimination['result'], org)
            orglog['app_blackdown_count'] = optResult(app_black_count['result'], org)
            orglog['url_violation_count'] = optResult(url_violation_count['result'], org)
            orglog['sen_words_count'] = optResult(sen_words_count['result'], org)
            orglog['reset_factory_count'] = optResult(reset_factory_count['result'], org)
            orglog['eliminate_data_count'] = optResult(eliminate_data_count['result'], org)
            # print orglog
            orglog['opt_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            loglist.append(orglog)
        logging.info(loglist)
        db.data_statistics.insert(loglist)
        logging.info('--------------insert_res-----------------')
        sen_word_org_count = db.senWordLog.find(
            {'opt_time': {
                '$gte': today_start,
                '$lt': today_end
            }},
            {"_id": 0, 'sensitive_word': 1, 'org_id': 1},
        )
        # print sen_word_org_count
        swoc_list = list(sen_word_org_count)
        senlog = {}
        for oid in org_list:
            senlog[oid] = {}
            for swoc in swoc_list:
                # print swoc
                if int(swoc['org_id']) == oid:
                    #         print swoc['sensitive_word']
                    if senlog[oid].has_key(swoc['sensitive_word']):
                        senlog[oid][swoc['sensitive_word']] += 1
                    else:
                        senlog[oid][swoc['sensitive_word']] = 1
        senlog_list = []
        for sl in senlog:
            senlog[sl]["org_id"] = sl
            senlog[sl]["opt_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            senlog_list.append(senlog[sl])
        # print senlog_list
        db.senword_violation_count.insert(senlog_list)
        # pass
        logging.info('-==============insert_senlog')
        # 每天23点
        mongoClient.close()

    except Exception as e:
        logging.info(e)


if __name__ == '__main__':
    executeFailureStrategyTask()