#!/usr/bin/env python
import os
import sys
import git
import glob
import time
import argparse
import subprocess
import signal
import shutil
from git import RemoteProgress
from datetime import datetime
from plexapi.server import PlexServer

class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            print(message)

def execfile(filename, globals=None, locals=None):
    if globals is None:
        globals = sys._getframe(1).f_globals
    if locals is None:
        locals = sys._getframe(1).f_locals
    with open(filename, "r") as fh:
        exec(fh.read()+"\n", globals, locals)

def get_channels(channelsDir='.'):
    #get list of available channels and arrange in numerical order
    dirList = sorted(os.listdir(channelsDir))
    chanList = ['all',]
    channelsList = []
    for dir in dirList:
        if "pseudo-channel_" in dir:
            chanList.append(dir)
    for chan in chanList:
        try:
            channelNumber = chan.split('_')
            channelsList.append(channelNumber[1])
        except:
            do = "nothing"
    return channelsList

def ps_install(ps_branch='python3', path='./channels'):
    dirCheck = os.path.isdir(path)
    if dirCheck == False:
        os.mkdir('channels')
    dirList = os.listdir(path)
    installExists = False
    for item in dirList:
        if 'pseudo-channel_' in item:
            installExists = True
        else:
            installExists = False
    if installExists == True:
        print("CHANNELS DETECTED! Running Update")
        ps_update(ps_branch)
        sys.exit()        
    else:
        print("Directory "+path+" is empty. Setting up Pseudo Channel here...")
        os.chdir(path)
        os.mkdir('temp') #create temp directory to download files into
        try:
            git.Repo.clone_from('https://github.com/FakeTV/pseudo-channel', './temp', branch=ps_branch)
        except Exception as e:
            print("ERROR GETTING DOWNLOADING FROM GIT")
            print("e")
        shutil.copy('./temp/setup.py', './')
        mainFiles = glob.glob('./temp/main-dir/*')
        bothFiles = glob.glob('./temp/both-dir/*')
        srcFiles = glob.glob('./temp/both-dir/src/*')
        chanFiles = glob.glob('./temp/channel-dir/*')
        chan1Dir = 'pseudo-channel_01'
        os.mkdir(chan1Dir) #create channel 1 directory
        os.mkdir('src')
        os.mkdir(chan1Dir+'/src')
        for file in mainFiles: #copy files from temp directory into ./ and channel 1
            shutil.copy(file, './')
        for file in chanFiles:
            shutil.copy(file, './'+chan1Dir)
        for file in bothFiles:
            try:
                shutil.copy(file, './')
            except:
                do = "nothing"
            try:
                shutil.copy(file, './'+chan1Dir)
            except:
                do = "nothing"
        for file in srcFiles:
            shutil.copy(file, './src')
            shutil.copy(file, './'+chan1Dir+'/src')
        shutil.rmtree('./temp')
        print("Temp Files Deleted")
        #get number of desired channels 
        print("Enter desired number of channels")
        numberofchannels = input(">:")
        n = len(str(numberofchannels))
        if n > 2:
            newdirname = "pseudo-channel_"
            while n > 1:
                newdirname = newdirname + "0"
                n = n-1
            newdirname = newdirname + "1"
            os.rename(chan1Dir,newdirname)
            chan1Dir = newdirname
        ch = 2
        while ch <= int(numberofchannels): #copy channel 1 into remaining channels
            chNumber = str(ch).zfill(len(str(numberofchannels)))
            chPrefix = 'pseudo-channel_'
            shutil.copytree(chan1Dir, chPrefix+chNumber)
            ch = ch + 1
        print("ENTER THE PLEX SERVER URL") #get variable values and edit token and config files
        baseurl = input('http://')
        print(baseurl)
        try:
            baseSplit = baseurl.split(':')
            baseport = baseSplit[1]
        except:
            print("ENTER THE PORT NUMBER FOR THE PLEX SERVER (default: 32400)")
            baseport = input('>: ')
            if baseport == '':
                baseport = "32400"
            baseurl = baseurl + ":" + baseport
        baseurl = 'http://'+baseurl
        print("ENTER YOUR PLEX TOKEN")
        token = input('>:')
        f = open('plex_token.py', 'w+')
        now = datetime.now()
        f.write("#PLEX TOKEN FILE GENERATED "+now.strftime("%Y.%m.%d %H:%M:%S"))
        f.write("\ntoken = '"+token+"'")
        f.write("\nbaseurl = '"+baseurl+"'")
        f.close()
        PLEX = PlexServer(baseurl, token)
        print("SELECT CLIENT TO SEND PLAYBACK TO:")
        clientList = []
        clientNumbers = []
        for i, client in enumerate(PLEX.clients()):
            print(str(i + 1)+":", client.title)
            clientList.append(client.title)
            clientNumbers.append(i + 1)
        selectedClient = input('>:')
        while int(selectedClient) not in clientNumbers:
            print("ERROR: INPUT OUTSIDE OF RANGE")
            selectedClient = input('>:')
        ps_client = clientList[int(selectedClient)-1]
        # get library variables
        sections = PLEX.library.sections()
        print("LIBRARY SELECTION")
        showsSections = []
        moviesSections = []
        commercialsSections = []
        sys.stdout.flush()
        sys.stdout.write("\033[K")
        sys.stdout.write("\rScanning Libraries...")
        for section in sections:
            sys.stdout.write(".")
            if section.scanner == "Plex Series Scanner":
                showsSections.append(section.title)
            elif section.scanner == "Plex Movie Scanner":
                moviesSections.append(section.title)
            elif section.scanner == "Plex Video Files Scanner":
                commercialsSections.append(section.title)
        print("\nSelect TV Show Libraries (separate multiple entries with a comma or enter 'all')")
        ps_showslibraries = select_libs(showsSections)
        print("Select Movies Libraries (separate multiple entries with a comma or enter 'all')")
        ps_movieslibraries = select_libs(moviesSections)
        print("Use Commercial Injection? (Y/N)")
        use_commercials = input('Y/N >: ')
        responses = ['yes','y','n','no']
        while use_commercials.lower() not in responses:
            print("INVALID ENTRY")
            use_commercials = input('Y/N >: ')
        if 'y' in use_commercials.lower():
            print("Select Commercials Libraries (separate multiple entries with a comma or enter 'all')")
            ps_commercialslibraries = select_libs(commercialsSections)
            print("Enter number of seconds to pad between commercials and other media")
            commercialPadding = input('>: ')
            if commercialPadding == '':
                commercialPadding = 0
            try:
                commercialPadding = int(commercialPadding)
            except:
                print("INVALID ENTRY")
                commercialPadding = input('>: ')
        print("Enter desired reset hour (between 0 and 23)")
        print("Ideally this should be a time when someone would be least likely to be watching.")
        dailyUpdateTime = input('>: ')
        while int(dailyUpdateTime) > 23:
            print("INVALID ENTRY: Enter a number between 0 and 23")
            dailyUpdateTime = input('>: ')
        dailyUpdateTime = dailyUpdateTime+':00'
        # write to config file
        configFile = open("pseudo_config.py", 'r')
        configData = configFile.read()
        configFile = open("pseudo_config.py", 'w')
        configData = configData.replace("plexClients = []", "plexClients = [\'"+ps_client+"\']")
        configData = configData.replace("\"TV Shows\" : []", "\"TV Shows\" : "+str(ps_showslibraries))
        configData = configData.replace("\"Movies\" : []", "\"Movies\" : "+str(ps_movieslibraries))
        if 'y' in use_commercials.lower():
            configData = configData.replace("\"Commercials\" : []", "\"Commercials\" : "+str(ps_commercialslibraries))
            configData = configData.replace("commercialPadding = 1", "commercialPadding = "+str(commercialPadding))
        else:
            configData = configData.replace("useCommercialInjection = True", "useCommercialInjection = False")
        configData = configData.replace("dailyUpdateTime = \"\"", "dailyUpdateTime = \""+dailyUpdateTime+"\"")
        configFile.write(configData)
        configFile.close()
        copyconfig()
        shutil.copy('./pseudo_config.py', '../')
        shutil.copy('./plex_token.py', '../')
        global_database_update('./') #run database scan
        os.remove('../pseudo_config.py')
        os.remove('../plex_token.py')

