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
import socket
import getpass
from git import RemoteProgress
from datetime import datetime
from plexapi.server import PlexServer
from crontab import CronTab
from pathlib import Path

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

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def generate_daily_schedules(channelsList):
    #execute PseudoChannel.py -g in specified channel
    for channel in channelsList:
        os.chdir('./pseudo-channel_'+channel)
        print("GENERATING SCHEDULE FOR CHANNEL "+channel)
        process = subprocess.Popen(["python3", "-u", "PseudoChannel.py", "-g"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
        os.chdir('../')
        
def randomize_episodes(channelsList):
    #execute PseudoChannel.py -ep in specified channel
    for channel in channelsList:
        os.chdir('./pseudo-channel_'+channel)
        print("RANDOMIZING STARTING EPISODES FOR ALL SHOWS ON CHANNEL "+channel)
        process = subprocess.Popen(["python3", "-u", "PseudoChannel.py", "-ep"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
        os.chdir('../')

def ps_install():
    branchList = ['main','python2_dev','python2']
    b = 1
    print("Select Pseudo Channel Repository Branch (default: main)")
    for branch in branchList:
        print(str(b)+": "+branch)
        b = b+1
    branchSelect = input('>: ')
    if branchSelect == "":
        ps_branch = 'main'
    else:
        try:
            branchSelect = int(branchSelect)
            while 0 > int(branchSelect) > b-1:
                print("INVALID ENTRY")
                branchSelect = input('>: ')
            ps_branch = branchList[branchSelect-1]
        except:
            while branchSelect not in branchList:
                print("INVALID ENTRY")
                branchSelect = input('>: ')
            ps_branch = branchSelect
    print("Enter Install Path (default: "+os.getcwd()+"/channels)")
    pathInput = input('>: ')
    if pathInput == '':
        path = os.getcwd()+"/channels"
    else:
        path = pathInput
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
            if section.scanner == "Plex TV Series":
                showsSections.append(section.title)
            elif section.scanner == "Plex Movie":
                moviesSections.append(section.title)
            elif section.scanner == "Plex Video Files":
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
        dailyUpdateHour = input('>: ')
        while int(dailyUpdateHour) > 23:
            print("INVALID ENTRY: Enter a number between 0 and 23")
            dailyUpdateHour = input('>: ')
        dailyUpdateTime = dailyUpdateHour+':00'
        #set up daily cron for schedule generation
        cron = CronTab(user=True)
        for job in cron:
            if job.comment == "Pseudo Channel Daily Schedule Generator":
                print("NOTICE: Removing existing cron job")
                cron.remove(job)
        print("ACTION: Creating cron job for Daily Schedule Generator")
        cronJob = cron.new(command = sys.executable+" "+os.getcwd()+"/controls.py -g", comment="Pseudo Channel Daily Schedule Generator")
        cronJob.hour.on(dailyUpdateHour)
        cronJob.minute.on(0)
        cron.write()
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
        shutil.copytree('./src', '../src')
        global_database_update('./') #run database scan
        channelsList = get_channels()
        randomize_episodes(channelsList)
        generate_daily_schedules(channelsList)
        shutil.rmtree('../src')
        os.remove('../pseudo_config.py')
        os.remove('../plex_token.py')
        web_setup()
        add_client = 'y'
        while 'y' in add_client.lower():
            print("Add another Plex client?")
            add_client = input('Y/N >: ')
            responses = ['yes','y','n','no']
            while add_client.lower() not in responses:
                print("INVALID ENTRY")
                add_client = input('Y/N >: ')
            if 'y' in add_client.lower():        
                copy_tv(clientList, path, os.getcwd())

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

def copy_tv(clientList, installDir, path):
    print("Adding Additional Pseudo Channel Clients") #make symlinked copy of pseudo channel files to run on another client
    print("SELECT DESIRED CLIENT")
    clientNumbers = []
    for i, client in enumerate(clientList):
        print(str(i + 1)+":", client)
        clientNumbers.append(i + 1)
    selectedClient = input('>:')
    while int(selectedClient) not in clientNumbers:
        print("ERROR: INPUT OUTSIDE OF RANGE")
        selectedClient = input('>:')
    ps_client = clientList[int(selectedClient)-1]
    ps_client = ps_client.replace(" ","\ ")
    if path[-1] == '/':
        path[-1] = path[-1].replace('/','')
    newChannelsDir = installDir+'_'+ps_client
    print("Copying Files to "+newChannelsDir)
    #os.mkdir(newChannelsDir)
    #copy all files and directories to a _CLIENT directory
    files = glob.glob(installDir+'/**', recursive=True)
    for file in files:
        isDirectory = os.path.isdir(file)
        if isDirectory == True:
            newDir = file.replace(installDir.split('/')[-1],installDir.split('/')[-1]+'_'+ps_client)
            print("ACTION: Creating Directory "+newDir)
            os.mkdir(newDir)
    for file in files: #copy files into new client directory
        isFile = os.path.isfile(file)
        newDir = file.replace(installDir.split('/')[-1],installDir.split('/')[-1]+'_'+ps_client)
        if isFile == True:
            if "pseudo-channel.db" in file: #symlink the database files
                print("ACTION: Creating symlink to "+file)
                filePathList = file.split('/')
                if "pseudo-channel_" in filePathList[-2]:
                    symLinkPath = newChannelsDir+'/'+filePathList[-2]+'/'+filePathList[-1]
                else:
                    symLinkPath = newChannelsDir+'/'+filePathList[-1]
                print("Creating symlink to database file")
                print(file+" --> "+symLinkPath)
                os.symlink(file,symLinkPath)
            else:
                if isFile == True:
                    print("ACTION: Copying "+file)
                    shutil.copy(file, newDir)

def ps_update():
    print("Updating Pseudo Channel") #download and copy updates from git to all branches and boxes
    branchList = ['main','python2_dev','python2']
    b = 1
    print("Select Pseudo Channel Repository Branch (default: main)")
    for branch in branchList:
        print(str(b)+": "+branch)
        b = b+1
    branchSelect = input('>: ')
    if branchSelect == "":
        ps_branch = 'main'
    else:
        try:
            branchSelect = int(branchSelect)
            while 0 > int(branchSelect) > b-1:
                print("INVALID ENTRY")
                branchSelect = input('>: ')
            ps_branch = branchList[branchSelect-1]
        except:
            while branchSelect not in branchList:
                print("INVALID ENTRY")
                branchSelect = input('>: ')
            ps_branch = branchSelect
    os.mkdir('../temp') #create temp directory to download files into
    try:
        git.Repo.clone_from('https://github.com/FakeTV/pseudo-channel', '../temp', branch=ps_branch)
    except Exception as e:
        print("ERROR GETTING DOWNLOADING FROM GIT")
        print(e)
    mainFiles = glob.glob('../temp/main-dir/*')
    bothFiles = glob.glob('../temp/both-dir/*')
    srcFiles = glob.glob('../temp/both-dir/src/*')
    chanFiles = glob.glob('../temp/channel-dir/*')
    filesList = [mainFiles,bothFiles,srcFiles,chanFiles]
    fL = 1
    for files in filesList:
        for file in files:
            fileName = file.split('/')[-1]
            if fileName != 'pseudo_config.py' and fileName != 'src':
                oldFiles = glob.glob('./**/'+fileName,recursive=True)
                if len(oldFiles) == 0:
                    #Figure out where to copy new files
                    psDirs = glob.glob("./pseudo-channel_*")
                    if fL == 1:
                        try:
                            shutil.copyfile(file, os.getcwd()+'/'+fileName)
                            try:
                                clearLine = " " * len(printLine)
                                print(clearLine,end='\r')       
                            except:
                                pass
                            printLine = "NOTICE: Copying " + fileName + " to " + os.getcwd()
                            print(printLine,end='\r')
                        except Exception as e:
                            print("\nERROR: Copy Failed - " + fileName + " to " + os.getcwd())
                            print(e)
                    elif fL == 2:
                        try:
                            shutil.copyfile(file, os.getcwd()+'/'+fileName)
                            try:
                                clearLine = " " * len(printLine)
                                print(clearLine,end='\r')       
                            except:
                                pass
                            printLine = "NOTICE: Copying " + fileName + " to " + os.getcwd()+'/'+fileName
                            print(printLine,end='\r')
                        except:
                            print("\nERROR: Copy Failed - " + fileName + " to " + os.getcwd()+'/'+fileName)
                        for psDir in psDirs:
                            try:
                                shutil.copyfile(file, psDir+'/'+fileName)
                                try:
                                    clearLine = " " * len(printLine)
                                    print(clearLine,end='\r')       
                                except:
                                    pass
                                printLine = "NOTICE: Copying " + fileName + " to " + psDir+'/'+fileName
                                print(printLine,end='\r')
                            except:
                                print("\nERROR: Copy Failed - " + fileName + " to " + psDir+'/'+fileName)
                    elif fL == 3:
                        try:
                            shutil.copyfile(file, os.getcwd()+'/src/'+fileName)
                            try:
                                clearLine = " " * len(printLine)
                                print(clearLine,end='\r')       
                            except:
                                pass
                            printLine = "NOTICE: Copying " + fileName + " to " + os.getcwd()+'/src/'+fileName
                            print(printLine,end='\r')
                        except:
                            print("\nERROR: Copy Failed - " + fileName + " to " + os.getcwd()+'/src/'+fileName)
                        for psDir in psDirs:
                            try:
                                shutil.copyfile(file, psDir+'/src/'+fileName)
                                try:
                                    clearLine = " " * len(printLine)
                                    print(clearLine,end='\r')       
                                except:
                                    pass
                                printLine = "NOTICE: Copying " + fileName + " to " + psDir+'/src/'+fileName
                                print(printLine,end='\r')
                            except:
                                print("\nERROR: Copy Failed - " + fileName + " to " + psDir+'/src/'+fileName)
                    elif fL == 4:
                        for psDir in psDirs:
                            try:
                                shutil.copyfile(file, psDir+'/src/'+fileName)
                                try:
                                    clearLine = " " * len(printLine)
                                    print(clearLine,end='\r')       
                                except:
                                    pass
                                printLine = "NOTICE: Copying " + fileName + " to " + psDir+'/src/'+fileName
                                print(printLine,end='\r')
                            except:
                                print("\nERROR: Copy Failed - " + fileName + " to " + psDir+'/src/'+fileName)
                else:
                    for old in oldFiles:
                        try:
                            shutil.copyfile(file, old)
                            try:
                                clearLine = " " * len(printLine)
                                print(clearLine,end='\r')       
                            except:
                                pass
                            printLine = "NOTICE: Copying " + fileName + " to " + old
                            print(printLine,end='\r')                            
                        except:
                            print("\nERROR: Copy Failed - " + fileName + " to " + old)

        fL = fL + 1
    shutil.rmtree('../temp')
    print("\nNOTICE: Temp Files Deleted")
    
def web_setup():
    print("Setting up the web interface and API...") #set up the web interface and api
    #copy files from web interface git
    branchList = ['master','develop']
    b = 1
    print("Select Web Interface Repository Branch (default: master)")
    for branch in branchList:
        print(str(b)+": "+branch)
        b = b+1
    branchSelect = input('>: ')
    if branchSelect == "":
        web_branch = 'master'
    else:
        try:
            branchSelect = int(branchSelect)
            while 0 > int(branchSelect) > b-1:
                print("INVALID ENTRY")
                branchSelect = input('>: ')
            web_branch = branchList[branchSelect-1]
        except:
            while branchSelect not in branchList:
                print("INVALID ENTRY")
                branchSelect = input('>: ')
            web_branch = branchSelect
    print("Is a web server (apache, nginx, etc) running on this device? (Y/N)")
    web_server = input('Y/N >: ')
    responses = ['yes','y','n','no']
    while web_server.lower() not in responses:
        print("INVALID ENTRY")
        web_server = input('Y/N >: ')
    if 'y' in web_server.lower():
        print("Enter Install Path (default: /var/www/html)")
        pathInput = input('>: ')
        if pathInput == '':
            path = "/var/www/html"
        else:
            path = pathInput
    else:
        print("Enter port number for web interface (default: 8080)")
        portNumber = input(">: ")
        if portNumber == "":
            portNumber = "8080"
        while portNumber.isnumeric() == False or portNumber == "80":
            print("INVALID ENTRY")
            portNumber = input(">: ")
        path = os.path.abspath(os.path.dirname(__file__))+'/web'
        os.mkdir(path)
        local_ip = get_ip()
        php_binary = shutil.which('php')
        '''cron = CronTab(user=True)
        for job in cron:
            if job.comment == "PHP Server":
                print("NOTICE: Removing existing cron job")
                cron.remove(job)
        print("ACTION: Adding cron job to run PHP Server on Boot")
        job = cron.new(command = "/usr/bin/php -S "+local_ip+":"+portNumber+" -t "+path+" &", comment="PHP Server")
        job.every_reboot()
        cron.write()'''
        systemctlFileText = "[Unit]\nDescription=PHP Start\n\n[Service]\nType=simple\nTimeoutSec=0\nPIDFile=~/\nExecStart="+php_binary+" -S "+local_ip+":"+portNumber+" -t "+path+"\nKillMode=process\nRestart=on=failure\nRestartSec=12s\n\n[Install]\nWantedBy=default.target"
        if (os.path.isdir(str(Path.home())+'/.config/systemd/user/') == False):
            os.mkdir(str(Path.home())+'/.config/systemd/user/')
        if (os.path.isfile(str(Path.home())+'/.config/systemd/user/php.service') == False):
            f=open(str(Path.home())+'/.config/systemd/user/php.service','w+')
            f.write(systemctlFileText)
            f.close
    try:
        print("Copying files to "+path)
        git.Repo.clone_from('https://github.com/FakeTV/Web-Interface-for-Pseudo-Channel', path, branch=web_branch)
    except Exception as e:
        print("ERROR GETTING DOWNLOADING FROM GIT")
        print("e")
    #insert config details
    configFile = open(path+"/psConfig.php", 'r')
    configData = configFile.read()
    configData = configData.replace("$pseudochannel = '/home/pi/channels/';", "$pseudochannel = '"+os.path.abspath(os.path.dirname(__file__))+"';")
    configFile.close()
    configFile = open(path+"/psConfig.php", 'w')
    configFile.write(configData)
    configFile.close()
    #job.run()

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
    action = 'store_true',
    help='Add another TV with linked database')
parser.add_argument('-u', '--update',
    action = 'store_true',
    help='Update Pseudo Channel to the Latest Version')
parser.add_argument('-w', '--web',
    action = 'store',
    help='Install and Set Up Web Interface and API')
parser.add_argument('-ud', '--updatedatabase',
    action='store_true',
    help='Generate Pseudo Channel Database')        
    
args = parser.parse_args()

if args.install:
    print("PSEUDO CHANNEL INSTALL INITIATED")
    ps_install()
if args.copyconfig:
    if args.copyconfig != 'all':
        print("COPYING CONFIG TO CHANNEL "+str(args.copyconfig))
        copyconfig(args.copyconfig)
    else:
        print("COPYING CONFIG TO ALL CHANNELS")
        copyconfig()
if args.tv:
    print("SETTING UP PSUEDO CHANNEL FOR CLIENT")
    import plex_token as plex_token
    PLEX = PlexServer(plex_token.baseurl, plex_token.token)
    clientList = []
    for i, client in enumerate(PLEX.clients()):
        clientList.append(client.title)
    installDir = os.getcwd()
    print(installDir)
    parentDir = os.path.abspath(os.path.join(installDir, os.pardir))
    print(parentDir)
    copy_tv(clientList, installDir, parentDir)
if args.update:
    print("UPDATING PSEUDO CHANNEL FROM GIT")
    ps_update()
if args.web:
    print("SETTING UP PSEUDO CHANNEL WEB INTERFACE AND API FROM GIT BRANCH "+str(args.web))
    #web_setup(args.web)
if args.updatedatabase:
    global_database_update()
