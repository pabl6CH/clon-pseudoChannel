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
import math
from shutil import copy2
from pseudo_config import plexLibraries as global_commercials
from src import PseudoChannelDatabase

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
os.chdir(os.path.abspath(os.path.dirname(__file__)))
print("ACTION: Doing global update from PLEX: %s" % update_flags)
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
    print("ACTION: Importing from " + db_path)
        
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
    print("ACTION: Copying global update to " + db_path)
    copy2('../pseudo-channel.db','.')
    
    
    # Step FOUR: Import the previous information we exported previously
    print("ACTION: Exporting to " + db_path)
    conn = sqlite3.connect(db_path)
    table = conn.cursor()
    
    for i in range(0,len(lastEpisode_export)):
        sql = "UPDATE shows SET lastEpisodeTitle=? WHERE title=?"
        table.execute(sql,lastEpisode_export[i])
        
    for i in range(0,len(lastMovie_export)):
        sql = "UPDATE movies SET lastPlayedDate=? WHERE title=?"
        table.execute(sql,lastMovie_export[i])
    if len(schedule) == 0:
        #db = PseudoChannelDatabase("./pseudo-channel.db")
        print("NOTICE: Schedule Not Found, Creating Default Schedule")
        entryList = {}
        entryList['id'] = "1"
        entryList['unix'] = str(time.time())
        entryList['mediaID'] = "0"
        rndsql = "SELECT * FROM shows WHERE (customSectionName NOT LIKE 'playlist' AND duration BETWEEN 6000 and 999000) ORDER BY RANDOM() LIMIT 1"
        table.execute(rndsql)
        the_show = table.fetchone()
        entryList['duration'] = str("1,"+str(int(the_show[4] / 60000)))
        entryList['title'] = the_show[3]
        entryList['startTime'] = "00:00:00"
        entryList['dayOfWeek'] = "everyday"
        entryList['startTimeUnix'] = time.mktime(time.strptime("2000/01/01 00:00:00", "%Y/%m/%d %H:%M:%S"))
        entryList['section'] = "TV Shows"
        if entryList['startTime'] == "00:00:00":
            entryList['strictTime'] = "true"
        else:
            entryList['strictTime'] = "secondary"
        entryList['endTime'] = datetime.datetime.fromtimestamp(float(entryList['startTimeUnix']) + the_show[4]/1000).strftime("%H:%M:%S")
        entryList['timeShift'] = 15
        entryList['overlapMax'] = 15
        entryList['xtra'] = ""
        print("INFO: Adding "+entryList['startTime']+" - "+entryList['title']+"\033[K",end='\n')
        sql = "INSERT INTO schedule(id,unix,mediaID,title,duration,startTime,endTime,dayOfWeek,startTimeUnix,section,strictTime,timeShift,overlapMax,xtra)  \
            VALUES(:id,:unix,:mediaID,:title,:duration,:startTime,:endTime,:dayOfWeek,:startTimeUnix,:section,:strictTime,:timeShift,:overlapMax,:xtra)"
        table.execute(sql,entryList)
        timediff = datetime.datetime.strptime("23:59:59", "%H:%M:%S") - datetime.datetime.strptime(entryList['startTime'], "%H:%M:%S")
        print("INFO: "+str(timediff.seconds)+" to midnight\033[K",end='\n')
        endloop = 0
        while timediff.seconds > 900 and endloop == 0:
            entryList['id'] = str(int(entryList['id']) + 1)
            entryList['unix'] = str(time.time())
            prevEndTimeUnix = float(entryList['startTimeUnix']) + the_show[4]/1000
            prevEndTime = datetime.datetime.fromtimestamp(prevEndTimeUnix)
            entryList['startTime'] = prevEndTime + (datetime.datetime.min - prevEndTime) % datetime.timedelta(minutes=entryList['timeShift'])
            entryList['startTime'] = entryList['startTime'].strftime("%H:%M:%S")
            entryList['startTimeUnix'] = time.mktime(time.strptime("2000/01/01 "+entryList['startTime'], "%Y/%m/%d %H:%M:%S"))
            print("INFO: "+str(entryList['startTimeUnix'])+" - New Unix Time Start\033[K",end='\n')
            print("INFO: "+str(entryList['startTime'])+" - New Start Time\033[K",end='\n')
            if entryList['startTime'] == "00:00:00":
                entryList['strictTime'] = "true"
            else:
                entryList['strictTime'] = "secondary"            
            timediff = datetime.datetime.strptime("23:59:59", "%H:%M:%S") - datetime.datetime.strptime(entryList['startTime'], "%H:%M:%S")
            maxMS = timediff.seconds * 1000
            if 0 < int(entryList['endTime'].split(':')[1]) <= 15 or 30 < int(entryList['endTime'].split(':')[1]) <= 45:
                maxMS = 15*60*1000
            rndsql = "SELECT * FROM shows WHERE (customSectionName NOT LIKE 'playlist' AND duration BETWEEN ? and ?) ORDER BY RANDOM() LIMIT 1"
            table.execute(rndsql, ("60000", str(maxMS)))
            the_show = table.fetchone()
            entryList['duration'] = str("1,"+str(int(the_show[4] / 60000)))
            entryList['endTime'] = datetime.datetime.fromtimestamp(float(entryList['startTimeUnix']) + the_show[4]/1000).strftime("%H:%M:%S")
            entryList['title'] = the_show[3]
            entryList['overlapMax'] = round(float(entryList['duration'].split(',')[1]) * 0.5)
            print("INFO: Adding "+entryList['startTime']+" - "+entryList['title']+"\033[K",end='\n')
            sql = "INSERT INTO schedule(id,unix,mediaID,title,duration,startTime,endTime,dayOfWeek,startTimeUnix,section,strictTime,timeShift,overlapMax,xtra)  \
                VALUES(:id,:unix,:mediaID,:title,:duration,:startTime,:endTime,:dayOfWeek,:startTimeUnix,:section,:strictTime,:timeShift,:overlapMax,:xtra)"            
            if entryList['startTime'] != "00:00:00":
                table.execute(sql,entryList)
                print("INFO: "+str(timediff.seconds)+" to midnight\033[K",end='\n') 
            else:
                endloop = 1
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