def global_database_update(path):
    os.chdir(path)
    from channels import Global_DatabaseUpdate

def select_libs(sectionsList):
    x = 1
    for section in sectionsList:
        print(str(x)+": "+section)
        x=x+1
    libraries = input('>: ')
    go = 0
    ps_libraries = []
    if libraries.lower() == "all":
        for lib in sectionsList:
            ps_libraries.append(lib)
    elif libraries == '':
        for lib in sectionsList:
            ps_libraries.append(lib)    
    else:
        while go != 1:
            try:
                libList = libraries.split(',')
            except:
                libList = libraries
            for lib in libList:
                try:
                    lib = int(lib)
                    if lib <= x:
                        ps_libraries.append(sectionsList[lib-1])
                        go = 1
                    else:
                        print("ERROR: "+str(lib)+" Outside of Range")
                        go = 0
                except:
                    if lib not in sectionsList:
                        print("ERROR: "+ps_libraries+" Not Found")
                        go = 0
                    else:
                        ps_libraries.append(lib)
                        go = 1
            if go == 0:
                print("Errors detected, re-enter library selections")
                libraries = input('>:')
    return ps_libraries
                    
def copyconfig(channel="all"):
    #copy config file to one or more channels
    channelsList = get_channels()
    try:
        channel = int(channel)
        chanDir = "pseudo-channel_"+channelsList[channel]
        shutil.copy('./pseudo_config.py', chanDir)
    except:
        for chan in channelsList:
            if chan != "all":
                chanDir = "pseudo-channel_"+str(chan)+'/'
                shutil.copy('./pseudo_config.py', chanDir)


