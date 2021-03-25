#!/usr/bin/env python
import os
import sys
import glob
import time
import argparse
import subprocess
import pseudo_config as config
import signal

OUTPUT_PID_FILE='running.pid'
OUTPUT_PID_PATH='.'
OUTPUT_LAST_FILE='last.info'


def execfile(filename, globals=None, locals=None):
    if globals is None:
        globals = sys._getframe(1).f_globals
    if locals is None:
        locals = sys._getframe(1).f_locals
    with open(filename, "r") as fh:
        exec(fh.read()+"\n", globals, locals)

def get_channels(channelsDir=os.path.abspath(os.path.dirname(__file__))):
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
    return channelsList

def get_playing():
    #check for pid file, if present, identify which channel is running
    pids = os.path.abspath(os.path.dirname(__file__))+"/**/"+OUTPUT_PID_FILE
    for runningPID in glob.glob(pids):
        with open(runningPID) as f:
            pid = f.readline()
    playing = { runningPID : pid }
    return playing

def get_last():
    #check for last file, if present identify which channel is 'last'
    lastFile = os.path.abspath(os.path.dirname(__file__))+'/**/'+OUTPUT_LAST_FILE
    print(lastFile)
    print(glob.glob(lastFile))
    for lasts in glob.glob(lastFile):
        pathtofile = lasts.split('/')
        lastDir = pathtofile[-2]
        last = lastDir.split('_')
    return last[1]

def start_channel(channel):
    #execute PseudoChannel.py -r in specified channel
    last = get_last()
    try:
        os.remove(os.path.abspath(os.path.dirname(__file__))+'/pseudo-channel_'+last+"/last.info")
        print("NOTICE: Previous last.info deleted")
    except:
        print("NOTICE: last.info not found")
    os.chdir(os.path.abspath(os.path.dirname(__file__))+'/pseudo-channel_'+channel)
    process = subprocess.Popen(["python", "-u", "PseudoChannel.py", "-r"], stdout=None, stderr=None, stdin=None)
    #create pid file and write pid into file
    print("NOTICE: Channel Process Running at "+str(process.pid))
    p = open(OUTPUT_PID_FILE, 'w+')
    p.write(str(process.pid))
    p.close()
    '''while True:
        #output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.strip())'''
    rc = process.poll()    
    
def stop_channel(channel, pid):
    #kill pid process
    '''ps_dir = channel.replace('running.pid','')
    script = os.path.abspath(os.path.dirname(__file__))+'/'+ps_dir+'PseudoChannel.py'
    print(subprocess.Popen.poll(subprocess.Popen(['python',script])))
    subprocess.Popen.terminate(subprocess.Popen(['python',script]))'''
    try:
        os.kill(int(pid), signal.SIGTERM)
        print(pid+" PID TERMINATED")
    except:
        print("PID "+pid+" NOT FOUND")
    #delete pid file
    os.remove(channel)
    print(OUTPUT_PID_FILE+" DELETED")
    #write last.info file
    lastFile = channel.replace(OUTPUT_PID_FILE, OUTPUT_LAST_FILE)
    i = open(lastFile, 'w')
    i.write(str(time.time()))
    i.close()
    print(OUTPUT_LAST_FILE+" CREATED")
    
def stop_all_boxes():
    #get list of boxes
    #get list of channels in box
    #stop all channels in box
    print("stop_all_boxes FUNCTION NOT YET IMPLEMENTED")
    
def channel_up(channelsList):
    #play next channel in numerical order
    try:
        getPlaying = get_playing()
        for channelPlaying, pid in getPlaying.items():
            channelNumber = channelPlaying.replace('pseudo-channel_','')
            channelNumber = channelNumber.replace('/'+OUTPUT_PID_FILE,'')
            channelNumber = channelNumber.split('/')[-1]
            print("NOTICE: Stopping Channel "+str(channelNumber)+" at PID "+str(pid))
            stop_channel(channelPlaying, pid)
    except:
        print("NOTICE: Channel not playing or error")
        channelPlaying = get_last()
    isnext = 0
    next_channel = channelsList[0]
    for channel in channelsList:
        if isnext == 1:
            next_channel = channel
            break
        if channel == channelNumber:
            isnext = 1
    print("NOTICE: Starting Channel "+str(next_channel))
    start_channel(next_channel)
    
