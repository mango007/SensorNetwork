import SocketServer
import MySQLdb
import time
import threading
from route import Route
import sys
import setting
import sqlwsn
from sqlwsn import MyDataModel

#indicate which experiment
exp = None
#retrive routing table
route = None

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        cur_thread = threading.current_thread()
        self.data=""
        
        str_end=chr(0x10)+chr(0x11)+chr(0x12)+chr(0x13)+chr(0x19)
        while (str_end not in self.data):   #(chr(0x1a) not in data) and
            self.data = self.data+ self.request.recv(1024)

        #if client sends an particular string, server will response the new routing table
        str_rout = chr(0x0F)+chr(0x10)+chr(0x11)+chr(0x12)+chr(0x13)+chr(0x19)
        if self.data[0:6] == str_rout:
            #In the received message, [6:end] byes indicate the routing round
            self.request.sendall(route.getRoutingTable(int(self.data[6:len(self.data)])))
            print int(self.data[6:len(self.data)])
            return
        dm = MyDataModel(self.data, exp)
        dm.separateData()
        dm.sendSqldata()


        
class ThreadedTCPServer(SocketServer.ForkingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in ['0', '1', '2','3']:
        exp = int(sys.argv[1])
    else:
        print "wrong argument"
        print "0: random"
        print "1: one base station"
        print "2: all base stations"
        print "3: moving base stations"
        sys.exit()

    #database reset before each test
    sqlwsn.clean(exp)
    route = Route(exp)

    HOST, PORT = setting.host, setting.port
    SocketServer.TCPServer.allow_reuse_address = True

    # Create the server, binding to localhost on port 9999
    # server = SocketServer.ForkingTCPServer((HOST, PORT), MyTCPHandler)
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    try:
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.setDaemon(True)

        # server_thread.daemon = True
        print "Server loop running in thread:", server_thread.name
        server_thread.start()

        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print 'Received keyboard interrupt, quitting threads.\n'
        threading.Event().set()
        sys.exit(0)



