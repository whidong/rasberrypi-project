import os
import time

class ds18b20:
    ## ds18b20 온도데이터값을 아래 temp_sensor 경로에 저장하기 위한 명령어
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm') 
        
    
    # 라즈베리파이가 센서데이터를 받는 경로를 설정합니다. (각자 비슷한 경로를 찾아보셔야 합니다)

    def read_temp():
        temp_sensor='/sys/bus/w1/devices/28-3de1045705f2/w1_slave'
        f = open(temp_sensor, 'r')
        lines = f.readlines()
        f.close()
        temp_output = lines[1].find('t=')

        if temp_output != -1:
            temp_string = lines[1].strip()[temp_output+2:]
            temp_c = float(temp_string)/1000
            return temp_c
        




print(ds18b20.read_temp())