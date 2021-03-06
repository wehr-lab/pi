import RPi.GPIO as GPIO
import os
import sys
from time import gmtime, strftime, sleep
import video_record as vid
import time
import pickle
from datetime import datetime
import json
#from picamera import PiCamera
#camera1=PiCamera()

# Set GPIO mode - determines how pins are numbered
GPIO.setmode(GPIO.BOARD)

# TODO: Make sure connected pin matches this one
on_pin  = 7
off_pin = 11
SCT_pin= 13
SCT=[];
  
# Base directory for recording, hardcoded for now
base_dir = '/home/pi/Videos'


def start_listener(on_pin, off_pin, SCT_pin):
    # Setup in for listening, set to be pulled down initially
    GPIO.setup(on_pin,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(off_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(SCT_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Give the pin callbacks
    GPIO.add_event_detect(on_pin,  GPIO.RISING, bouncetime=200)
    GPIO.add_event_detect(off_pin, GPIO.RISING, bouncetime=200)
    GPIO.add_event_detect(SCT_pin, GPIO.RISING, bouncetime=100)

if __name__ == "__main__" and __package__ is None:
    start_listener(on_pin, off_pin, SCT_pin)
    camera = vid.init_camera(vid.CONF_FILE)
    camera.crop=(.25, .25, .5, .5)
    camera.vflip= "True"
    camera.hflip= "True"
    camera.shutter_speed=6000
    camera.framerate=30
    # camera.contrast=80
    #camera.contrast=-15
    camera.iso = 1000
    #camera.brightness=70
    camera.exposure_compensation=25
    camera.exposure_mode='nightpreview'    

    print("Initialized camera")

    # Just chill and wait for some input
    while True:
        # Check every 1s if we've gotten a signal
        sleep(0.0001)
        
        if GPIO.event_detected(on_pin):
            time_string = strftime("%Y-%m-%d_%H-%M-%S",time.localtime())
            base_dir = '/home/pi/Videos'
	    vfile = os.path.join(base_dir,"".join(['pupil_',time_string, '.h264']))
            print(vfile)
            camera.start_recording(vfile, format='h264')
            c=datetime.now()
            c=str(c)
            SCT=[]
            SCT.append(c)
            print("Started recording video to {}".format(vfile))
            camera.start_preview()

        if GPIO.event_detected(SCT_pin):
            c=datetime.now()
            c=str(c)
            SCT.append(c)

        if GPIO.event_detected(off_pin):
            camera.stop_recording()
            c=datetime.now()
            c=str(c)
            SCT.append(c)
            print("Stopped recording at {}".format(strftime("%H-%M-%S",time.localtime())))
            camera.stop_preview()
            vfile2=os.path.join(base_dir,"".join([time_string,'.mp4']))
            print(vfile)
            print(vfile2)
            #os.chdir('Videos')
            os.system(" MP4Box -add {} {} ".format(vfile,vfile2))
            os.system("rm {}".format(vfile)) 

            name=os.path.join(base_dir,"".join([time_string,'.txt']))
            print('Detected SCTs, saving in {}'.format(name))
            print(SCT)
            #os.chdir('Videos')   
            with open(name, 'w') as f:
                json.dump(SCT, f, ensure_ascii=False)
                print('saved SCTs in {}'.format(name))
            
            SCT=[]
