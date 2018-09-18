import RPi.GPIO as GPIO
import spidev
import time
import os
import sys  
from datetime import datetime
from os import system

spi = spidev.SpiDev()
spi.open(0,0)

count = 1
frequ = 0.5
stop_pressed = True
play = True
start = time.time()
dataArray = [0,0,0]
i = 0

def GetData(channel):
    spi.max_speed_hz = 1350000
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3)<<8)+adc[2]
    return data

def ConvertVolts(data,places):
    volts = (data*3.3)/float(1023)
    volts = round(volts,places)
    return volts

def PotVolts(data,places):
    v = ConvertVolts(data,places)
    return v

def ConvertTemp(data,places):
    volt = ConvertVolts(data,places)
    Temp = (volt-0.5)/0.01
    Temp = round(Temp,places)
    return Temp

def LightPercent(data,places): #convert light intensity to a percentage
    V = ConvertVolts(data,places)
    Percent = ((3-V)/3)*100
    return Percent

start = time.time()

def timer_string():
    global start
    now = time.time() - start

    m,s = divmod(now,60)
    h,m = divmod(m,60)

   
    timer_str = "%02d:%02d:%02d"%(h,m,s)
    psec = str(now - int(now))
    pstr = psec[1:5]
    timer_str = timer_str + str(pstr)

    return timer_str
    
    

def data_print():

    
    CH0 = 0
    CH1 = 1
    CH2 = 2
    CH0_Data = GetData(CH0)
    CH0_Temp = ConvertTemp(CH0_Data,2)
    CH1_Data = GetData(CH1)
    CH1_Light = LightPercent(CH1_Data,0)
    CH2_Data = GetData(CH2)
    CH2_Pot = PotVolts(CH2_Data,0)
    CH1_string = str(int(CH1_Light))+"%"
    sys.stdout.flush()
    
    data =("{CH2_Pot}V    {CH0_Temp}C    {CH1_string}".format(CH2_Pot=CH2_Pot,CH0_Temp=CH0_Temp,CH1_string=CH1_string))
    return data

# string for time
def time_string():
    
    time_start = time.time()
    real_time = time.localtime()
    h = real_time.tm_hour
    m = real_time.tm_min
    s = real_time.tm_sec
    #get current date and time
    tstring = "%02d:%02d:%02d"%(h,m,s)

    time_str = str(tstring)
    

    return time_str
    


def my_callback(push1):
    
    print("reset1")
    
    #resseting timeer to 0
    global start
    start = time.time()
    os.system("clear")
    
    
    print("\n"*40)


def my_callback1(push2): 
    print("Stop switch pressed")
    global play
    play = not play
    

def my_callback2(push2):
    print("frequency button")
    global count
    global frequ
    print(frequ)
    count+=1
    
    if count > 3:
        count = 1

    if count ==1: #initial frequency
        frequ = 0.5

    elif count ==2: #2nd frequency
        frequ =1

    elif count ==3: #3rd frequency
        frequ = 2



def my_callback3(push4): 
    global dataArray
    k = -1
    for t in range(0,5):
        global dataArray
        global i
        time_str = time_string()
        timer_str = timer_string()
        data = data_print()
        dataArray.append(data)
        dataArray.append(data)
        info = dataArray[0 + k]
        print("{time_str}     {timer_str}      {info} ".format(time_str=time_str,timer_str=timer_str , info = info))
        time.sleep(frequ)
        k -=1

def main():
#using the BCM pinout
    GPIO.setmode(GPIO.BCM)      

    
    push1 = 2
    push2 = 3
    push3 = 4
    push4 = 21

    GPIO.setup(push1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(push2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(push3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(push4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.add_event_detect(push1, GPIO.FALLING, callback=my_callback, bouncetime=500) 
    GPIO.add_event_detect(push2, GPIO.FALLING, callback=my_callback1, bouncetime=500)
    GPIO.add_event_detect(push3, GPIO.FALLING, callback=my_callback2, bouncetime=500)
    GPIO.add_event_detect(push4, GPIO.FALLING, callback=my_callback3, bouncetime=500)

    print("Time    |      Timer    |     Pot   |    Temp    |  Light")
    print("-------------------------------------------------------")
    
    while (True):

        
        while (play):
            global dataArray
            global i
            time_str = time_string()
            timer_str = timer_string()
            data = data_print()
            dataArray.append(data)
            i += 1
            dataArray.append(data)
            info = dataArray[0 + i]
            print("{time_str}     {timer_str}      {info} ".format(time_str=time_str,timer_str=timer_str , info = info))
            time.sleep(frequ)

if __name__ == "__main__":
    main()
