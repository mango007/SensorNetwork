from monitor.models import Sensor, User_Sensor, Energymonitor, Topology, ActiveBS
from datetime import datetime, timedelta

#This model is the middle ware between database and website

#addSensor: add (user_id,sensor_id) pairs into database
#input: addid: list of sensor ids which will be added
#       request: http request
#outpot: None
def addSensor(addIDs, request):
    uid = request.user.id
    for id in addIDs:
        sid = int(id)
        us = User_Sensor(user_id = uid, sensor_id = sid)
        us.save()

#delSensor: delete (user_id,sensor_id) pairs from database
#input: delid: list of sensor ids which will be deleted
#       request: http request
#outpot: None
def delSensor(delIDs, request):
    uid = request.user.id
    for id in delIDs:
        sid = int(id)
        User_Sensor.objects.filter(user_id = uid).filter(sensor_id = sid).delete()

#getUserSensorIDs: retrieve sensors which belong to the current user
#input: request: http request
#output: list of sensors' ID
def getUserSensorIDs(request):
    uid = request.user.id
    return sorted([ele.sensor_id for ele in User_Sensor.objects.filter(user_id = uid)])

#getAllSensorIDs: retrieve all sensors in the network
#input: None
#output: list of sensors' ID
def getAllSensorIDs():
    return [ele.sensor_id for ele in Sensor.objects.all()]

#getSlope: calculate sensor's cumulative current decrease rate of each test
#input: sensorID: sensor's id
#       exps: list of test ids
#       start_time, end_time
#output: slopes of each test
def getSlope(sensorID, exps, start_time, end_time):
    slope = {}
    for i in exps:
        data = Energymonitor.objects.filter(nodeid = sensorID).filter(exp = i)\
                .filter(time__gte = start_time).filter(time__lte = end_time)
        if len(data) < 2:
            continue
        d1 = data[0]
        d2 = data[len(data)-1]
        t1 = getSecs((d1.time.replace(tzinfo=None)-datetime(1970,1,1)))
        t2 = getSecs((d2.time.replace(tzinfo=None)-datetime(1970,1,1)))
        slope[i] = (d2.cumcurr-d1.cumcurr)/(t2-t1)
    return slope

#getVIT: retrieve sensors' voltage and cumulative current information during a period
#input: selectedSens: list of sensor ids
#       selectedExp: test id
#       start_time, end_time
#output: list of voltage, cumulative current and time, which are for displaying the chart
def getVIT(selectedSens, selectedExp, start_time, end_time):
    data = Energymonitor.objects.filter(nodeid = selectedSens).filter(exp = selectedExp)\
                .filter(time__gte = start_time).filter(time__lte = end_time)
    if len(data) == 0:
        return ([],[],[])
    else:
        tT = []
        tV = []
        tI = []

        #100 time intervals between start time and end time
        #We take the average as the voltage and cumulative current for each interval
        nd = 100
        delta = timedelta(seconds=getSecs(end_time-start_time)/nd)
        iters = 0
        tmpt = start_time
        while iters < nd:
            iters += 1
            tT.append(tmpt+delta/2)
            tmp = [(ele.voltage,ele.cumcurr) for ele in data if tmpt <= ele.time.replace(tzinfo=None) < tmpt+delta]
            if len(tmp) == 0:
                tV.append(0.0)
                tI.append(0.0)
            else:
                sumV = 0
                sumI = 0
                for ele in tmp:
                    sumV += ele[0]
                    sumI += ele[1]
                tV.append(sumV/len(tmp))
                tI.append(sumI/len(tmp))
            tmpt = tmpt+delta

        #In some cases, there will be no data in a time interval, which causes the voltage and cumulative current to
        #be zero. The following code is to make sure the line is smooth. The idea is to find the closest non-zero data
        #on both side of current data point and take the average.
        V = []
        I = []
        T = []
        for i in range(0, len(tT)):
            T.append(tT[i])
            if tV[i] == 0.0:
                l = i-1
                lv = 0
                while l >= 0:
                    if tV[l] > 0:
                        lv = tV[l]
                    l = l-1
                r = i+1
                rv = 0
                while r < len(tT):
                    if tV[r] > 0:
                        rv = tV[r]
                    r = r+1
                if lv != 0 and rv != 0:
                    V.append(round((lv+rv)/2,2))
                else:
                    V.append(round(max(lv,rv),2))
            else:
                V.append(round(tV[i],2))
            if tI[i] == 0.0 :
                l = i-1
                lv = 0
                while l >= 0:
                    if tI[l] > 0:
                        lv = tI[l]
                        break
                    l = l-1
                r = i+1
                rv = 0
                while r < len(tT):
                    if tI[r] > 0:
                        rv = tI[r]
                        break
                    r = r+1
                if lv != 0 and rv != 0:
                    I.append((lv+rv)/2)
                else:
                    I.append(max(lv,rv))
            else:
                I.append(tI[i])

        return (V, I, T)

