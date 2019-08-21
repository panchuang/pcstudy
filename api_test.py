# _*_ coding:utf-8 _*_
__author__ = 'pan'
import sys
import logging
import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.web
from tornado.options import options, define


define("port", default=8080, help="Tornado Server", type=int, metavar="none")

class Test(tornado.web.RequestHandler):

    def get(self):
        self.write('hello')

    def post(self):
        num = self.get_argument('num')
        self.write(num)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    tornado.options.parse_command_line()
    application = tornado.web.Application(
        handlers=[(r'/',Test),]
    )
    http_server = tornado.httpserver.HTTPServer(application,xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()