def channel_down(channelsList):
    #play previous channel in numerical order
    try:
        getPlaying = get_playing()
        for channelPlaying, pid in getPlaying.items():
            channelNumber = channelPlaying.replace('pseudo-channel_','')
            channelNumber = channelNumber.replace('/'+OUTPUT_PID_FILE,'')
            channelNumber = channelNumber.split('/')[-1]
            print("NOTICE: Stopping Channel "+str(channelNumber)+" at PID "+str(pid))
            stop_channel(channelPlaying, pid)
    except:
        print("NOTICE: Channel not playing or error")
        channelPlaying = get_last()
    isnext = 0
    channelsList.reverse()
    next_channel = channelsList[0]
    for channel in channelsList:
        if isnext == 1:
            next_channel = channel
            break
        if channel == channelNumber:
            isnext = 1
    print("NOTICE: Starting Channel "+str(next_channel))
    start_channel(next_channel)
    
def generate_daily_schedules(channelsList):
    #execute PseudoChannel.py -g in specified channel
    print("GENERATING DAILY SCHEDULES FOR ALL CHANNELS")
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    process = subprocess.Popen(["python", "-u", "Global_DailySchedule.py"], stdout=None, stderr=None, stdin=None)
    '''for channel in channelsList:
        os.chdir(os.path.abspath(os.path.dirname(__file__))+'/pseudo-channel_'+channel)
        print("GENERATING SCHEDULE FOR CHANNEL "+channel)
        process = subprocess.call(["python", "-u", "PseudoChannel.py", "-g"], stdout=None, stderr=None, stdin=None)
        os.chdir('../')
    print("ALERT: ALL DAILY SCHEDULE GENERATION COMPLETE")'''
        
def global_database_update():
    print("UPDATING PSEUDO CHANNEL DATABASE FROM PLEX SERVER")
    #import Global_DatabaseUpdate
    workingDir = os.path.abspath(os.path.dirname(__file__))
    os.chdir(workingDir)
    print("NOTICE: Working directory changed to "+workingDir)
    process = subprocess.Popen(["python", "-u", "Global_DatabaseUpdate.py"], stdout=None, stderr=None, stdin=None)

parser = argparse.ArgumentParser(description='Pseudo Channel Controls')
channelsList = get_channels()
#channel, pid = playing.popitem()
parser.add_argument('-c', '--channel',
    choices = channelsList,
    help='Start Specified Channel')
parser.add_argument('-s', '--stop',
    action='store_true',
    help='Stop Active Channel')
parser.add_argument('-sb', '--stopallboxes',
    action='store_true',
    help='Stop All Clients')
parser.add_argument('-up', '--channelup',
    action='store_true',
    help='Channel Up')
parser.add_argument('-dn', '--channeldown',
    action='store_true',
    help='Channel Down')
parser.add_argument('-l', '--last',
    action='store_true',
    help='Last Channel')
parser.add_argument('-r', '--restart',
    action='store_true',
    help='Restart Playing Channel')    
parser.add_argument('-g', '--generateschedules',
    action='store_true',
    help='Generate Daily Schedules for All Channels')
parser.add_argument('-u', '--updatedatabase',
    action='store_true',
    help='Generate Pseudo Channel Database')      
    
args = parser.parse_args()

if args.channel:
    print("STARTING CHANNEL "+args.channel)
    start_channel(args.channel)
if args.stop:
    playing = get_playing()
    for channel, pid in playing.items():
        print("STOPPING CHANNEL "+channel.replace('/running.pid','').split('_')[1])
        stop_channel(channel, pid)
if args.stopallboxes:
    print("STOPPING ALL BOXES")
    stop_all_boxes()
if args.channelup:
    print("CHANNEL UP")
    channel_up(channelsList)
if args.channeldown:
    print("CHANNEL DOWN")
    channel_down(channelsList)
if args.last:
    print("LAST CHANNEL")
    last = get_last()
    start_channel(last)
if args.restart:
    playing = get_playing()
    for channel, pid in playing.items():
        stop_channel(channel, pid)
        print("STOPPING ACTIVE CHANNEL AT PID "+pid)
    last = get_last()
    print("RESTARTING CHANNEL "+last)
    start_channel(last)    
if args.generateschedules:
    try:
        playing = get_playing()
        for channel, pid in playing.items():
            print("STOPPING CHANNEL "+channel.replace('/running.pid','').split('_')[1])
            stop_channel(channel, pid)
        last = get_last()
        print("GENERATING DAILY SCHEDULES")
        generate_daily_schedules(channelsList)
        print("RESTARTING CHANNEL "+last)
        start_channel(last)
    except:
        print("GENERATING DAILY SCHEDULES")
        generate_daily_schedules(channelsList)
if args.updatedatabase:
    global_database_update()