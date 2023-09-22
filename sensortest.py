# -*- coding: utf-8 -*-
import spidev
import time
import datetime as dt
import math


# spi 통신 설정
def init_mq8():
    global spi_mq8
    spi_mq8 = spidev.SpiDev()
    spi_mq8.open(0, 0)
    spi_mq8.max_speed_hz = 500000


# spi 채널 설정 및 ADC변환
def read_spi_adc_mq8(adcChannel):
    adcValue8 = 0
    buff = spi_mq8.xfer2([1, (8 + adcChannel) << 4, 0])
    adcValue8 = ((buff[1] & 3) << 8) + buff[2]
    return adcValue8


# spi 통신 설정
def init_mq4():
    global spi_mq4
    spi_mq4 = spidev.SpiDev()
    spi_mq4.open(0, 0)
    spi_mq4.max_speed_hz = 500000


# spi 채널 설정 및 ADC변환
def read_spi_adc_mq4(adcChannel):
    adcValue4 = 0
    buff = spi_mq4.xfer2([1, (8 + adcChannel) << 4, 0])
    adcValue4 = ((buff[1] & 3) << 8) + buff[2]
    return adcValue4


def sensor_value():
    adcChannel_mq8 = 0  # ch0
    adcChannel_mq4 = 7  # ch7
    return read_spi_adc_mq8(adcChannel_mq8), read_spi_adc_mq4(adcChannel_mq4)


#  Calculate Rs
def rs_cal(vl):
    return (vcc * (1023 - vl)) // vl


# Calculate PPM
def ppm_cal(ratio, a, b):
    return a * pow(ratio, b)


# Calculate logscale PPM
def ppm_log_cal(ratio, a, b, c):
    return pow(10, ((math.log10(ratio) - b) // a) + c)


"""
PPM 
VCC = 3.3V
RL = 10k

VL = VCC*(RL/(RS+RL)
RS = (RL*VCC)/VL-RL

PPM = a * ratio * b
"""
vcc = 5
rl = 10
constant = {
    "mq4": ["CH4", "mq4", 1012.7, -2.786],
    "mq8": ["H2", "mq8", 976.97, -0.688],
    "CH4Curve": ["CH4", "mq4", 2.3, 0.24, -0.35],
    "H2Curve": ["H2", "mq8", 2.3, 0.93, -1.44],
}

init_mq8()
init_mq4()
# Ro 값을 구하기위해 Rs값을 10번 구해서 평균값 구함(calibration)
r0_mq8, r0_mq4 = 0, 0
for i in range(0, 10):  # Calculate Ro
    v_mq8, v_mq4 = sensor_value()
    print(sensor_value())
    v_mq8, v_mq4 = rs_cal(v_mq8), rs_cal(v_mq4)
    r0_mq8 += v_mq8 / 9.21
    r0_mq4 += v_mq4 / 4.45
    print(f"\rcalibrating...{i+1}초", end="", flush=True)
    time.sleep(1)
print("calibration is done...")
r0_mq8 = r0_mq8 / 10
r0_mq4 = r0_mq4 / 10
print(f"R0_mq8={r0_mq8} R0_mq4={r0_mq4}")
try:
    while True:
        rs_mq8, rs_mq4 = sensor_value()
        rs_mq8 = rs_cal(rs_mq8)
        rs_mq4 = rs_cal(rs_mq4)
        ratio_mq8 = rs_mq8 / r0_mq8
        ratio_mq4 = rs_mq4 / r0_mq4
        Value_mq8 = round(
            ppm_log_cal(
                ratio_mq8,
                constant["H2Curve"][4],
                constant["H2Curve"][3],
                constant["H2Curve"][2],
            ),
            2,
        )
        Value_mq4 = round(ppm_cal(ratio_mq4, constant["mq4"][2], constant["mq4"][3]), 2)
        x = dt.datetime.now()
        t = x.strftime("%Y/%m/%d %H:%M:%S")
        print(f"{t} H2 : {Value_mq8}, CH4  : {Value_mq4}")
        time.sleep(1)
except KeyboardInterrupt:
    spi_mq8.close()
    spi_mq4.close()
