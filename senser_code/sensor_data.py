# -*- coding: utf-8 -*-
from mq8 import *
from mq4 import *
from temp import *
import sys, time
import datetime as dt
import pymysql as pysql
from DB import Database

db = Database()

try:
    mq8 = MQ8()
    mq4 = MQ4()
    while True:
        perc8, perc4 = mq8.MQPercentage(), mq4.MQPercentage()
        x = dt.datetime.now()
        t = x.strftime("%Y/%m/%d %H:%M:%S")
        Value_mq8 = round(perc8["H2"], 4)
        Value_mq4 = round(perc4["CH4"], 4)
        Value_temp = ds18b20.read_temp()
        print(f"{t} H2: {Value_mq8} ppm CH4 : {Value_mq4} ppm 수온: {Value_temp}", flush=True)
        db.insert(t, Value_mq8, Value_mq4, Value_temp)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nMeasurement stopped by User")
    db.close()
except Exception as e:
    print(f"\nError: {e}\nAbort by user")