def copy_tv(client=None):
    print("copy_tv") #make symlinked copy of pseudo channel files to run on another client

def ps_update(branch='main'):
    print("ps_update") #download and copy updates from git to all branches and boxes
    
def web_setup(branch='main'):
    print("web_setup") #set up the web interface and api

parser = argparse.ArgumentParser(description='Pseudo Channel Controls')
try:
    channelsList = get_channels()
except:
    channelsList = []
parser.add_argument('-i', '--install',
    action='store_true',
    help='Install Pseudo Channel from git')
parser.add_argument('-cc', '--copyconfig',
    choices = channelsList,
    help='Copy root config file to one or all channels')
parser.add_argument('-tv', '--tv',
    action = 'store',
    help='Add another TV with linked database')
parser.add_argument('-u', '--update',
    choices = ['main','dev'],
    help='Update Pseudo Channel to the Latest Version')
parser.add_argument('-w', '--web',
    choices = ['main','dev'],
    help='Install and Set Up Web Interface and API')
parser.add_argument('-ud', '--updatedatabase',
    action='store_true',
    help='Generate Pseudo Channel Database')        
    
args = parser.parse_args()

if args.install:
    print("DOWNLOADING AND INSTALLING PSEUDO CHANNEL FROM GIT")
    ps_install()
if args.copyconfig:
    if args.copyconfig != 'all':
        print("COPYING CONFIG TO CHANNEL "+str(args.copyconfig))
        copyconfig(args.copyconfig)
    else:
        print("COPYING CONFIG TO ALL CHANNELS")
        copyconfig()
if args.tv:
    print("SETTING UP PSUEDO CHANNEL FOR CLIENT "+str(args.tv))
    #copy_tv(args.tv)
if args.update:
    print("UPDATING PSEUDO CHANNEL FROM GIT BRANCH "+str(args.update))
    #ps_update(args.update)
if args.web:
    print("SETTING UP PSEUDO CHANNEL WEB INTERFACE AND API FROM GIT BRANCH "+str(args.web))
    #web_setup(args.web)
if args.updatedatabase:
    global_database_update()