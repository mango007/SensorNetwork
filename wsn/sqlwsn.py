#this module is the middle ware between database and wsn server
import MySQLdb
import math
import setting
import time
import random
import calendar

#map the Sensor table
class Sensor():
    sensorID = 0
    x = 0
    y = 0
    initialEnergy = 0
    remainingEnergy = 0
    lastVoltage = 0
    lastConnectedTime = None
    def __init__(self, sensorID, lastConnectedTime, initialEnergy, remainingEnergy, lastVoltage, x, y):
        self.sensorID = sensorID
        self.lastConnectedTime = lastConnectedTime
        self.initialEnergy = initialEnergy
        self.remainingEnergy = remainingEnergy
        self.lastVoltage = lastVoltage
        self.x = x
        self.y = y

#this class retrieves sensor information and network topology information from database
class DatabaseAccess():
    sqladd = setting.sqladd
    userid = setting.userid
    userpsw = setting.userpsw
    database = setting.database

    baseStations = {}
    regularSensors = {}
    sensors = {}
    neighborhood = {}

    def __init__(self):
        db = MySQLdb.connect(self.sqladd,self.userid,self.userpsw,self.database)
        cursor = db.cursor()
        cursor.execute("select * from monitor_sensor;")
        sensors = cursor.fetchall()


        for sensor in sensors:
            s = Sensor(int(sensor[0]), sensor[1], sensor[2], sensor[3], sensor[5], int(sensor[6]), int(sensor[7]))
            self.sensors[int(sensor[0])] = s
            if int(sensor[4]) == 1:
                self.baseStations[int(sensor[0])] = s
            else:
                self.regularSensors[int(sensor[0])] = s
            self.neighborhood[int(sensor[0])] = {}
        db.close()
        self.getTopology()

    #retrieve topology information
    def getTopology(self):
        db = MySQLdb.connect(self.sqladd,self.userid,self.userpsw,self.database)
        cursor = db.cursor()
        cursor.execute("select * from monitor_topology;")
        data = cursor.fetchall()
        for row in data:
            sensor1ID = int(row[1])
            sensor2ID = int(row[2])
            sensor1 = self.sensors[sensor1ID]
            sensor2 = self.sensors[sensor2ID]
            distance  = math.sqrt(math.pow(sensor1.x-sensor2.x,2)+math.pow(sensor1.y-sensor2.y,2))

            self.neighborhood[sensor1ID][sensor2ID] = distance
            self.neighborhood[sensor2ID][sensor1ID] = distance
        db.close()


    #create a network randomly
    def createNetwork(self, numOfBasestation, numOfRegularSensors):
        db = MySQLdb.connect(self.sqladd,self.userid,self.userpsw,self.database)
        cursor = db.cursor()
        connected = []
        unconnected = []
        cursor.execute("TRUNCATE TABLE monitor_sensor;")
        cursor.execute("TRUNCATE TABLE monitor_topology;")
        for id in range(numOfBasestation):
            command = "INSERT INTO monitor_sensor (sensor_id, last_connected_time, initial_energy, remaining_energy, is_base_station, last_voltage, x, y) " \
                         "VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}');".\
                format(id,
                       time.strftime('%Y-%m-%d %H:%M:%S', time.struct_time((2014,11,1,0,0,0,0,0,0))),
                       setting.initEnergyBS,
                       setting.initEnergyBS,
                       1,
                       4.8,
                       id,
                       random.randint(0, 2*(numOfBasestation+numOfRegularSensors)))
            cursor.execute(command)
            connected.append(id)
        for id in range(numOfBasestation, numOfBasestation+numOfRegularSensors):
            command = "INSERT INTO monitor_sensor (sensor_id, last_connected_time, initial_energy, remaining_energy, is_base_station, last_voltage, x, y) " \
                         "VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}');".\
                format(id,
                       time.strftime('%Y-%m-%d %H:%M:%S', time.struct_time((2014,11,1,0,0,0,0,0,0))),
                       setting.initEnergyRS,
                       setting.initEnergyRS,
                       0,
                       4.8,
                       id,
                       random.randint(0, 2*(numOfBasestation+numOfRegularSensors)))
            cursor.execute(command)
            unconnected.append(id)
        edges = []
        while unconnected:
            s1 = random.sample(unconnected, 1)[0]
            unconnected.remove(s1)
            edges.append((s1, random.sample(connected,1)[0]))
            connected.append(s1)

        for i in range(10):
            s1 = random.randint(0, numOfBasestation+numOfRegularSensors-1)
            s2 = random.randint(0, numOfBasestation+numOfRegularSensors-1)
            if s1 == s2 or (s1,s2) in edges or (s2,s1) in edges:
                continue
            else:
                edges.append((s1,s2))
        for edge in edges:
            command = "INSERT INTO monitor_topology (sensorID1, sensorID2) " \
                         "VALUES ('{0}','{1}');".\
                format(edge[0],
                       edge[1])
            cursor.execute(command)
        db.close()

    #insert information about activated base stations into ActiveBS table
    def insertActive(self, exp, routingRound, F0):
        db = MySQLdb.connect(self.sqladd,self.userid,self.userpsw,self.database)
        timeStamp = time.struct_time((2014,11,1,0,0,0,0,0,0))
        cursor = db.cursor()
        starttime = time.gmtime(calendar.timegm(timeStamp)+60*setting.rt*routingRound)
        endtime = time.gmtime(calendar.timegm(timeStamp)+60*setting.rt*(routingRound+1))
        for i in F0:
            tmpcommand = "INSERT INTO ActiveBS (Experiment, NodeID, StartTime, EndTime) VALUES ('{0}','{1}','{2}','{3}');"\
                .format(exp,i,time.strftime('%Y-%m-%d %H:%M:%S', starttime),time.strftime('%Y-%m-%d %H:%M:%S', endtime))
            cursor.execute(tmpcommand)
        db.close()

