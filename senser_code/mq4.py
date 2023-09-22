# -*- coding: utf-8 -*-
import time
import math
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


class MQ4:
    RL_VALUE = 10
    RO_CLEAN_AIR_FACTOR = 4.45
    CALIBRATION_SAMPLE_TIMES = 50
    CALIBRATION_SAMPLE_INTERVAL = 50
    READ_SAMPLE_INTERVAL = 50
    READ_SAMPLE_TIMES = 5
    GAS_CH4 = 0

    def __init__(self, Ro=10):
        self.Ro = Ro
        # create the spi bus
        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        # create the cs (chip select)
        cs = digitalio.DigitalInOut(board.D8)
        # create the mcp object
        mcp = MCP.MCP3008(spi, cs)
        # create an analog input channel on pin 2 for MQ4
        self.chan_MQ4 = AnalogIn(mcp, MCP.P7)
        self.CH4Curve = [2.3, 0.24, -0.35]  # two points are taken from the curve.
        print("Calibrating MQ-4...")
        self.Ro = self.MQ4_Calibration()
        print("Calibration of MQ-4 is done...")
        print("MQ-4 Ro=%f kohm" % self.Ro)

    def MQ4_Calibration(self):
        val = 0.0
        for i in range(self.CALIBRATION_SAMPLE_TIMES):  # take multiple samples
            val += self.MQResistanceCalculation(self.chan_MQ4.value)
            time.sleep(self.CALIBRATION_SAMPLE_INTERVAL / 1000.0)
        val = val / self.CALIBRATION_SAMPLE_TIMES  # calculate the average value
        val = (
            val / self.RO_CLEAN_AIR_FACTOR
        )  # divided by RO_CLEAN_AIR_FACTOR yields the Ro
        return val

    def MQResistanceCalculation(self, raw_adc):
        if raw_adc == 0:
            raw_adc = 1
        return float(self.RL_VALUE * (65472.0 - raw_adc) / float(raw_adc))

    def MQRead(self):
        rs = 0.0
        raw_value = 0.0
        for i in range(self.READ_SAMPLE_TIMES):
            raw_value += self.chan_MQ4.value
            rs += self.MQResistanceCalculation(self.chan_MQ4.value)
            time.sleep(self.READ_SAMPLE_INTERVAL / 1000.0)
        rs = rs / self.READ_SAMPLE_TIMES
        raw_value = raw_value / self.READ_SAMPLE_TIMES
        return rs, raw_value

    def MQPercentage(self):
        val = {}
        read, raw_value = self.MQRead()
        val["CH4"] = self.MQGetGasPercentage(read / self.Ro, self.GAS_CH4)
        val["RAW_VALUE"] = raw_value
        return val

    def MQGetGasPercentage(self, rs_ro_ratio, gas_id):
        if gas_id == self.GAS_CH4:
            return self.MQGetPercentage(rs_ro_ratio, self.CH4Curve)
        return 0

    def MQGetPercentage(self, rs_ro_ratio, pcurve):
        return math.pow(
            10, (((math.log(rs_ro_ratio) - pcurve[1]) / pcurve[2]) + pcurve[0])
        )
