#this model renders the responding web page

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
import sqlweb

#render home.html
@login_required
def home(request):
    return render_to_response('monitor/home.html', {})

#render linewithfocuschart.html
@login_required
def linewithfocuschart(request):
    (time, voltage, current, userSensors, selectedSens, exps, selectedExp,slope,activeTime) = sqlweb.getData(request)
    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_seriev = {"tooltip": {"y_start": "", "y_end": ""},
                   "date_format": tooltip_date}
    extra_seriei = {"tooltip": {"y_start": "", "y_end": ""},
                   "date_format": tooltip_date}

    chartdatav = {'x': time}
    for i in range(0,len(selectedSens)):
        chartdatav['name'+str(i+1)] = 'Voltage-'+str(selectedSens[i])
        chartdatav['y'+str(i+1)] = voltage[i]
        chartdatav['extra'+str(i+1)] = extra_seriev

    chartdatai = {'x': time}
    for i in range(0,len(selectedSens)):
        chartdatai['name'+str(i+1)] = 'Current-'+str(selectedSens[i])
        chartdatai['y'+str(i+1)] = current[i]
        chartdatai['extra'+str(i+1)] = extra_seriei

    charttypev = "lineWithFocusChart"
    charttypei = "lineWithFocusChart"
    chartcontainerv = 'linewithfocuschart_containerv'  # container name
    chartcontaineri = 'linewithfocuschart_containeri'

    data = {
        'charttypev': charttypev,
        'charttypei': charttypei,
        'chartdatav': chartdatav,
        'chartdatai': chartdatai,
        'chartcontainerv': chartcontainerv,
        'chartcontaineri': chartcontaineri,
        'extrav': {
            'x_is_date': True,
            'x_axis_format': '%d %b %Y %H',
            'tag_script_js': True,
            'jquery_on_ready': True,
        },
         'extrai': {
            'x_is_date': True,
            'x_axis_format': '%d %b %Y %H',
            'tag_script_js': True,
            'jquery_on_ready': True,
        },
        'userSensors':userSensors,
        'selectedSens':selectedSens,
        'exps':exps,
        'selectedExp':selectedExp,
        'slopes': slope,
        'activeTime':activeTime
    }
    data.update(csrf(request))
    return render_to_response('monitor/linewithfocuschart.html', data)

@login_required
def data(request):
    return render_to_response('monitor/data.html', {})

#render home_iframe.html
@login_required
def home_iframe(request):
    if request.method == 'POST':
        addid = request.POST.getlist('add', False)
        if addid != False:
            sqlweb.addSensor(addid, request)
        delid = request.POST.getlist('delete', False)
        if delid != False:
             sqlweb.delSensor(delid, request)
    (userSensors, allSensors, topology) = sqlweb.getSensorsInfo(request)
    userSensorsID = [us.sensor_id for us in userSensors]
    notUserSensors = [s for s in allSensors if s.sensor_id not in userSensorsID]
    userSensors = [s for s in allSensors if s.sensor_id in userSensorsID]
    data = {
        'allSensors':allSensors,
        'userSensors':userSensors,
        'notUserSensors':notUserSensors,
        'topology':topology
    }
    data.update(csrf(request))
    return render_to_response('monitor/home_iframe.html', data)

