import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import uuid
import time
import thread

import tornado.wsgi
import wsgiref.simple_server

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
online = dict()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/login", LoginHandler),
            (r"/update", UpdateHandler),
            (r"/new", NewMsgHandler),
            (r"/([a-z0-9]*)", MainHandler),
        ]
        settings = dict(
            cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            autoescape="xhtml_escape",
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        name = self.get_argument('name')
        self.set_cookie("name", name)
        
class UpdateHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        name =  self.get_cookie("name")
        roomname = self.get_argument("roomname")
        if name is None:
            name = 'anonymous'
        self.name = name
        online[roomname].add((name, self.callback))
        self.roomname = roomname
    def callback(self, message):
        self.finish(message)

    def on_connection_close(self):
        online[self.roomname].remove((self.name, self.callback))
        if len(online[self.roomname]) == 0:
            del online[self.roomname]
    
class NewMsgHandler(tornado.web.RequestHandler):
    def new_messages(self, messages):
        global online
        name =  self.get_cookie("name")
        roomname = self.get_argument("roomname")
        if name is None:
            name = 'anonymous'
        for n, callback in online[roomname]:
            try:
                callback("<font color='green'>"+  name + "</font> > " + messages)
            except:
                logging.error("Error in waiter callback", exc_info=True)
        online[roomname] = set()    
    def post(self):
        msg = self.get_argument('text')
        self.new_messages(msg)
    
class MainHandler(tornado.web.RequestHandler):
    def get(self, roomname):
        if roomname == '':
            self.redirect('/global', permanent=True)
            return
        if online.has_key(roomname) == False:
            online[roomname] = set()
        self.render("index.html")

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
