# -*- coding: utf-8 -*-
import spidev
import time
import datetime as dt
import pymysql as pysql
from mcpsensor.DB import Database

db = Database()


# spi 통신 설정
def init_mq8():
    global spi_mq8
    spi_mq8 = spidev.SpiDev()
    spi_mq8.open(0, 0)
    spi_mq8.max_speed_hz = 500000


def init_mq4():
    global spi_mq4
    spi_mq4 = spidev.SpiDev()
    spi_mq4.open(0, 0)
    spi_mq4.max_speed_hz = 500000


# spi 채널 설정 및 ADC변환
def read_spi_adc_mq8(adcChannel):
    adcValue = 0
    buff = spi_mq8.xfer2([1, (8 + adcChannel) << 4, 0])
    adcValue = ((buff[1] & 3) << 8) + buff[2]
    return adcValue


def read_spi_adc_mq4(adcChannel):
    adcValue = 0
    buff = spi_mq4.xfer2([1, (8 + adcChannel) << 4, 0])
    adcValue = ((buff[1] & 3) << 8) + buff[2]
    return adcValue


init_mq8()
init_mq4()
try:
    while True:
        adcChannel_mq8 = 0  # ch0
        adcChannel_mq4 = 7  # ch7
        Value_mq8 = read_spi_adc_mq8(adcChannel_mq8)
        Value_mq4 = read_spi_adc_mq4(adcChannel_mq4)
        x = dt.datetime.now()
        t = x.strftime("%Y/%m/%d %H:%M:%S")
        db.insert(t, Value_mq8, Value_mq4)  # 센서값 DB에 입력

        print(f"{t} H2 : {Value_mq8}, CH4  : {Value_mq4}")
        time.sleep(1)
except KeyboardInterrupt:
    spi_mq8.close()
    spi_mq4.close()
    db.close()
