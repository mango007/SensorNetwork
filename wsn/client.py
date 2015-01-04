#this module simulates the wireless sensor network
#For simplicity, we assume all actions are in sequence,
# i.e. After a certain time, regular sensors will send messages in turn, then, they will transfer their messages in turn.
# Though in reality, the actions of regular sensors are independent.But it will not cause much inaccuracy.
#Another assumption is that base stations will send messages to server and retrieve routing information from server
#at fixed time points. Then Routing information is broadcast from each base station. This can be achieve in real network.

import socket
import Queue
import time
import calendar
import MySQLdb
from sqlwsn import DatabaseAccess
import setting
# from sqlwsn import MyDataModel
# import sys

#in our simulation, the start time is set to 2014-11-01 00:00:00
timeStamp = time.struct_time((2014,11,1,0,0,0,0,0,0))

routingTable = None
sensors = {} #all the sensors

#pack the message sent from each sensor
#message format: 1st byte: id, 2nd and 3rd byte: voltage, 4th and 5th bytes: cumulative current, remaining bytes: time stamp
def packString(m):
    global timeStamp
    packedm = ''
    packedm += chr(m['nodeid'])
    packedm += chr(m['voltage_low'])
    packedm += chr(m['voltage_high'])
    packedm += chr(m['cumcurr_low'])
    packedm += chr(m['cumcurr_high'])
    packedm += time.strftime('%Y-%m-%d %H:%M:%S', timeStamp)
    return packedm

#this class simulates the behaviors of regular sensor
#three major functions of a sensor:
#   send message, receive message, transfer message
class Sensor:
    remainingEnergy = None
    id = None
    nextNode = None
    messageQueue = None #every sensor has a message queue
    receivedMessage = 0 #number of received messages

    def __init__(self, id, remainingEnergy):
        self.id = id
        self.remainingEnergy = remainingEnergy
        self.messageQueue = Queue.Queue(1000000)

    def send(self):
        #if the sensor is base station and not used as regular sensor, it should not have send function
        if self.nextNode is None:
            return


        self.remainingEnergy -= (setting.cc)*setting.rst/60+self.receivedMessage*setting.csr+(self.receivedMessage+1)*setting.cst
        if self.remainingEnergy < 0: #have no energy to send a message
            return
        m = {'nodeid': self.id, 'voltage_low': 0xD0, 'voltage_high': 0x07,
             'cumcurr_low': int(self.remainingEnergy) & 0xFF, 'cumcurr_high': (int(self.remainingEnergy) & 0xFF00)/16/16}
        m = packString(m)
        try:
            self.messageQueue.put(m)
        except:
            return

    def receive(self, m):
        try:
            self.messageQueue.put(m)
            self.receivedMessage += 1
        except:
            pass

    def transfer(self):
        #if the sensor is base station and not used as regular sensor, it should not have transfer function
        if self.nextNode is None:
            return
        #if node has no energy
        if self.remainingEnergy < 0:
            return
        while True:
            try:
                m = self.messageQueue.get(False)
                self.nextNode.receive(m)
            except:
                break
        self.receivedMessage = 0 #reset the number of received messages to 0

    #receive routing information from base station
    def receiveRoutingTable(self):
        if self.id in routingTable.keys(): #if sensor is not base station
            self.nextNode = sensors[routingTable[self.id]]
        else:
            self.nextNode = None

