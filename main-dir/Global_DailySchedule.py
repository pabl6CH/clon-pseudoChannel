#!/usr/bin/env python
import os
import subprocess

channelsDir=os.path.abspath(os.path.dirname(__file__))
#get list of available channels and arrange in numerical order
dirList = sorted(next(os.walk(channelsDir))[1])
chanList = []
channelsList = []
for dir in dirList:
    if "pseudo-channel_" in dir:
        chanList.append(dir)
for chan in chanList:
    channelNumber = chan.split('_')
    channelNumber = channelNumber[1]
    channelsList.append(channelNumber)
    
#execute PseudoChannel.py -g in specified channel
os.chdir(os.path.abspath(os.path.dirname(__file__)))
for channel in channelsList:
    os.chdir(os.path.abspath(os.path.dirname(__file__))+'/pseudo-channel_'+channel)
    print("GENERATING SCHEDULE FOR CHANNEL "+channel)
    process = subprocess.call(["python3", "-u", "PseudoChannel.py", "-g"], stdout=None, stderr=None, stdin=None)
    os.chdir('../')
print("ALERT: ALL DAILY SCHEDULE GENERATION COMPLETE")