#this class inserts received messages into database
class MyDataModel(object):
    sqladd = setting.sqladd
    userid = setting.userid
    userpsw = setting.userpsw
    database = setting.database
    resourceAvai = True
    def __init__(self,data,exp):
        self.data = data
        self.sepdatalist = None
        self.exp = exp

    @staticmethod
    def requestResource():
        if MyDataModel.resourceAvai == False:
            return False
        else:
            MyDataModel.resourceAvai = False
            return True

    @staticmethod
    def releaseResource():
        if MyDataModel.resourceAvai == False:
            MyDataModel.resourceAvai =True
            return True
        else:
            MyDataModel.resourceAvai = True
            return True

    def separateData(self):
        sepstr =chr(0x10)+chr(0x11)+chr(0x12)+chr(0x13)
        self.sepdatalist = self.data.split(sepstr)
        self.sepdatalist= self.sepdatalist[0:len(self.sepdatalist)-1]
        # print "The number of packets received:{0}".format(len(self.sepdatalist)) #this shows the number of strings received
        for index in range(0,len(self.sepdatalist)):
            s =self.sepdatalist[index]
            #print ':'.join(x.encode('hex') for x in s[0:5])

    def sendSqldata(self):
        while MyDataModel.requestResource()== False:
            time.sleep(0.01)
        # set up sql connection
        db = MySQLdb.connect(MyDataModel.sqladd,MyDataModel.userid,MyDataModel.userpsw,MyDataModel.database )
        cursor = db.cursor()
        # print len(self.sepdatalist)
        # mystringlist = self.mystring.split('\r') # '\r' is a separator
        for s in self.sepdatalist:
            # print s
            result=self.unpackstring(s)
            nodeid = result['nodeid']
            timestamp = result['timestamp']
            voltage = result['voltage']
            cumcurr = result['cumcurr']
            data = "111"
            if result!=None:
                #insert sensor information into EnergyMonitor table
                tmpcommand = "INSERT INTO EnergyMonitor (NodeID, Time, Voltage, CumCurr, Data, Experiment) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}');"\
                    .format(nodeid,timestamp,voltage,cumcurr,data,self.exp)
                cursor.execute(tmpcommand)

                #updata corresponding sensor information, i.e. last_connected_time, remaining_energy and last_voltage
                tmpcommand = "UPDATE monitor_sensor SET last_connected_time = '{0}', remaining_energy = '{1}', last_voltage = '{2}' WHERE sensor_id = '{3}'"\
                    .format(timestamp, cumcurr, voltage, nodeid)
                cursor.execute(tmpcommand)

        db.close()
        MyDataModel.releaseResource()

    def unpackstring(self,tmpstring):
        nodeid  = ord(tmpstring[0])  #uint8_t nodeid, uint32_t timestamp, uint16_t voltage, uint16_t cumcurr, uint16_t data,

        voltage_low  = ord(tmpstring[1])
        voltage_high = (ord(tmpstring[2]) & 0x07)
        voltage= (voltage_high*256+voltage_low)*0.00244

        cumcurr_low  = ord(tmpstring[3])
        cumcurr_high = ord(tmpstring[4])
        cumcurr  = cumcurr_high*256+cumcurr_low

        timestamp = tmpstring[5:]
        data = tmpstring[0:5]
        return {'nodeid':nodeid, 'timestamp':timestamp ,'voltage':voltage, 'cumcurr':cumcurr, 'data':data }

#Before each test, the Sensor table, EnergyMonitor table and ActiveBS table should be reset to default value
def clean(exp):
    db = MySQLdb.connect(setting.sqladd,setting.userid,setting.userpsw,setting.database )
    cursor = db.cursor()
    cursor.execute("DELETE FROM EnergyMonitor WHERE Experiment = {0};".format(exp))
    cursor.execute("DELETE FROM ActiveBS WHERE Experiment = {0};".format(exp))
    command = "UPDATE monitor_sensor SET last_connected_time = '{0}', initial_energy = '{1}'," \
              " remaining_energy = '{2}', last_voltage = '{3}' WHERE is_base_station = '1'".\
            format( time.strftime('%Y-%m-%d %H:%M:%S', time.struct_time((2014,11,1,0,0,0,0,0,0))),
                    setting.initEnergyBS,
                    setting.initEnergyBS,
                    4.8)
    cursor.execute(command)
    command = "UPDATE monitor_sensor SET last_connected_time = '{0}', initial_energy = '{1}'," \
              " remaining_energy = '{2}', last_voltage = '{3}' WHERE is_base_station = '0'".\
            format( time.strftime('%Y-%m-%d %H:%M:%S', time.struct_time((2014,11,1,0,0,0,0,0,0))),
                    setting.initEnergyRS,
                    setting.initEnergyRS,
                    4.8)
    cursor.execute(command)
    db.close()

if __name__ == "__main__":
    dba = DatabaseAccess()
    dba.createNetwork(setting.bsnum,setting.rsnum)



