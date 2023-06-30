import numpy as np
import cv2
import time
from datetime import datetime
from timeit import default_timer
from PIL import Image
import csv

import argparse
import serial
import random

import os
import pandas as pd


## SERIAL PORT SETTING
ser = serial.Serial('COM7', 115200)
print(ser.name)

## IR KEYS FOR CONTROL
P_TOG=b'mc 00 08\n'
P_ON = b'ka 00 01\n'
P_OFF = b'ka 00 00\n'
ChUp = b'mc 00 00\n'
ChDown = b'mc 00 01\n'

VolUp = b'mc 00 02\n'
VolDown = b'mc 00 03\n'

DpadUp = b'mc 00 40\n'
DpadDn = b'mc 00 41\n'
DpadLt = b'mc 00 07\n'
DpadRt = b'mc 00 06\n'

Back =  b'mc 00 28\n'
Home = b'mc 00 7C\n'
OK = b'mc 00 44\n'

Num_00 =b'mc 00 10\n'
Num_01 =b'mc 00 11\n'
Num_02 =b'mc 00 12\n'
Num_03 =b'mc 00 13\n'
Num_04 =b'mc 00 14\n'
Num_05 =b'mc 00 15\n'
Num_06 =b'mc 00 16\n'
Num_07 =b'mc 00 17\n'
Num_08 =b'mc 00 18\n'
Num_09 =b'mc 00 19\n'

RED=b'mc 00 72\n'
GRN=b'mc 00 71\n'
YEL=b'mc 00 63\n'
BLU=b'mc 00 61\n'

#####################################
## Setup Parameter
#####################################
#   camera input
input_loc = 1

#   threshold for brigtness to stop
gray_threshold = 50

#   total repeatition 
Loop=1
SOC='LG_Channel_'
CP = 'V031130_230630_O22N_'

"""
##Turning On the Power
ser.write(P_ON)
print ("Sending Power ON. Wait until the system settle down")

time.sleep(3)

ser.write(Home)
print("sending Home")
time.sleep(5)

ser.write(OK)
print("Selecting LG Channel")
time.sleep(5)

ser.write(OK)
print("Streaming Initiation")
time.sleep(5)
"""




while(Loop<300):
    

    ser.write(ChUp)
    nowOK = datetime.now()
    start = time.time()
    
    count = 0
    cap = cv2.VideoCapture(0)
    comp=[]
    
    
    motherDirectory = "C:/Temp/"
    directory_path = motherDirectory + SOC + str(CP)+ str(Loop)
    
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)
        print(directory_path+" was created...")
    
    output_loc =  directory_path


    
    ## GETTING IMAGES
    while (True):
        
        ret, frame = cap.read()
       
        ##App Started 
        now = datetime.now()
        current=time.time()

        ##Turning Image Frame to GrayScale
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        
        """
        nowHour=now.hour-now_init.hour
        nowMinute=now.minute-now_init.minute
        nowSecond=now.second-now_init.second
        nowMicrosecond=now.microsecond-now_init.microsecond
        """
        
        elapsedTime = (current-start)*1000
        
        #print ( str((current-start)*1000) + "miliseconds")
        
        kernel = np.ones((1,1), np.uint8)
        image=gray
        image = cv2.dilate(image,kernel,iterations=1)
        image = cv2.erode(image,kernel,iterations=1)
        meanValue = image.mean()
        
        font=0
        bottomLeftCornerOfText = (10,400)
        fontScale = 0.4
        fontColor = (255,255,255)
        lineType = 1

        cv2.putText(image, "Elapsed : %dmS, T1 = %d:%d:%d:%d, T0 = %d:%d:%d:%d, MeanValue : %d"%(elapsedTime, now.hour, now.minute, now.second, now.microsecond, nowOK.hour, nowOK.minute, nowOK.second, nowOK.microsecond, meanValue ),bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        cv2.imshow('frame', image)


        cv2.imwrite(output_loc + "/%#05d_.jpg" % (count+1), image)
        count+=1
        
        ## Timer Check
        #comp[count]=meanValue
        #meanValue = image.mean()
        
        #print ("Mean Value of the image is : ", meanValue)

        
        #print(meanValue[count],"meanTest")
        
        comp.append(meanValue)
        
        if count >5:
            #print("count is over 20")
            
            if  (((round(comp[len(comp)-1])) - (round(comp[count-4]))==0 ) and (meanValue>=gray_threshold)):
                #if ((comp[len(comp)-1]) - (comp[len(comp)-7]) <= 1 ):
                #print((comp[len(comp)-1]), round(comp[len(comp)-4]), meanValue)
                time.sleep(2)
                #print(round(comp[len(comp)-1]), round(comp[len(comp)-4]), meanValue)
                print ("Moving To Next Channel")
                channelNumber = Loop
                new_data = {'Channel':[channelNumber], 'Delay':elapsedTime}
                
                new_df = pd.DataFrame(new_data)
                with open('output.csv', 'a') as f:
                    for index, row in new_df.iterrows():
                        f.write(f"{row['Channel']}, {row['Delay']}\n")
                        print(row)
                time.sleep(8)
                break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    time.sleep(7)
    Loop+=1