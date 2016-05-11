import tornado
import tornado.auth
import tornado.httpserver
import tornado.web

import ui
from api.baseapi import Api
from handler import MainHandler, SMHandler, DebugHandler, DevHandler, LoginHandler


def start(port):
    settings = {
        "cookie_secret": "*****",
        "login_url": "/login",
        # "xsrf_cookies": True,
        'debug': True,
        "ui_modules": ui,

    }

    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/e/.*", SMHandler),
        (r"/debug(/.*|)$", DebugHandler),
        (r"/dev(/.*|)$", DevHandler),
        (r"/api(/.*|)$", Api),
        (r"/login(/.*|)$", LoginHandler),
        (r"/files/(.*)", tornado.web.StaticFileHandler, {"path": "static/files/"}),
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    print('started')
    tornado.ioloop.IOLoop.current().start()
