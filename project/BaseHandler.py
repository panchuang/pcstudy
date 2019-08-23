# -*-coding:utf8 -*-

import time
import uuid
import json
import logging
import httplib
from api import ecode
from tornado import gen
from utils.dto import Dto
from config import config
from tornado.web import RequestHandler
from utils.auth_verify import authverify


class BaseHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        # self.set_header("Access-Control-Allow-Origin", "http://192.168.2.147:3000")
        # self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, X-Requested-By, \
                        If-Modified-Since, X-File-Name, Cache-Control")

    @property
    def admin(self):
        return config.adminInfo()

    @property
    def adminSettings(self):
        return self.application.adminSettings

    @property
    def pymongo_db(self):
        return self.application.pymongo_client

    @property
    def base_db(self):
        return self.application.db_client

    @property
    def app_db(self):
        return self.application.db_app_client

    @property
    def session_db(self):
        return self.application.sessionDB

    @property
    def cache_db(self):
        return self.application.cacheDB

    @property
    def userpolicy_db(self):
        return self.application.userPolicyDB

    @property
    def secbuff(self):
        return self.application.secbuff

    @property
    def pwdexpiry_db(self):
        return self.application.pwdExpiryDB

    @property
    def filecache_db(self):
        return self.application.fileCacheDB

    @property
    def image_root(self):
        return self.application.image_root

    @property
    def log_root(self):
        return self.application.log_root

    @property
    def document_root(self):
        return self.application.document_root

    @property
    def qrcode_root(self):
        return self.application.qrcode_root

    @property
    def confman(self):
        return self.application.confman_root

    @property
    def sms_server(self):
        return self.application.sms_server

    @property
    def fido_server(self):
        return self.application.fido_server

    @property
    def sched(self):
        return self.application.sched

    @property
    def license(self):
        return self.application.license

    @license.setter
    def license(self, value):
        if isinstance(value, dict):
            self.application.license = value

    @property
    def jpushMsg(self):
        return self.application.jpushMsg

    @property
    def recodLog(self):
        return self.application.recodLog

    def get_params(self, request_list_args):
        params = self.request.arguments
        dto = Dto()
        for item in request_list_args:
            if not params.get(item, None):
                logging.error("%s is needed", item)
                return None
        dto.update(dict([(key, value[0])for key, value in params.items()]))
        return dto

    def get_and_check_params(self, request_list_args):
        request_params = self.get_params(request_list_args)
        if not request_params:
            raise ecode.IPUTERROR
        return request_params

    def get_id(self, name):
        db_id = self.base_db.ids.find_and_modify(query={'name': name}, update={'$inc': {'id': 1}}, new=True, fields={'_id': 0, 'id': 1})
        return db_id

    @gen.coroutine
    def get_operater(self, user):
        operater = eval(user)
        admin = operater.get("admin")
        raise gen.Return(admin)

    @gen.coroutine
    def get_user(self, user):
        operater = eval(user)
        account = operater.get("user")
        raise gen.Return(account)

    @gen.coroutine
    def get_organ(self, user):
        operater = eval(user)
        orgId = int(operater.get("org"))
        raise gen.Return(orgId)

    @gen.coroutine
    def get_dev(self, user):
        user = eval(user)
        dev_id = user.get("dev_id")
        raise gen.Return(dev_id)

    def notify_by_push_server(self, sid):
        try:
            if not self.is_sid_on_push_server(sid):
                return
            conn = httplib.HTTPConnection(
                '%s:%d' % (self.application.pushConfig['host'], self.application.pushConfig['port']))
            conn.request("POST", "/pub?id=%s" % (sid), 'cmd')
        except:
            logging.exception('notify_by_push_server,sid:%s,pushs_host:%s,port:%d', sid, self.application.pushConfig['host'], self.application.pushConfig['port'])

    def is_sid_on_push_server(self, sid):
        try:
            conn = httplib.HTTPConnection('%s:%d' % (self.application.pushConfig['host'], self.application.pushConfig['port']))
            conn.request("GET", "/channels-stats?id=%s" % (sid))
            r = conn.getresponse()
            if r.status == 200:
                return True
        except:
            logging.exception('is_sid_on_push_server,sid:%s,pushs_host:%s,port:%d', sid, self.application.pushConfig['host'], self.application.pushConfig['port'])
        return False

    @authverify
    @gen.coroutine
    def prepare(self):
        try:
            request_url = self.request.uri.split("?")[0]
            request_params = self.request.arguments
            request_params = dict([(key, value[0]) for key, value in request_params.items()])
            # logging.warning(self.request)
            logging.info("clent_ip= %s, protocol= %s, API= %s, method= %s, request_params= %s" %
                        (self.request.remote_ip, self.request.version, request_url, self.request.method, request_params))
            if self.request.method == "PUT" and "org_id" in request_params:
                raise ecode.IPUTERROR
            sid = request_params.get("sid", "")
            # logging.info("sid:"+sid)
            if sid:
                user = self.session_db.get_user(sid)
                logging.info("user:"+user)
                if not user:
                    raise ecode.SESSION_EXPIRATION
                if user.find("dev_id") == -1:
                    self.session_db.flush_session(sid)
                    adm = yield self.get_operater(user)
                    # logging.info(adm)
                    admin_info = yield self.base_db.admin.find_one({"account": adm})
                    # logging.info(admin_info)
                    if not admin_info:
                        raise ecode.NOTEXISTUSER
                    elif admin_info["status"] == 0:
                        logging.warning("%s's account is disabled" % admin_info["account"])
                        raise ecode.ADMIN_FORBIDDEN
                    logging.info("--------------"+request_url)
                    if self.recodLog.url.get(request_url, ""):
                        self.recodLog.orgId = yield self.get_organ(user)
                        self.recodLog.method = self.request.method
                        self.recodLog.named = self.recodLog.url.get(request_url)
                        self.recodLog.admin = admin_info["account"]
                        self.recodLog.opt_time = time.strftime("%Y-%m-%d %X")
                        # logging.info("dddddddddddddddddddddddddddddddddddddddd")
                        # logging.info(request_params)
                        yield self.recodLog.LogHandler(request_url, request_params)
                else:
                    sessionId = eval(user)
                    if sessionId["repeat"] != 0:
                        self.session_db.del_sid(sid)
                        raise ecode.ACCOUNT_REPEAT_LOGIN
        except Exception as e:
            rt = (type(e) == type(ecode.OK)) and e or ecode.SESSION_EXPIRATION
            logging.info("-------------------------------123123123---------------")
            logging.error("err: %s" % e)
            self.write(dict(rt=rt.eid, desc=rt.desc))
            self.finish()

    @gen.coroutine
    def write(self, chunk):
        from tornado import escape
        from tornado.escape import utf8
        from tornado.util import unicode_type
        json_chunk = None
        if self._finished:
            raise RuntimeError("Cannot write() after finish()")
        if not isinstance(chunk, (bytes, unicode_type, dict)):
            message = "write() only accepts bytes, unicode, and dict objects"
            if isinstance(chunk, list):
                message += ". Lists not accepted for security reasons; see " \
                           "http://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.write"
            raise TypeError(message)
        if isinstance(chunk, dict):
            json_chunk = escape.json_encode(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        if json_chunk:
            json_chunk = utf8(json_chunk)
            self._write_buffer.append(json_chunk)
        elif chunk:
            chunk = utf8(chunk)
            self._write_buffer.append(chunk)
        # logging.warning("Response Data = %s" % json_chunk)
        if self.recodLog.insLogId:
            for per in self.recodLog.insLogId:
                if isinstance(chunk, str):
                    continue
                if chunk.get("rt") == "0000":
                    status = "成功"
                else:
                    status = "失败"
                if per["shunt"] in ["super", "admin"]:
                    yield self.base_db.admin_log.update({"_id": per["_id"]}, {"$set": {"state": status}}, multi=True)
                elif per["shunt"] == "org":
                    yield self.base_db.organ_log.update({"_id": per["_id"]}, {"$set": {"state": status}}, multi=True)
                elif per["shunt"] == "role":
                    yield self.base_db.role_log.update({"_id": per["_id"]}, {"$set": {"state": status}}, multi=True)
                elif per["shunt"] in ["user", "depart", "tag"]:
                    yield self.base_db.user_log.update({"_id": per["_id"]}, {"$set": {"state": status}}, multi=True)
                elif per["shunt"] == "device":
                    yield self.base_db.dev_log.update({"_id": per["_id"]}, {"$set": {"state": status}}, multi=True)
                elif per["shunt"] == "policy":
                    yield self.base_db.policy_log.update({"_id": per["_id"]}, {"$set": {"state": status}}, multi=True)
                elif per["shunt"] in ["appList", 'app']:
                    yield self.base_db.app_log.update({"_id": per["_id"]}, {"$set": {"state": status}}, multi=True)
                elif per["shunt"] == "file":
                    yield self.base_db.fileManagerLog.update({"_id": per["_id"]}, {"$set": {"state": status}}, multi=True)