#getActiveTime: retrieve the activated time for all the base stations
#input: selectedExp: test id
#       start_time, end_time
#output: list of tuples with 12 elements, representing the start and end of activated time slot
#       (0~5: year, month, day, hour, minute, second of start time; 6~11: year, month, day, hour, minute, second of end time)
def getActiveTime(selectedExp, start_time, end_time):
    AT = {}
    baseStations = [ele.sensor_id for ele in Sensor.objects.filter(is_base_station = 1)]
    for bs in baseStations:
        data = ActiveBS.objects.filter(nodeid = bs).filter(exp = selectedExp)\
                .filter(starttime__gte = start_time).filter(endtime__lte = end_time)
        AT[bs] = [(ele.starttime.year,ele.starttime.month,ele.starttime.day,
                   ele.starttime.hour,ele.starttime.minute,ele.starttime.second,
                   ele.endtime.year,ele.endtime.month,ele.endtime.day,
                   ele.endtime.hour,ele.endtime.minute,ele.endtime.second) for ele in data]
    return AT

#getData: retrieve necessary data for rendering the linewithfocuschart.html
def getData(request):
    userSensors = getUserSensorIDs(request)
    exps = [0,1,2,3]
    end_time = datetime.now()
    selectedSens = []
    selectedExp = ''
    start_time = end_time-timedelta(days = 7)

    timeline = []
    voltage = []
    current = []
    slope = {}
    activeTime = {}
    if request.method == "POST":
        start = request.POST.get('start', False)
        end = request.POST.get('end', False)
        selectedSens = request.POST.getlist('sensorID', False)
        if selectedSens == False:
            selectedSens = []
        selectedExp = request.POST.get('experiment', False)

        #deal with inconsistent input of start time and end time
        if start:
            startT = datetime(int(start[0:4]), int(start[5:7]), int(start[8:10]))
            if(startT < end_time):
                start_time = startT
        if end:
            endT = datetime(int(end[0:4]), int(end[5:7]), int(end[8:10]))
            if endT < end_time and endT > start_time:
                end_time = endT
            if endT == start_time:
                end_time = endT+timedelta(days=1)
        start_time = start_time.replace(tzinfo=None)
        end_time = end_time.replace(tzinfo=None)

        #get test id
        if selectedExp != '':
            selectedExp = int(selectedExp)
            activeTime = getActiveTime(selectedExp, start_time, end_time)

            if selectedSens != False:
                #get selected sensors
                for i in range(0,len(selectedSens)):
                    selectedSens[i] = int(selectedSens[i])

                activeTime = getActiveTime(selectedExp, start_time, end_time)

                #for each sensor, get voltage, current and current decrease rate
                flag = True
                for sensor in selectedSens:
                    d = Energymonitor.objects.filter(nodeid = sensor).filter(exp = selectedExp)\
                    .filter(time__gte = start_time).filter(time__lte = end_time)

                    tmpslope = getSlope(sensor, exps, start_time, end_time)

                    (tmpvoltage, tmpcurrent, tmptimeline) = getVIT(sensor, selectedExp, start_time, end_time)
                    if flag:
                        timeline = map(lambda x: int(getSecs((x.replace(tzinfo=None)-datetime(1970,1,1)))*1000), tmptimeline)
                        flag = False
                    voltage.append(tmpvoltage)
                    current.append(tmpcurrent)
                    slope[sensor] = tmpslope
    return (timeline, voltage, current,userSensors, selectedSens, exps, selectedExp, slope,activeTime)

#getSensorsInfo:  retrieve necessary data for rendering the home_iframe.html
def getSensorsInfo(request):
    uid = request.user.id
    userSensors = User_Sensor.objects.filter(user_id = uid)
    allSensors = Sensor.objects.all()
    topology = Topology.objects.all()
    return (userSensors, allSensors, topology)

def getSecs(dt):
    return dt.days*24*3600+dt.seconds