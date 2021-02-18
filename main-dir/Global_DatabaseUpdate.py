#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 17:33:59 2018

@author: Matt
"""
import sys
import argparse
import sqlite3
import os
import datetime
import time
from shutil import copy2
from pseudo_config import plexLibraries as global_commercials

channel_dir_increment_symbol = "_"



parser = argparse.ArgumentParser(description="Global Database Update Script")

parser.add_argument('-u','--update_all',action='store_true',help='update ALL elements')
parser.add_argument('-i','--install',action='store_true',help='update ALL elements')
parser.add_argument('-um','--update_movies',action='store_true',help='update MOVIE elements')
parser.add_argument('-utv','--update_tv',action='store_true',help='update TV elements')
parser.add_argument('-uc','--update_comm',action='store_true',help='update COMMERCIAL elements')
args = parser.parse_args()

if args.update_all or len(sys.argv) == 1 or args.install:
    update_flags = '-u'
else:
    update_flags=''
    if args.update_movies:
        update_flags+=' -um'
    if args.update_tv:
        update_flags+=' -utv'
    if args.update_comm:
        update_flags+=' -uc'


update_call = "python PseudoChannel.py %s" % update_flags


# Step ONE: Global database update 
print("NOTICE: Doing global update from PLEX: %s" % update_flags)
try:
    os.rename("pseudo-channel.db", "pseudo-channel.bak")
except OSError:
    pass
try:
    os.system(update_call)
except:
    print("ERROR: Global Update Failed!")
    os.remove("pseudo-channel.db")
    os.rename("pseudo-channel.bak", "pseudo-channel.db")
    sys.exit()


base_dirA = os.path.dirname(os.path.abspath(__file__))
locations = "pseudo-channel"+channel_dir_increment_symbol
channel_dirs = [ item for item in os.listdir('.') if os.path.isdir(os.path.join('.', item)) ]
channel_dirs = list(filter(lambda x: x.startswith(locations),channel_dirs))

for channel_dir in channel_dirs:
    # Step TWO: Go to each folder, export the following information
    # - Show title, lastEpisodeTitle
    # - Movie title, lastPlayedDate
    # - Current channel schedule that the daily schedule is sourced from
    # - Daily schedule currently being executed
    os.chdir(channel_dir)
    
    channel_dirA = os.path.dirname(os.path.abspath(__file__))
    print(channel_dirA.split('/')[-1])
    if channel_dirA.split('/')[-1] == "channels":
        os.chdir(os.path.join(channel_dirA, channel_dir))
        channel_dirA = os.getcwd()
    db_path = os.path.join(channel_dirA, "pseudo-channel.db")
    print("NOTICE: Importing from " + db_path)
        
    try:
        conn = sqlite3.connect(db_path)
        table = conn.cursor()
        
            
        lastEpisode_export = table.execute('SELECT lastEpisodeTitle,title FROM shows').fetchall()
        lastEpisode_export = list(lastEpisode_export)
        lastMovie_export = table.execute('SELECT lastPlayedDate,title FROM movies').fetchall()
        lastMovie_export = list(lastMovie_export)
        schedule = table.execute('SELECT * FROM schedule').fetchall()
        daily_schedule = table.execute('SELECT * FROM daily_schedule').fetchall()
        
        
        
        conn.commit()
        conn.close()
    except:
        print("NOTICE: Database experiencing errors or hasn't been formed yet; creating fresh one")
        lastEpisode_export = []
        lastMovie_export = []
        schedule = []
        daily_schedule = []
    
    
    # Step THREE: Delete the previous database, replace with the recently created global one
    print("NOTICE: Copying global update to " + db_path)
    copy2('../pseudo-channel.db','.')
    
    
    # Step FOUR: Import the previous information we exported previously
    print("NOTICE: Exporting to " + db_path)
    conn = sqlite3.connect(db_path)
    table = conn.cursor()
    
    for i in range(0,len(lastEpisode_export)):
        sql = "UPDATE shows SET lastEpisodeTitle=? WHERE title=?"
        table.execute(sql,lastEpisode_export[i])
        
    for i in range(0,len(lastMovie_export)):
        sql = "UPDATE movies SET lastPlayedDate=? WHERE title=?"
        table.execute(sql,lastMovie_export[i])
    if len(schedule) == 0:
        print("NOTICE: Schedule Not Found, Creating Default Schedule")
        entryList = {}
        entryList['id'] = "1"
        entryList['unix'] = str(time.time())
        entryList['mediaID'] = "999"
        entryList['title'] = "random"
        entryList['duration'] = "10,90"
        entryList['startTime'] = "00:00:00"
        entryList['endTime'] = "0"
        entryList['dayOfWeek'] = "everyday"
        entryList['startTimeUnix'] = str(time.mktime(time.strptime("2000/01/01 00:00:00", "%Y/%m/%d %H:%M:%S")))
        entryList['section'] = "TV Shows"
        entryList['strictTime'] = "true"
        entryList['timeShift'] = "5"
        entryList['overlapMax'] = 15
        entryList['xtra'] = ""
        sql = "INSERT INTO schedule(id,unix,mediaID,title,duration,startTime,endTime,dayOfWeek,startTimeUnix,section,strictTime,timeShift,overlapMax,xtra)  \
            VALUES(:id,:unix,:mediaID,:title,:duration,:startTime,:endTime,:dayOfWeek,:startTimeUnix,:section,:strictTime,:timeShift,:overlapMax,:xtra)"
        table.execute(sql,entryList)
        while int(entryList['id']) < 96:
            entryList['id'] = str(int(entryList['id']) + 1)
            entryList['unix'] = str(time.time())
            entryList['startTimeUnix'] = float(entryList['startTimeUnix']) + 900
            entryList['startTime'] = str(datetime.datetime.fromtimestamp(entryList['startTimeUnix']).strftime("%H:%M:%S"))
            timediff = datetime.datetime.strptime("23:59:59", "%H:%M:%S") - datetime.datetime.strptime(entryList['startTime'], "%H:%M:%S")
            durationSplit = entryList['duration'].split(',')
            if timediff.seconds < 5399:
                maxTime = round(timediff.seconds / 60)
                minTime = int(durationSplit[0])
                if minTime > maxTime:
                    minTime = maxTime - 1
                entryList['duration'] = str(minTime)+','+str(maxTime)
            entryList['overlapMax'] = round(int(durationSplit[0]) * 1.5)
            table.execute(sql,entryList)
    else:
        for i in range(0,len(schedule)):
            sql = "INSERT INTO schedule(id,unix,mediaID,title,duration,startTime,endTime,dayOfWeek,startTimeUnix,section,strictTime,timeShift,overlapMax,xtra)  \
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            table.execute(sql,schedule[i])
    for i in range(0,len(daily_schedule)):
        sql = "INSERT INTO daily_schedule(id,unix,mediaID,title,episodeNumber,seasonNumber,showTitle,duration,startTime,endTime,dayOfWeek,sectionType,plexMediaID,customSectionName)  \
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        table.execute(sql,daily_schedule[i])
    
        
    # Step FIVE: Remove any media not in the directories set of commerical archives
    print("NOTICE: Trimming database at " + db_path)
    os.system('python report_MediaFolders.py')
    local_commercials = open('Commercial_Libraries.txt').read().splitlines()
    local_movies = open('Movie_Libraries.txt').read().splitlines()
    local_tvs = open('TV_Libraries.txt').read().splitlines()
    
    commercial_removal = [x for x in global_commercials["Commercials"] if x not in local_commercials]
    movie_removal = [x for x in global_commercials["Movies"] if x not in local_movies]
    tv_removal = [x for x in global_commercials["TV Shows"] if x not in local_tvs]
    
#    print(db_path)
#    print(local_commercials)
#    print(global_commercials["Commercials"])
#    print(commercial_removal)
    
    for commercial in commercial_removal:
        sql = "DELETE FROM commercials WHERE customSectionName=?"
        table.execute(sql,(commercial,))
    for movie in movie_removal:
        sql = "DELETE FROM movies WHERE customSectionName=?"
        table.execute(sql,(movie,))
    for tv in tv_removal:
        sql = "DELETE FROM shows WHERE customSectionName=?"
        table.execute(sql,(tv,))
        sql = "DELETE FROM episodes WHERE customSectionName=?"
        table.execute(sql,(tv,))
    
    conn.commit()
    conn.close()

    os.chdir('..')
    
    print("NOTICE: " + db_path + " complete!  Going to next file")    
    
print("NOTICE: Global update COMPLETE")
