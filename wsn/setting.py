#Server
host = "localhost"
port = 53464

#MySQL
sqladd = "localhost"
userid = "root"
userpsw = "lcav123"
database = "smartsense"


#network parameter
#initVoltage = 4.88 #initial voltage of sensors
initEnergyBS = 30000 #initial energy(or cumulative current) of base station
initEnergyRS = 10000 #initial energy(or cumulative current) of regular sensor
bsnum = 5 #number of base stations
rsnum = 10 #number of regular sensors
rst = 10 #time interval for regular sensor to send a message(eg. 10 minutes)
bst = 30 #time interval for base station to send messages to remote server(eg. 30 minutes)
rt = 60  #time interval for a network to update its routing strategy
cc,cst,csr,clc,clt,r = 6,1,1,60,1,6

alpha = 10000
