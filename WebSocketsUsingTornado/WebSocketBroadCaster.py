import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.httpclient
import tornado.options
import datetime

from tornado.options import define, options
define("port", default=7777, help="run on the given port", type=int)

class SubscribeHandler(tornado.websocket.WebSocketHandler):
    sClientsPerService = {} 

    def open(self,clientName):
        print "Opened Websocket"
        print "Received clientName: %s"%(clientName)

        self.clientName = clientName        

        if clientName not in SubscribeHandler.sClientsPerService.keys(): 
            SubscribeHandler.sClientsPerService[clientName] = []
        
        SubscribeHandler.sClientsPerService[clientName].append(self)
           
    def on_message(self):
        pass

    def on_close(self):
        print 'Closed Websocket'

        SubscribeHandler.sClientsPerService[self.clientName].remove(self)
        if len(SubscribeHandler.sClientsPerService[self.clientName]) == 0:
            SubscribeHandler.sClientsPerService.pop(self.clientName)

class BroadcastHandler(tornado.web.RequestHandler):
    
    def post(self, clientName):
        message = self.get_argument('message')
        if SubscribeHandler.sClientsPerService.has_key(clientName):
            for client in SubscribeHandler.sClientsPerService[clientName]:
                client.write_message(message)   


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/subscribe/([\w\-]+)",SubscribeHandler),
            (r"/broadcast/([\w\-]+)",BroadcastHandler)
        ],
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
