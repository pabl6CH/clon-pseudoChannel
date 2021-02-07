#!/usr/bin/env python
import os
import sys
import glob
import time
import argparse
import subprocess
import pseudo_config as config
import signal

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

def ps_install():
    #download and install pseudo channel from git

def copyconfig(channel=None):
    #copy config file to one or more channels
    
def copy_tv(client):
    #make symlinked copy of pseudo channel files to run on another client

def ps_update(branch='main'):
    #download and copy updates from git to all branches and boxes
    
def web_setup(branch='main'):
    #set up the web interface and api

parser = argparse.ArgumentParser(description='Pseudo Channel Controls')
channelsList = get_channels()
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