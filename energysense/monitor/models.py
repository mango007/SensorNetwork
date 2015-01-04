from django.db import models
#This model map each tale in database to a class in django framwork

class Sensor(models.Model):
    sensor_id = models.IntegerField(primary_key=True)
    last_connected_time = models.DateTimeField()
    initial_energy = models.FloatField()
    remaining_energy = models.FloatField()
    is_base_station = models.IntegerField()
    last_voltage = models.FloatField()
    x = models.IntegerField()
    y = models.IntegerField()

class User_Sensor(models.Model):
    user_id = models.IntegerField()
    sensor_id = models.IntegerField()

class Energymonitor(models.Model):
    nodeid = models.IntegerField(db_column='NodeID') # Field name made lowercase.
    time = models.DateTimeField(db_column='Time') # Field name made lowercase.
    voltage = models.FloatField(db_column='Voltage') # Field name made lowercase.
    cumcurr = models.FloatField(db_column='CumCurr') # Field name made lowercase.
    data = models.CharField(db_column='Data', max_length=40) # Field name made lowercase.
    exp = models.IntegerField(db_column='Experiment')
    class Meta:
        managed = False
        db_table = 'EnergyMonitor'

class Topology(models.Model):
    sensorID1 = models.IntegerField()
    sensorID2 = models.IntegerField()

class ActiveBS(models.Model):
    starttime = models.DateTimeField(db_column = 'StartTime')
    endtime = models.DateTimeField(db_column = 'EndTime')
    nodeid = models.IntegerField(db_column = 'NodeID')
    exp = models.IntegerField(db_column = 'Experiment')
    class Meta:
        managed = False
        db_table = 'ActiveBS'