#Base stations have all the functions of regular sensors.
#Base stations alse have the function: send messages to remote server
exp = None
class BaseStation(Sensor):
    ip = None   #ip address for connecting with remote server
    port = None

    def __init__(self, ip, port, id, remainingEnergy):
        Sensor.__init__(self, id, remainingEnergy)
        self.ip = ip
        self.port = port

    def sendToServer(self):

        self.remainingEnergy -= (setting.cc+setting.clc)*setting.bst/60+self.receivedMessage*setting.csr+(self.receivedMessage+1)*setting.clt
        if self.remainingEnergy < 0: #no energy to send messages
            return

        #append the information of basestation
        m = packString({'nodeid': self.id, 'voltage_low': 0xD0, 'voltage_high': 0x07,
            'cumcurr_low': int(self.remainingEnergy) & 0xFF, 'cumcurr_high': (int(self.remainingEnergy) & 0xFF00)/16/16})+chr(0x10)+chr(0x11)+chr(0x12)+chr(0x13)

        #append the sensors' information
        #chr(0x10)+chr(0x11)+chr(0x12)+chr(0x13) are the separating characters between each messages
        while True:
            try:
                m += self.messageQueue.get(False)+chr(0x10)+chr(0x11)+chr(0x12)+chr(0x13)
            except:
                break

        #append an end symbol
        m += chr(0x19)

        # dm = MyDataModel(m,exp)
        # dm.separateData()
        # dm.sendSqldata()
        # self.receivedMessage = 0
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.ip, self.port))
            sock.sendall(m)
            self.receivedMessage = 0
        except:
            pass
        return m

#In our simulation, we assume there is virtual base station which retrieves routing information from server.
#In real network, each base station should retrieve such information from server. But this will not impact the result.
routingRound = 0
def getRoutingTable():
    global routingTable,sensors,routingRound
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((setting.host, setting.port))
    #"chr(0x0F)+chr(0x10)+chr(0x11)+chr(0x12)+chr(0x13)+chr(0x19)" identifies the request as retrieving routing information
    #Base station should have a counter which records routing round, which is synchronized between all base stations
    sock.sendall(chr(0x0F)+chr(0x10)+chr(0x11)+chr(0x12)+chr(0x13)+chr(0x19)+str(routingRound))
    routingTable = {}
    r = sock.recv(1024)
    r = r.split(',')
    for e in r[0:-1]:
        e = e.split(':')
        routingTable[ord(e[0])] = ord(e[1])

    for sensor in sensors.values():
        sensor.receiveRoutingTable()

    routingRound += 1

#check if all the sensors have remaining energy
def hasEnergy():
    for sensor in sensors.values():
        if sensor.remainingEnergy < 0:
            return False
    return True

if __name__ == "__main__":
    # if len(sys.argv) == 2 and sys.argv[1] in ['0', '1', '2','3']:
    #     exp = int(sys.argv[1])
    # else:
    #     print "wrong argument"
    #     print "0: random"
    #     print "1: one base station"
    #     print "2: all base stations"
    #     print "3: moving base stations"
    #     sys.exit()

    global timeStamp,sensors,routingTable

    dba = DatabaseAccess()
    baseStations = {}
    for rs in dba.regularSensors.values():
        sensors[rs.sensorID] = Sensor(rs.sensorID, rs.remainingEnergy)
    for bs in dba.baseStations.values():
        baseStation =  BaseStation(setting.host, setting.port, bs.sensorID, bs.remainingEnergy)
        sensors[bs.sensorID] = baseStation
        baseStations[bs.sensorID] = baseStation

    getRoutingTable()
    activeBS = [] #activated base station
    for baseStation in baseStations.values():
        if baseStation.id in routingTable.values() and baseStation.nextNode is None:
            activeBS.append(baseStation)

    counter = 0
    while True:
        counter += 1
        if not hasEnergy():
            break

        timeStamp = time.gmtime(calendar.timegm(timeStamp)+60)

        if counter%setting.rst == 0:
            #every sensor sends message
            for s in sensors.values():
                s.send()

            #every sensor transfers message
            for s in sensors.values():
                s.transfer()

        #base stations send messages to server
        if counter%(setting.bst) == 0:
            for baseStation in activeBS:
                baseStation.sendToServer()

        #retrieve routing information
        if counter%(setting.rt) == 0:
            getRoutingTable()
            activeBS = []
            for baseStation in baseStations.values():
                if baseStation.id in routingTable.values() and baseStation.nextNode is None:
                    activeBS.append(baseStation)





