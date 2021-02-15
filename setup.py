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
    dirList = sorted(next(os.walk('.'))[1])
    chanList = ['all',]
    channelsList = []
    for dir in dirList:
        if "pseudo-channel_" in dir:
            chanList.append(dir)
    for chan in chanList:
        channelNumber = chan.split('_')
        channelNumber = channelNumber[1]
        channelsList.append(channelNumber)
    return channelsList

def ps_install(ps_branch='python3', path='./channels'):
    dirCheck = os.path.isdir(path)
    if dirCheck == False:
        os.mkdir('channels')
    dirList = os.listdir(path)
    if 'pseudo-channel_' in dirList:
        print("CHANNELS DETECTED! Running Update")
        ps_update(branch)
        sys.exit()        
    else:
        print("Directory "+path+" is empty. Setting up Pseudo Channel here...")
        os.chdir(path)
        os.mkdir('temp') #create temp directory to download files into
        try:
            git.Repo.clone_from('https://github.com/FakeTV/pseudo-channel', './temp', branch=ps_branch, progress=CloneProgress())
        except Exception as e:
            print("ERROR GETTING DOWNLOADING FROM GIT")
            print("e")
        shutil.copy('./temp/setup.py', './')
        mainFiles = glob.glob('./temp/main-dir/*')
        bothFiles = glob.glob('./temp/both-dir/*')
        srcFiles = glob.glob('./temp/both-dir/src/*')
        os.mkdir('pseudo-channel_01') #create channel 1 directory
        os.mkdir('src')
        os.mkdir('pseudo-channel_01/src')
        for file in mainFiles: #copy files from temp directory into ./ and channel 1
            shutil.copy(file, './')
        for file in bothFiles:
            shutil.copy(file, './')
            shutil.copy(file, './pseudo-channel_01')
        for file in srcFiles:
            shutil.copy(file, './src')
            shutil.copy(file, './pseudo-channel_01/src')
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
            os.rename('pseudo-channel_01',newdirname)
        ch = 2
        while ch <= int(numberofchannels): #copy channel 1 into remaining channels
            chNumber = str(ch).zfill(len(str(numberofchannels)))
            chPrefix = 'pseudo-channel_'
            shutil.copytree('pseudo-channel_01', chPrefix+chNumber)
            ch = ch + 1
    print("ENTER THE PLEX SERVER URL") #get variable values and edit token and config files
    baseurl = 'http://'+input('http://')
    try:
        baseSplit = baseurl.split(':')
    except:
        print("ENTER THE PORT NUMBER FOR THE PLEX SERVER (default: 32400")
        baseport = input('>:')
        if baseport == '':
            baseport = "32400"
        baseurl = baseurl + baseport
    print("ENTER YOUR PLEX TOKEN")
    token = input('>:')
    f = open('plex_token.py', 'w+')
    now = datetime.now()
    f.write("#PLEX TOKEN FILE GENERATED "+now.strftime("%Y.%m.%d %H:%M:%S"))
    f.write("token = "+token)
    f.write("baseurl = "+baseurl)
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
    while selectedClient not in clientNumbers:
        print("ERROR: INPUT OUTSIDE OF RANGE")
        selectedClient = input('>:')
    ps_client = clientList[int(selectedClient)-1]
    # get library variables
    sections = PLEX.library.sections()
    print("LIBRARY SELECTION")
    showsSections = []
    moviesSections = []
    commercialsSections = []
    for section in sections:
        sys.stdout.write("\033[K")
        sys.stdout.write("Scanning Libraries... ["+section.title+"]")
        if section.scanner == "Plex Series Scanner":
            showsSections.append(section.title)
        elif section.scanner == "Plex Movie Scanner":
            moviesSections.append(section.title)
        elif section.scanner == "Plex Video Files Scanner":
            commercialsSections.append(section.title)
    sys.stdout.write("\033[K")
    print("Select TV Show Libraries (separate multiple entries with a comma or enter 'all')")
    ps_showslibraries = select_libs(showsSections)
    print("Select Movies Libraries (separate multiple entries with a comma or enter 'all')")
    ps_movieslibraries = select_libs(moviesSections)
    print("Use Commercial Injection? (Y/N)")
    use_commercials = input('Y/N >:')
    responses = ['yes','y','n','no']
    while use_commercials.lower() not in responses:
        print("INVALID ENTRY")
        use_commercials = input('Y/N >:')
    if 'y' in use_commercials.lower():
        print("Select Commercials Libraries (separate multiple entries with a comma or enter 'all')")
        ps_commercialslibraries = select_libs(commercialsSections)
        print("Enter number of seconds to pad between commercials and other media")
        commercialPadding = input('>:')
        if commercialPadding == '':
            commercialPadding = 0
        try:
            commercialPadding = int(commercialPadding)
        except:
            print("INVALID ENTRY")
            commercialPadding = input('>:')
    print("Enter desired daily schedule reset time using H:MM time formatting (ideally this should be a time when someone would be least likely to be watching)")
    dailyUpdateTime = input('>:')
    # write to config file
    configFile = open("pseudo_config.py", 'w+')
    configData = configFile.read()
    configData = configData.replace("plexClients = []", "plexClients = ["+ps_client+"]")
    configData = configData.replace("\"TV Shows\" : []", "\"TV Shows\" : "+ps_showslibraries)
    configData = configData.replace("\"Movies\" : []", "\"Movies\" : "+ps_movieslibraries)
    if 'y' in use_commercials.lower():
        configData = configData.replace("\"Commercials\" : []", "\"Commercials\" : "+ps_commercialslibraries)
        configData = configData.replace("commercialPadding = 1", "commercialPadding = "+commercialPadding)
    else:
        configData = configData.replace("useCommercialInjection = True", "useCommercialInjection = False")
    configData = configData.replace("dailyUpdateTime = \"\"", "dailyUpdateTime = \""+dailyUpdateTime+"\"")
    configFile.write(configData)
    configFile.close()
    copyconfig()

def select_libs(sectionsList):
    x = 1
    for section in sectionsList:
        print(str(x)+": "+section)
        x+1
    libraries = input('>:')
    go = 0
    if libraries == "all":
        ps_libraries = sectionsList
    else:
        ps_libraries = []
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
        sys.stdout.write("\033[K")
        sys.stdout.write("Copying config to channel "+channelsList[channel])        
        chanDir = "pseudo-channel_"+channelsList[channel]
        shutil.copy('./pseudo_config.py', chanDir)
    except:
        for chan in channelsList:
            if chan != "all":
                sys.stdout.write("\033[K")
                sys.stdout.write("Copying config to channel "+chan)
                chanDir = "pseudo-channel_"+str(chan)+'/'
                shutil.copy('./pseudo_config.py', chanDir)

def copy_tv(client):
    #make symlinked copy of pseudo channel files to run on another client
    print("copy_tv")

def ps_update(branch='main'):
    #download and copy updates from git to all branches and boxes
    print("ps_update")
    
def web_setup(branch='main'):
    #set up the web interface and api
    print("web_setup")

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
    copy_tv(args.tv)
if args.update:
    print("UPDATING PSEUDO CHANNEL FROM GIT BRANCH "+str(args.update))
    ps_update(args.update)
if args.web:
    print("SETTING UP PSEUDO CHANNEL WEB INTERFACE AND API FROM GIT BRANCH "+str(args.web))
    web_setup(args.web)