#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal
import datetime
from datetime import time
from time import mktime as mktime
import logging
import calendar
import itertools
import argparse
import textwrap
import os, sys
from xml.dom import minidom
import xml.etree.ElementTree as ET
import json
from pprint import pprint
import random
import re
from plexapi.server import PlexServer
import schedule
from time import sleep
from src import PseudoChannelDatabase
from src import Movie
from src import Commercial
from src import Episode
from src import Music
from src import Video
from src import PseudoDailyScheduleController
from src import PseudoChannelCommercial
from src import PseudoChannelRandomMovie
import pseudo_config as config
from importlib import reload

reload(sys)
#sys.setdefaultencoding('utf-8')

class PseudoChannel():

    PLEX = PlexServer(config.baseurl, config.token)
    MEDIA = []
    GKEY = config.gkey
    USING_COMMERCIAL_INJECTION = config.useCommercialInjection
    DAILY_UPDATE_TIME = config.dailyUpdateTime
    APP_TIME_FORMAT_STR = '%H:%M:%S'
    COMMERCIAL_PADDING_IN_SECONDS = config.commercialPadding
    CONTROLLER_SERVER_PATH = config.controllerServerPath
    CONTROLLER_SERVER_PORT = config.controllerServerPort
    USE_OVERRIDE_CACHE = config.useDailyOverlapCache
    DEBUG = config.debug_mode
    ROTATE_LOG = config.rotateLog
    USE_DIRTY_GAP_FIX = config.useDirtyGapFix
    HTML_PSEUDO_TITLE = config.htmlPseudoTitle

    def __init__(self):

        logging.basicConfig(filename="pseudo-channel.log", level=logging.INFO)
        self.db = PseudoChannelDatabase("pseudo-channel.db")
        self.controller = PseudoDailyScheduleController(
            config.baseurl, 
            config.token, 
            config.plexClients,
            self.CONTROLLER_SERVER_PATH,
            self.CONTROLLER_SERVER_PORT,
            self.DEBUG,
            self.HTML_PSEUDO_TITLE
        )

        self.movieMagic = PseudoChannelRandomMovie()

    """Database functions.
        update_db(): Grab the media from the Plex DB and store it in the local pseudo-channel.db.
        drop_db(): Drop the local database. Fresh start. 
        update_schedule(): Update schedule with user defined times.
        drop_schedule(): Drop the user defined schedule table. 
        generate_daily_schedule(): Generates daily schedule based on the "schedule" table.
    """

    # Print iterations progress
    def print_progress(self, iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            bar_length  - Optional  : character length of bar (Int)
        """
        str_format = "{0:." + str(decimals) + "f}"
        percents = str_format.format(100 * (iteration / float(total)))
        filled_length = int(round(bar_length * iteration / float(total)))
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        sys.stdout.write('\x1b[2K\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

        #if iteration == total:
        #    sys.stdout.write('\n')
        sys.stdout.flush()

    def update_db(self):

        print("NOTICE: Updating Local Database")
        self.db.create_tables()
        libs_dict = config.plexLibraries
        sections = self.PLEX.library.sections()
        for section in sections:
            for correct_lib_name, user_lib_name in libs_dict.items():
                if section.title.lower() in [x.lower() for x in user_lib_name]:
                    if correct_lib_name == "Movies":
                        sectionMedia = self.PLEX.library.section(section.title).all()
                        for i, media in enumerate(sectionMedia):
                            fetchMedia = self.PLEX.fetchItem(media.key)
                            try:
                                genres = [genre.tag for genre in fetchMedia.genres]
                            except:
                                genres = ''
                            try:
                                actors = [actor.tag for actor in fetchMedia.actors]
                            except:
                                actors = ''
                            try:
                                collections = [collection.tag for collection in fetchMedia.collections]
                            except:
                                collections = ''
                            #actors = {}
                            #for actor in fetchMedia.actors:
                            #    actors[actor.tag] = str(actor.id)
                            self.db.add_movies_to_db(media.ratingKey, media.title, media.duration, media.key, section.title, media.contentRating, media.summary, media.originallyAvailableAt, str(genres), str(actors), str(collections), media.studio)
                            self.print_progress(
                                    i + 1, 
                                    len(sectionMedia), 
                                    prefix = section.title+" "+str(i+1)+' of '+str(len(sectionMedia))+": ", 
                                    suffix = 'Complete ['+media.title+']', 
                                    bar_length = 40
                                )
                        #print('')
                    elif correct_lib_name == "TV Shows":
                        sectionMedia = self.PLEX.library.section(section.title).all()
                        for i, media in enumerate(sectionMedia):
                            fetchMedia = self.PLEX.fetchItem(media.key)
                            try:
                                genres = [genre.tag for genre in fetchMedia.genres]
                            except:
                                genres = ''
                            try:
                                actors = [actor.tag for actor in fetchMedia.actors]
                            except:
                                actors = ''
                            try:
                                similars = [similar.tag for similar in fetchMedia.similar]
                            except:
                                similars = ''

                            self.db.add_shows_to_db(
                                media.ratingKey, 
                                media.title, 
                                media.duration if media.duration else 1, 
                                '', 
                                media.originallyAvailableAt, 
                                media.key, 
                                section.title,
                                media.contentRating,
                                str(genres),
                                str(actors),
                                str(similars),
                                media.studio
                            )
                            self.print_progress(
                                    i + 1,
                                    len(sectionMedia),
                                    prefix = 'TV Show '+str(i+1)+' of '+str(len(sectionMedia))+': ',
                                    suffix = 'Complete ['+media.title[0:40]+']',
                                    bar_length = 40
                                )
                        #add all episodes of each tv show to episodes table
                        for i, media in enumerate(sectionMedia):
                            episodes = self.PLEX.library.section(section.title).get(media.title).episodes()
                            for j, episode in enumerate(episodes):
                                duration = episode.duration
                                if duration:
                                    self.db.add_episodes_to_db(
                                            media.ratingKey, 
                                            episode.title, 
                                            duration, 
                                            episode.index, 
                                            episode.parentIndex, 
                                            media.title,
                                            episode.key,
                                            section.title,
                                            episode.contentRating,
                                            episode.originallyAvailableAt,
                                            episode.summary
                                        )
                                else:
                                    self.db.add_episodes_to_db(
                                            episode.ratingKey, 
                                            episode.title, 
                                            0, 
                                            episode.index, 
                                            episode.parentIndex, 
                                            media.title,
                                            episode.key,
                                            section.title,
                                            episode.contentRating,
                                            episode.originallyAvailableAt,
                                            episode.summary
                                        )
                                self.print_progress(
                                        j + 1,
                                        len(episodes),
                                        prefix = str(i+1)+' of '+str(len(sectionMedia))+" "+media.title+': ',
                                        suffix = 'Complete ['+episode.title[0:40]+']',
                                        bar_length = 40
                                    )
                        #print('')
                    elif correct_lib_name == "Commercials":
                        sectionMedia = self.PLEX.library.section(section.title).all()
                        media_length = len(sectionMedia)
                        for i, media in enumerate(sectionMedia):
                            self.db.add_commercials_to_db(3, media.title, media.duration, media.key, section.title)
                            self.print_progress(
                                i + 1, 
                                media_length, 
                                prefix = section.title+" "+str(i+1)+' of '+str(len(sectionMedia))+":", 
                                suffix = 'Complete['+media.title[0:40]+']', 
                                bar_length = 40
                            )
                        #print('')
        dothething = "yes"
        if dothething == "yes":
            playlists = self.PLEX.playlists()
            for i, playlist in enumerate(playlists):
                duration_average = playlist.duration / playlist.leafCount
                playlist_added = playlist.addedAt.strftime("%Y-%m-%d %H:%M:%S")
                self.db.add_shows_to_db(
                    playlist.ratingKey,
                    playlist.title,
                    duration_average,
                    '',
                    playlist_added,
                    playlist.key,
                    playlist.type,
                    '',
                    '',
                    '',
                    '',
                    ''
                )
                # add all entries of playlist to episodes table
                episodes = self.PLEX.playlist(playlist.title).items()
                for j, episode in enumerate(episodes):
                    duration = episode.duration
                    sectionTitle = "Playlists"
                    itemID = str(episode.playlistItemID)
                    itemData = self.PLEX.fetchItem(episode.key)
                    if itemData.type == "episode":
                        sNo = str(itemData.parentIndex)
                        eNo = str(itemData.index)
                        plTitle = episode.grandparentTitle +" - "+ episode.title + " (S" + sNo + "E" + eNo + ")"
                    else:
                        sNo = "0"
                        eNo = "0"
                        plTitle = episode.title + " ("+str(episode.year)+")"
                    if duration:
                        self.db.add_playlist_entries_to_db(
                            episode.ratingKey,
                            plTitle,
                            duration,
                            eNo,
                            sNo,
                            playlist.title,
                            episode.key,
                            sectionTitle,
                            episode.contentRating,
                            episode.originallyAvailableAt,
                            episode.summary
                        )
                    else:
                        self.db.add_playlist_entries_to_db(
                            episode.ratingKey,
                            episode.title,
                            0,
                            eNo,
                            sNo,
                            playlist.title,
                            episode.key,
                            sectionTitle,
                            episode.contentRating,
                            episode.originallyAvailableAt,
                            episode.summary
                        )
                    self.print_progress(
                        j + 1,
                        len(episodes),
                        prefix = 'Playlist '+str(i+1)+' of '+str(len(playlists))+': ',
                        suffix = 'Complete ['+playlist.title[0:40]+']',
                        bar_length = 40
                    )
                #print('', end='\r')
            sys.stdout.write("\033[K")
            sys.stdout.write('\rNOTICE: Database Update Complete!')
            print('')
    def update_db_playlist(self):
        dothething = "yes"
        if dothething == "yes":
            playlists = self.PLEX.playlists()
            for i, playlist in enumerate(playlists):
                duration_average = playlist.duration / playlist.leafCount
                self.db.add_shows_to_db(
                    2,
                    playlist.title,
                    duration_average,
                    '',
                    '',
                    playlist.key,
                    playlist.type
                )
                # add all entries of playlist to episodes table
                episodes = self.PLEX.playlist(playlist.title).items()
                for j, episode in enumerate(episodes):
                    duration = episode.duration
                    sectionTitle = "Playlists"
                    itemID = str(episode.playlistItemID)
                    itemData = self.PLEX.fetchItem(episode.key)
                    if itemData.type == "episode":
                        sNo = str(itemData.parentIndex)
                        eNo = str(itemData.index)
                        plTitle = episode.grandparentTitle +" - "+ episode.title + " (S" + sNo + "E" + eNo + ")"
                    else:
                        sNo = "0"
                        eNo = "0"
                        plTitle = episode.title + " ("+str(episode.year)+")"
                    if duration:
                        self.db.add_playlist_entries_to_db(
                            5,
                            plTitle,
                            duration,
                            eNo,
                            sNo,
                            playlist.title,
                            episode.key,
                            sectionTitle
                        )
                    else:
                        self.db.add_playlist_entries_to_db(
                            5,
                            episode.title,
                            0,
                            eNo,
                            sNo,
                            playlist.title,
                            episode.key,
                            sectionTitle
                        )
                    self.print_progress(
                        j + 1,
                        len(episodes),
                        prefix = 'Progress Playlist '+str(i+1)+' of '+str(len(playlists))+': ',
                        suffix = 'Complete ['+playlist.title+']',
                        bar_length = 40
                    )
                #print('', end='\r')
            sys.stdout.write("\033[K")
            sys.stdout.write('\rNOTICE: Playlist Database Update Complete!')
            print('')

    def update_db_movies(self):

        print("NOTICE: Updating Local Movies Database")
        self.db.create_tables()
        libs_dict = config.plexLibraries
        sections = self.PLEX.library.sections()
        for section in sections:
            for correct_lib_name, user_lib_name in libs_dict.items():
                if section.title.lower() in [x.lower() for x in user_lib_name]:
                    if correct_lib_name == "Movies":
                        sectionMedia = self.PLEX.library.section(section.title).all()
                        for i, media in enumerate(sectionMedia):
                            fetchMedia = self.PLEX.fetchItem(media.key)
                            try:
                                genres = [genre.tag for genre in fetchMedia.genres]
                            except:
                                genres = ''
                            try:
                                actors = [actor.tag for actor in fetchMedia.actors]
                            except:
                                actors = ''
                            try:
                                collections = [collection.tag for collection in fetchMedia.collections]
                            except:
                                collections = ''
                            #actors = {}
                            #for actor in fetchMedia.actors:
                            #    actors[actor.tag] = str(actor.id)
                            self.db.add_movies_to_db(media.key.replace('/library/metadata/',''), media.title, media.duration, media.key, section.title, media.contentRating, media.summary, media.originallyAvailableAt, str(genres), str(actors), str(collections), media.studio)
                            self.print_progress(
                                    i + 1, 
                                    len(sectionMedia), 
                                    prefix = 'Progress '+section.title+": ", 
                                    suffix = 'Complete ['+media.title+']', 
                                    bar_length = 40
                                )
    def update_db_tv(self):

        print("NOTICE: Updating Local Database, TV ONLY")
        self.db.create_tables()
        libs_dict = config.plexLibraries
        sections = self.PLEX.library.sections()
        for section in sections:
            for correct_lib_name, user_lib_name in libs_dict.items():
                if section.title.lower() in [x.lower() for x in user_lib_name]:
                    if correct_lib_name == "TV Shows":
                        sectionMedia = self.PLEX.library.section(section.title).all()
                        for i, media in enumerate(sectionMedia):
                            backgroundImagePath = self.PLEX.library.section(section.title).get(media.title)
                            backgroundImgURL = ''
                            if isinstance(backgroundImagePath.art, str):
                                backgroundImgURL = config.baseurl+backgroundImagePath.art+"?X-Plex-Token="+config.token
                            self.db.add_shows_to_db(
                                2, 
                                media.title, 
                                media.duration if media.duration else 1, 
                                '', 
                                backgroundImgURL, 
                                media.key, 
                                section.title
                            )
                            #add all episodes of each tv show to episodes table
                            episodes = self.PLEX.library.section(section.title).get(media.title).episodes()
                            for j, episode in enumerate(episodes):
                                duration = episode.duration
                                if duration:
                                    self.db.add_episodes_to_db(
                                            4, 
                                            episode.title, 
                                            duration, 
                                            episode.index, 
                                            episode.parentIndex, 
                                            media.title,
                                            episode.key,
                                            section.title
                                        )
                                else:
                                    self.db.add_episodes_to_db(
                                            4, 
                                            episode.title, 
                                            0, 
                                            episode.index, 
                                            episode.parentIndex, 
                                            media.title,
                                            episode.key,
                                            section.title
                                        )
                                self.print_progress(
                                        j + 1,
                                        len(episodes),
                                        prefix = 'Progress TV Show '+str(i+1)+' of '+str(len(sectionMedia))+': ',
                                        suffix = 'Complete ['+media.title+']',
                                        bar_length = 40
                                    )
            #print('', end='\r')
        sys.stdout.write("\033[K")
        sys.stdout.write('\rNOTICE: TV Shows Database Update Complete!')
        print('')
    def update_db_comm(self):

        print("NOTICE: Updating Local Database, COMMERCIALS ONLY")
        self.db.create_tables()
        libs_dict = config.plexLibraries
        sections = self.PLEX.library.sections()
        for section in sections:
            for correct_lib_name, user_lib_name in libs_dict.items():
                if section.title.lower() in [x.lower() for x in user_lib_name]:
                    if correct_lib_name == "Commercials":
                        sectionMedia = self.PLEX.library.section(section.title).all()
                        media_length = len(sectionMedia)
                        for i, media in enumerate(sectionMedia):
                            self.db.add_commercials_to_db(3, media.title, media.duration, media.key, section.title)
                            self.print_progress(
                                i + 1, 
                                media_length, 
                                prefix = 'Progress '+section.title+":", 
                                suffix = 'Complete ['+media.title[0:12]+']', 
                                bar_length = 40
                            )
            #print('', end='\r')
        sys.stdout.write("\033[K")
        sys.stdout.write('\rNOTICE: Commercials Database Update Complete!')
        print('')
    def update_schedule(self):

        """Changing dir to the schedules dir."""
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)
        self.db.create_tables()
        self.db.remove_all_scheduled_items()
        scheduled_days_list = [
            "mondays",
            "tuesdays",
            "wednesdays",
            "thursdays",
            "fridays",
            "saturdays",
            "sundays",
            "weekdays",
            "weekends",
            "everyday"
        ]
        section_dict = {
            "TV Shows" : ["series", "shows", "tv", "episodes", "tv shows", "show","random"],
            "Movies"   : ["movie", "movies", "films", "film"],
            "Videos"   : ["video", "videos", "vid"],
            "Music"    : ["music", "songs", "song", "tune", "tunes"]
        }
        tree = ET.parse('pseudo_schedule.xml')
        root = tree.getroot()
        for child in root:
            if child.tag in scheduled_days_list:
                for time in child.iter("time"):
                    for key, value in section_dict.items():
                        if time.attrib['type'] == key or time.attrib['type'] in value:
                            title = time.attrib['title'] if 'title' in time.attrib else ''
                            natural_start_time = self.translate_time(time.text)
                            natural_end_time = 0
                            section = key
                            if section == "TV Shows" and time.attrib['title'] == "random":
                                mediaID_place=999
                            elif time.attrib['type'] == "random":
                                mediaID_place=9999
                            else:
                                mediaID_place=0
                            day_of_week = child.tag
                            duration = time.attrib['duration'] if 'duration' in time.attrib else '0,43200000'
                            strict_time = time.attrib['strict-time'] if 'strict-time' in time.attrib else 'false'
                            time_shift = time.attrib['time-shift'] if 'time-shift' in time.attrib else '1'
                            overlap_max = time.attrib['overlap-max'] if 'overlap-max' in time.attrib else '0'
                            seriesOffset = time.attrib['series-offset'] if 'series-offset' in time.attrib else ''
                            xtra = time.attrib['xtra'] if 'xtra' in time.attrib else ''
                            
                            # start_time_unix = self.translate_time(time.text)

                            now = datetime.datetime.now()

                            start_time_unix = mktime(
                                datetime.datetime.strptime(
                                    self.translate_time(natural_start_time), 
                                    self.APP_TIME_FORMAT_STR).replace(day=now.day, month=now.month, year=now.year).timetuple()
                                )


                            print("Adding: ", time.tag, section, time.text, time.attrib['title'])
                            self.db.add_schedule_to_db(
                                mediaID_place, # mediaID
                                title, # title
                                duration, # duration
                                natural_start_time, # startTime
                                natural_end_time, # endTime
                                day_of_week, # dayOfWeek
                                start_time_unix, # startTimeUnix
                                section, # section
                                strict_time, # strictTime
                                time_shift, # timeShift
                                overlap_max, # overlapMax
                                xtra, # xtra kargs (i.e. 'director=director')
                            )

    def drop_db(self):

        self.db.drop_db()

    def drop_schedule(self):

        self.db.drop_schedule()

    def remove_all_scheduled_items():

        self.db.remove_all_scheduled_items()

    def translate_time(self, timestr):

        try:
            return datetime.datetime.strptime(timestr, '%I:%M %p').strftime(self.APP_TIME_FORMAT_STR)
        except ValueError as e:
            pass
        try:
            return datetime.datetime.strptime(timestr, '%I:%M:%S %p').strftime(self.APP_TIME_FORMAT_STR)
        except ValueError as e:
            pass
        try:
            return datetime.datetime.strptime(timestr, '%H:%M').strftime(self.APP_TIME_FORMAT_STR)
        except ValueError as e:
            pass
        return timestr

    def time_diff(self, time1,time2):
        '''
        *
        * Getting the offest by comparing both times from the unix epoch time and getting the difference.
        *
        '''
        timeA = datetime.datetime.strptime(time1, pseudo_channel.APP_TIME_FORMAT_STR)
        timeB = datetime.datetime.strptime(time2, pseudo_channel.APP_TIME_FORMAT_STR)
        timeAEpoch = calendar.timegm(timeA.timetuple())
        timeBEpoch = calendar.timegm(timeB.timetuple())
        tdelta = abs(timeAEpoch) - abs(timeBEpoch)
        return int(tdelta/60)


    '''
    *
    * Passing in the endtime from the prev episode and desired start time of this episode, calculate the best start time 

    * Returns time - for new start time
    *
    '''
    def calculate_start_time(self, prevEndTime, intendedStartTime, timeGap, overlapMax):

        self.TIME_GAP = timeGap
        self.OVERLAP_GAP = timeGap
        self.OVERLAP_MAX = overlapMax
        time1 = prevEndTime.strftime(self.APP_TIME_FORMAT_STR)
        timeB = datetime.datetime.strptime(intendedStartTime, self.APP_TIME_FORMAT_STR).strftime(self.APP_TIME_FORMAT_STR)
        print("INFO: Previous End Time: ", time1, "Intended start time: ", timeB)
        timeDiff = self.time_diff(time1, timeB)
        print("INFO: Time Difference = "+ str(timeDiff))
        newTimeObj = timeB
        newStartTime = timeB
        
        '''
        *
        * ADDED PIECE 6/21/18: Need to check if we are near the day's end
        * We will do this by checking if our previous end time is larger than ALL times
        * Listed in the "timeset" variable. If it is, we must have hit the end of a
        * day and can simply pick the first value of the timeset. 
        *
        * If this doesn't apply, simply move on to the regular "checks"
        *
        '''
        time1A=prevEndTime.strftime('%H:%M:%S')
        time1A_comp = datetime.datetime.strptime(time1A, '%H:%M:%S') # there was an issue with the date changing to 1/2, so we had to do this for correct comparison
        timeset=[datetime.time(h,m).strftime("%H:%M:%S") for h,m in itertools.product(range(0,24),range(0,60,int(self.OVERLAP_GAP)))]
        timeset_last = timeset[-1]
        theTimeSetInterval_last = datetime.datetime.strptime(timeset_last, '%H:%M:%S')
        
        prevEndTime = time1A_comp #maybe this will change things?
        print("INFO: Previous End Time: ", time1A_comp)
        print("INFO: Last Element of the Day: ", theTimeSetInterval_last)
        
        if time1A_comp > theTimeSetInterval_last:
            print("NOTICE: We are starting a show with the new day.  Using first element of the next day")
            theTimeSetInterval = datetime.datetime.strptime(timeset[0], '%H:%M:%S') #This must be the element we are looking for
            newStartTime = theTimeSetInterval
            '''
            *
            * If time difference is negative, then we know there is overlap
            *
            '''
        elif timeDiff < 0:
            '''
            *
            * If there is an overlap, then the overlapGap var in config will determine the next increment. If it is set to "15", then the show will will bump up to the next 15 minute interval past the hour.
            *
            '''
            print("NOTICE: OVERLAP DETECTED - elif timeDiff < 0")
            timeSetToUse = None
            for time in timeset:
                theTimeSetInterval = datetime.datetime.strptime(time, '%H:%M:%S')
                print("INFO: Time Set Interval: "+str(theTimeSetInterval))
                if theTimeSetInterval >= prevEndTime:
                    print("NOTICE: There is overlap. Setting new time-interval:", theTimeSetInterval)
                    newStartTime = theTimeSetInterval
                    break
        elif (timeDiff >= 0) and (self.TIME_GAP != -1):
            '''
            *
            * If this value is configured, then the timeGap var in config will determine the next increment. 
            * If it is set to "15", then the show will will bump up to the next 15 minute interval past the hour.
            *
            '''
            print("NOTICE: OVERLAP DETECTED - (timeDiff >= 0) and (self.TIME_GAP != -1)")
            for time in timeset:
                theTimeSetInterval = datetime.datetime.strptime(time, '%H:%M:%S')
                tempTimeTwoStr = datetime.datetime.strptime(time1, self.APP_TIME_FORMAT_STR).strftime('%H:%M:%S')
                formatted_time_two = datetime.datetime.strptime(tempTimeTwoStr, '%H:%M:%S')
                if theTimeSetInterval >= formatted_time_two:
                    print("INFO: Setting new time-interval:", theTimeSetInterval)
                    newStartTime = theTimeSetInterval
                    break
        else:
            print("NOTICE: time1A_comp < theTimeSetInterval_last")
        print("INFO: New Start Time = "+newStartTime.strftime(self.APP_TIME_FORMAT_STR))
        return newStartTime.strftime(self.APP_TIME_FORMAT_STR)

    def get_end_time_from_duration(self, startTime, duration):

        time = datetime.datetime.strptime(startTime, self.APP_TIME_FORMAT_STR)
        show_time_plus_duration = time + datetime.timedelta(milliseconds=duration)
        return show_time_plus_duration

    def generate_daily_schedule(self):

        print("ACTION: Generating Daily Schedule")
        #logging.info("##### Dropping previous daily_schedule database")
        #self.db.remove_all_daily_scheduled_items()
        print("NOTICE: Removing Previous Daily Schedule")
        self.db.drop_daily_schedule_table()
        print("NOTICE: Adding New Daily Schedule Table to Database")
        self.db.create_daily_schedule_table()

        if self.USING_COMMERCIAL_INJECTION:
            print("NOTICE: Getting Commercials List from Database")
            self.commercials = PseudoChannelCommercial(
                self.db.get_commercials(),
                self.COMMERCIAL_PADDING_IN_SECONDS,
                self.USE_DIRTY_GAP_FIX
            )
        print("NOTICE: Getting Base Schedule")
        schedule = self.db.get_schedule_alternate(config.dailyUpdateTime)
        weekday_dict = {
            "0" : ["mondays", "weekdays", "everyday"],
            "1" : ["tuesdays", "weekdays", "everyday"],
            "2" : ["wednesdays", "weekdays", "everyday"],
            "3" : ["thursdays", "weekdays", "everyday"],
            "4" : ["fridays", "weekdays", "everyday"],
            "5" : ["saturdays", "weekends", "everyday"],
            "6" : ["sundays", "weekends", "everyday"],
        }
        weekno = datetime.datetime.today().weekday()
        schedule_advance_watcher = 0
        xtraSeason = None
        xtraEpisode = None
        last_movie = ""
        actors_list = {}
        prev_actors = []
        prev_movies = []
        for entry in schedule:
            schedule_advance_watcher += 1
            section = entry[9]
            for key, val in weekday_dict.items(): 
                if str(entry[7]) in str(val) and int(weekno) == int(key):
                    media_id = entry[2]
                    if section == "TV Shows":
                        next_episode = None
                        try:
                            minmax = entry[4].split(",")
                            min = int(minmax[0])
                            min = min * 60000
                            max = int(minmax[1])
                            max = max * 60000
                        except:
                            minmax = entry[4]
                            min = int(minmax)
                            min = min * 60000
                            max = int(minmax)
                            max = max * 60000
                        if str(entry[3]).lower() == "random":
                            if entry[14] == 0:
                                media_id = 998
                            else:
                                media_id = 999
                            advance_episode = "no"
                            sections = self.PLEX.library.sections()
                            shows_list = []
                            libs_dict = config.plexLibraries
                            for theSection in sections:
                                for correct_lib_name, user_lib_name in libs_dict.items():
                                    if theSection.title.lower() in [x.lower() for x in user_lib_name]:
                                        if correct_lib_name == "TV Shows":
                                            while next_episode is None:
                                                print("----------------------------------")
                                                shows = self.PLEX.library.section(theSection.title)
                                                print("NOTICE: Getting Show That Matches Data Filters")
                                                the_show = self.db.get_random_show_data("TV Shows",int(min),int(max),entry[15],entry[16],entry[17],entry[18],entry[19],entry[20])
                                                print("INFO: " + the_show[3])
                                                if (the_show == None):
                                                    print("NOTICE: Failed to get shows with data filters, trying with less")
                                                    the_show = self.db.get_random_show_data("TV Shows",int(min),int(max),entry[15],None,None,None,entry[19],None)
                                                    #the_show = self.db.get_shows(random.choice(shows_list).title)
                                                    try:
                                                        print("INFO: "+str(the_show[3]))
                                                    except:
                                                        print("NOTICE: FAILED TO GET RANDOM SHOW")
                                                if (the_show is None):
                                                    print("ACTION: Getting random episode of random show")
                                                    next_episode = self.db.get_random_episode_duration(int(min), int(max))
                                                    attempt = 1
                                                    episode_duration = next_episode[4]
                                                    while episode_duration < min or episode_duration > max:
                                                        print("NOTICE: EPISODE LENGTH OUTSIDE PARAMETERS")
                                                        print("ACTION: Getting random episode of random show")
                                                        next_episode = self.db.get_random_episode_duration(int(min), int(max))
                                                        episode_duration = int(next_episode[4])
                                                        attempt = attempt + 1
                                                        if attempt > 1000:
                                                            episode_duration = max
                                                        else:
                                                            episode_duration = int(next_episode[4])
                                                    print("INFO: Random Selection: "+next_episode[7]+" - S"+str(next_episode[6])+"E"+str(next_episode[5])+" - "+next_episode[3])
                                                else:
                                                    print("INFO: entry[2] = " + str(entry[2]))
                                                    print("INFO: media_id = " + str(media_id))
                                                    if entry[2] == 999 or media_id == 999:
                                                        media_id = 999
                                                        print("ACTION: Choosing random episode of "+the_show[3].upper())
                                                        try:
                                                            next_episode = self.db.get_random_episode_of_show_by_data(the_show[2],int(min),int(max),entry[15],entry[21].split(',')[0],entry[21].split(',')[1])
                                                        except:
                                                            next_episode = self.db.get_random_episode_of_show_by_data(the_show[2],int(min),int(max),entry[15])
                                                    elif entry[2] == 998 or media_id == 998:
                                                        media_id = 998
                                                        if entry[14] == 1:
                                                            print("ACTION: Choosing last episode of " +the_show[3].upper())
                                                            advance_episode = "no"
                                                            next_episode = self.db.get_last_episode(the_show[2]) #get last episode
                                                            try:
                                                                print("INFO: Scheduled: "+next_episode[7]+" - (S"+str(next_episode[6])+"E"+str(next_episode[5])+") "+next_episode[3])
                                                            except:
                                                                pass
                                                        else:
                                                            print("ACTION: Choosing next episode of " +the_show[3].upper())
                                                            advance_episode = "yes"
                                                            next_episode = self.db.get_next_episode(the_show[3]) #get next episode
                                                            try:
                                                                print("INFO: Scheduled: "+next_episode[7]+" - (S"+str(next_episode[6])+"E"+str(next_episode[5])+") "+next_episode[3])
                                                            except:
                                                                pass
                                            episode_duration = int(next_episode[4])
                                            show_title = next_episode[7]
                                            xtraSeason = None
                                            xtraEpisode = None
                                            print("INFO: " + next_episode[7] + " - " + next_episode[3] + " (S" + str(next_episode[6]) + "E" + str(next_episode[5]) + ")")
                            print("----------------------------------")
                        elif entry[2] == 9999:
                            media_id = 9999
                            advance_episode = "no"
                            print("ACTION: Getting random episode of "+entry[3])
                            if entry[15] != None:
                                if entry[15][3] == '*':
                                    print("INFO: Decade = " + str(entry[15]))
                                    airDate=entry[15][0:3]
                                else:
                                    print("INFO: Air Date = " + str(entry[15]))
                                    airDate=entry[15]
                            else:
                                airDate=None
                            try:
                                next_episode = self.db.get_random_episode_of_show_by_data_alt(entry[3], int(min), int(max), airDate, entry[21].split(',')[0], entry[21].split(',')[1])
                            except Exception as e:
                                print("ERROR: " + str(e))
                                next_episode = self.db.get_random_episode_of_show_by_data_alt(entry[3], int(min), int(max), airDate)
                            print("INFO: Episode Selected: S"+str(next_episode[6])+"E"+str(next_episode[5])+" "+next_episode[3].upper())
                            show_title = next_episode[7]
                            episode_duration = next_episode[4]
                            attempt = 1
                            while int(episode_duration) < min or episode_duration > max:
                                print("ACTION: Getting random episode of "+entry[3])
                                next_episode = self.db.get_random_episode_of_show(entry[3])
                                print("INFO: Episode Selected: S"+str(next_episode[6])+"E"+str(next_episode[5])+" "+next_episode[3].upper())
                                attempt = attempt + 1
                                if attempt > 500:
                                    episode_duration = max
                                else:
                                    episode_duration = next_episode[4]
                            show_title = next_episode[7]
                        else:
                            print("----------------------------------")
                            if entry[14] == 1:
                                advance_episode = "no"
                                #check for same show in MEDIA list
                                for m in self.MEDIA:
                                    try:
                                        seriesTitle = m.show_series_title
                                    except:
                                        seriesTitle = None
                                    if seriesTitle == entry[3]:
                                        next_episode = self.db.get_episode_from_plexMediaID(m.plex_media_id)
                                if next_episode == None:
                                    next_episode = self.db.get_last_episode_alt(entry[3]) #get last episode
                            else:
                                advance_episode = "yes"
                                #check for same show in MEDIA list
                                episodeID = None
                                for m in self.MEDIA:
                                    try:
                                        seriesTitle = m.show_series_title
                                    except:
                                        seriesTitle = None
                                    if seriesTitle == entry[3] and m.media_id == 2:
                                        episodeID = self.db.get_episode_id_alternate(m.plex_media_id,seriesTitle)[0]
                                if episodeID != None:
                                    next_episode = self.db.get_next_episode_alt(seriesTitle, episodeID)
                                if next_episode == None:
                                    next_episode = self.db.get_next_episode(entry[3]) #get next episode
                            try:
                                print("INFO: Scheduled: "+next_episode[7]+" - (S"+str(next_episode[6])+"E"+str(next_episode[5])+") "+next_episode[3])
                            except:
                                pass
                            show_title = entry[3]
                        try:
                            episode_rating = str(next_episode[10])
                        except Exception as e:
                            print(e)
                            episode_rating = "None"
                        try:
                            episode_notes = str(next_episode[12])
                        except Exception as e:
                            print(e)
                            episode_notes = ""
                        notes_data = "Rated " + episode_rating +  "</br>" + episode_notes
                        if next_episode != None:
                            customSectionName = next_episode[9]
                            episode = Episode(
                                section, # section_type
                                next_episode[3], # title
                                entry[5], # natural_start_time
                                self.get_end_time_from_duration(self.translate_time(entry[5]), next_episode[4]), # natural_end_time
                                next_episode[4], # duration
                                entry[7], # day_of_week
                                entry[10], # is_strict_time
                                entry[11], # time_shift
                                entry[12], # overlap_max
                                #next_episode[8] if len(next_episode) >= 9 else '', # plex id
                                next_episode[8], # plex_media_id
                                customSectionName, # custom lib name
                                media_id, #media_id
                                show_title, # show_series_title
                                next_episode[5], # episode_number
                                next_episode[6], # season_number
                                advance_episode, # advance_episode
                                notes_data #notes
                                )
                            self.MEDIA.append(episode)
                        else:
                            print("ERROR: Cannot find TV Show Episode, {} in the local db".format(entry[3]))
                    elif section == "Movies":
                        minmax = entry[4].split(",")
                        min = int(minmax[0])
                        min = min * 60000
                        max = int(minmax[1])
                        max = max * 60000
                        movies_list = []
                        movies_list_filtered = []
                        if str(entry[3]).lower() == "random":
                            if(entry[13] != ''): # xtra params
                                """
                                Using specified Movies library names
                                """
                                libs_dict = config.plexLibraries

                                sections = self.PLEX.library.sections()
                                for theSection in sections:
                                    for correct_lib_name, user_lib_name in libs_dict.items():
                                        if theSection.title.lower() in [x.lower() for x in user_lib_name]:
                                            if correct_lib_name == "Movies" and entry[13] != "":
                                                print("----------------------------------")
                                                print("INFO: Movie Xtra Arguments: ", entry[13])
                                                movies = self.PLEX.library.section(theSection.title)
                                                xtra = []
                                                d = {}
                                                if ";" in xtra:
                                                    xtra = entry[13].split(';')
                                                else:
                                                    if xtra != None:
                                                        xtra = str(entry[13]) + ';'
                                                        xtra = xtra.split(';')
                                                print(xtra)
                            try:
                                """for thestr in xtra:
                                    print ("INFO: "+thestr)
                                    regex = re.compile(r"\b(\w+)\s*:\s*([^:]*)(?=\s+\w+\s*:|$)")
                                    d.update(regex.findall(thestr))
                                # turn values into list
                                for key, val in d.items():
                                    d[key] = val.split(',')"""
                                if entry[13] != "" and entry[13] != None:
                                    movie_search = self.db.get_movies_xtra(correct_lib_name,int(min),int(max),xtra)
                                else:
                                    movie_search = self.db.get_movies_data("Movies",int(min),int(max),entry[15],entry[16],entry[17],entry[18],entry[19],entry[20])
                                for movie in movie_search:
                                    movies_list.append(movie)
                            except:
                                pass
                            if (len(movies_list) > 0):
                                movie_get = random.choice(movies_list)
                                movies_list.remove(movie_get)
                                try:
                                    print("INFO: Movie Title -  " + movie_get[3])
                                    the_movie = self.db.get_movie_by_id(movie_get[6])
                                except Exception as e:
                                    print("ERROR: Key not found")
                                    print(e)
                                    print("INFO: " + movie_get[3])
                                    the_movie = self.db.get_movie(movie_get[3])
                                movie_duration = the_movie[4]
                                attempt = 1
                                while int(movie_duration) < min or movie_duration > max:
                                    movie_get = random.choice(movies_list)
                                    movies_list.remove(movie_get)
                                    try:
                                        print("INFO: Movie Title -  " + movie_get[3])
                                        the_movie = self.db.get_movie_by_id(movie_get[6])
                                    except Exception as e:
                                        print("ERROR: Key not found")
                                        print(e)
                                        print("INFO: " + movie_get[3])
                                        the_movie = self.db.get_movie(movie_get[6])
                                    attempt = attempt + 1
                                    if attempt > 500:
                                        movie_duration = max
                                    else:
                                        movie_duration = the_movie[4]
                                """Updating movies table in the db with lastPlayedDate entry"""
                                self.db.update_movies_table_with_last_played_date(the_movie[3])
                            else:
                                print("ERROR: xtra args not found, getting random movie")
                                movie_search = self.db.get_movies_data("Movies",int(min),int(max),None,None,None,None,entry[19],None)
                                for movie in movie_search:
                                    if movie not in movies_list and movie[3] not in last_movie:
                                        movies_list.append(movie)
                                movie_get = random.choice(movies_list)
                                movies_list.remove(movie_get)
                                try:
                                    print("INFO: Movie Title -  " + movie_get[3])
                                    the_movie = self.db.get_movie_by_id(movie_get[6])
                                except Exception as e:
                                    print("ERROR: Key not found")
                                    print(e)
                                    print("INFO: " + movie_get[3])
                                    the_movie = self.db.get_movie(movie_get[6])
                                print("INFO: Movie Title - " + str(the_movie[3]))
                                movie_duration = the_movie[4]
                                attempt = 1
                                while int(movie_duration) < min or movie_duration > max:
                                    the_movie = self.db.get_random_movie_duration(int(min), int(max))
                                    attempt = attempt + 1
                                    if attempt > 500:
                                        movie_duration = max
                                    else:
                                        movie_duration = the_movie[4]
                                """Updating movies table in the db with lastPlayedDate entry"""
                                self.db.update_movies_table_with_last_played_date(the_movie[3])
                            """minmax = str(entry[4]).split(",")
                            min = int(minmax[0])
                            min = min * 60000
                            max = int(minmax[1])
                            max = max * 60000
                            the_movie = self.db.get_random_movie_duration(int(min), int(max))
                            movie_duration = the_movie[4]
                            attempt = 1
                            while int(movie_duration) < min or movie_duration > max:
                                the_movie = self.db.get_random_movie_duration(int(min), int(max))
                                attempt = attempt + 1
                                if attempt > 500:
                                    movie_duration = max
                                else:
                                    movie_duration = the_movie[4]
                                    movies_list = []
                                    libs_dict = config.plexLibraries
                                    sections = self.PLEX.library.sections()
                                    #Updating movies table in the db with lastPlayedDate entry
                                    self.db.update_movies_table_with_last_played_date(the_movie[3])"""
                        elif str(entry[3]).lower() == "kevinbacon":
                            #kevin bacon mode
                            print("----------------------------------")
                            print("NOTICE: Kevin Bacon Mode Initiated")
                            backup_list = []
                            delete_list = []
                            xtra = []
                            for k in actors_list:
                                if actors_list[k] in prev_actors:
                                    delete_list.append(k)
                            for dL in delete_list:
                                    actors_list.pop(dL)
                            """
                            Using specified Movies library names
                            """
                            libs_dict = config.plexLibraries

                            sections = self.PLEX.library.sections()
                            for theSection in sections:
                                for correct_lib_name, user_lib_name in libs_dict.items():
                                    if theSection.title.lower() in [x.lower() for x in user_lib_name]:
                                        if correct_lib_name == "Movies":
                                            movies = self.PLEX.library.section(theSection.title)
                            '''if(entry[13] != None or len(actors_list) > 0): # xtra params
                                xtra = []
                                try:
                                    print("INFO: Movie Xtra Arguments: ", entry[13])
                                except:
                                    print("INFO: Xtra Arguments Not Found")
                                d = {}'''
                            if len(actors_list) > 0:
                                xtra_actors = []
                                if entry[17] != None and ',' in entry[17]:
                                    xtra_actors = entry[17].split(',')
                                elif entry[17] != None and ',' not in entry[17]:
                                    xtra_actors.append(entry[17])
                                for actorName in actors_list:
                                    the_actors = []
                                    for xActor in xtra_actors:
                                        print("INFO: xtra actor = " + xActor)
                                        the_actors.append(xActor)
                                    the_actors.append(actorName)
                                    aLoop = 1
                                    actor_data = ''
                                    print("----------------------------------")
                                    print("INFO: Actor from " + last_movie + " selected - " + actorName)
                                    print("NOTICE: Executing movies search for matches")
                                    print("INFO: " + str(entry[15]) + ', ' + str(entry[16]) + ', ' + str(the_actors) + ', ' + str(entry[18]) + ', ' + str(entry[19]) + ', ' + str(entry[20]))
                                    movie_search = self.db.get_movies_data("Movies",int(min),int(max),entry[15],entry[16],the_actors,entry[18],entry[19],entry[20])
                                    print("INFO: " + str(len(movie_search)) + " results found")
                                    #except Exception as e:
                                        #print(e)
                                    for movie in movie_search:
                                        if movie not in movies_list and movie[3] not in last_movie:
                                            print(str(movie[3]))
                                            movies_list.append(movie)
                                        #print("INFO: Match Found - " + str(movie))
                                    #for movie in movies.search(None, **d):
                                    #    movies_list.append(movie)
                                    #    print("INFO: Match Found - " + str(movie))
                                    #except Exception as e:
                                    #    print("ERROR: " + str(e))
                                    #    pass
                                    #print("INFO: Movies List: " + str(movies_list))
                            else:
                                print("NOTICE: No previous actor data, skipping...")
                                '''if ";" in entry[13]:
                                    xtra = entry[13].split(';')
                                else:
                                    if entry[13] != None:
                                        xtra = str(entry[13]) + ';'
                                        xtra = xtra.split(';')
                                print(xtra)'''
                                try:
                                    """for thestr in xtra:
                                        print ("INFO: "+thestr)
                                        regex = re.compile(r"\b(\w+)\s*:\s*([^:]*)(?=\s+\w+\s*:|$)")
                                        d.update(regex.findall(thestr))
                                    # turn values into list
                                    for key, val in d.items():
                                        d[key] = val.split(',')"""
                                    movie_search = self.db.get_movies_data("Movies",int(min),int(max),entry[15],entry[16],entry[17],entry[18],entry[19],entry[20])
                                    for movie in movie_search:
                                        movies_list.append(movie)
                                        #print("INFO: Match Found - " + movie)
                                except Exception as e:
                                    print("ERROR: " + str(e))
                                    pass
                            #print(xtra)
                            
                            if (len(movies_list) > 0):
                                print("----------------------------------")
                                print("INFO: " + str(len(movies_list)) + " movies in list")
                                movie_get = random.choice(movies_list)
                                movies_list.remove(movie_get)
                                try:
                                    print("INFO: Movie Title -  " + movie_get[3])
                                    the_movie = self.db.get_movie_by_id(movie_get[6])
                                except Exception as e:
                                    print("ERROR: Key not found")
                                    print(e)
                                    print("INFO: " + movie_get[3])
                                    the_movie = self.db.get_movie(movie_get[3])
                                attempt = 1
                                while the_movie[6] in prev_movies and last_movie in the_movie[3] and attempt < 500:
                                    movie_get = random.choice(movies_list)
                                    try:
                                        print("INFO: Movie Title -  " + movie_get[3])
                                        the_movie = self.db.get_movie_by_id(movie_get[6])
                                    except Exception as e:
                                        print("ERROR: Key not found")
                                        print(e)
                                        print("INFO: " + movie_get[3])
                                        the_movie = self.db.get_movie(movie_get[3])
                                    attempt = attempt + 1
                                movie_duration = the_movie[4]
                                attempt = 1
                                while int(movie_duration) < min or movie_duration > max:
                                    if len(movies_list) > 0:
                                        movie_get = random.choice(movies_list)
                                        movies_list.remove(movie_get)
                                        try:
                                            print("INFO: Movie Title -  " + movie_get[3])
                                            the_movie = self.db.get_movie_by_id(movie_get[6])
                                        except Exception as e:
                                            print("ERROR: Key not found")
                                            print(e)
                                            print("INFO: " + movie_get[3])
                                            the_movie = self.db.get_movie(movie_get[3])
                                    else:
                                        the_movie = self.db.get_random_movie_duration(int(min), int(max))
                                        print("ERROR: Falling back to random movie that fits in the duration window")
                                        print("INFO: Movie Title - " + str(the_movie[3]))
                                    attempt = attempt + 1
                                    if attempt > 500:
                                        movie_duration = max
                                    else:
                                        movie_duration = the_movie[4]
                                """Updating movies table in the db with lastPlayedDate entry"""
                                self.db.update_movies_table_with_last_played_date(the_movie[3])
                            else:
                                print("----------------------------------")
                                print("ERROR: No movies found, re-rolling without xtra args")
                                d = {}
                                if len(actors_list) > 0:
                                    for actorName in actors_list:
                                        actorID = actorName
                                        print("INFO: Actor from " + last_movie + " selected - " + actorName)
                                        try:
                                            xtra = xtra.append("actor:"+str(actorID))
                                        except:
                                            xtra = ["actor:"+str(actorID)]
                                        try:
                                            """for thestr in xtra:
                                                print ("INFO: "+thestr)
                                                regex = re.compile(r"\b(\w+)\s*:\s*([^:]*)(?=\s+\w+\s*:|$)")
                                                d.update(regex.findall(thestr))
                                            # turn values into list
                                            for key, val in d.items():
                                                d[key] = val.split(',')"""
                                            movie_search = self.db.get_movies_data("Movies",int(min),int(max),None,None,actor_data,None,entry[19],None)
                                            #movie_search = movies.search(None, **d)
                                            for movie in movie_search:
                                                if movie not in movies_list and movie[3] not in last_movie:
                                                    movies_list.append(movie)
                                                #print("INFO: Match Found - " + movie)
                                        except Exception as e:
                                            print("ERROR: " + str(e))
                                            pass
                                        print("INFO: " + str(len(movie_search)) + " results found")

                                if (len(movies_list) > 0):
                                    print("----------------------------------")
                                    print("INFO: " + str(len(movies_list)) + " movies in list")
                                    movie_get = random.choice(movies_list)
                                    movies_list.remove(movie_get)
                                    try:
                                        print("INFO: Movie Title -  " + movie_get[3])
                                        the_movie = self.db.get_movie_by_id(movie_get[6])
                                    except Exception as e:
                                        print("ERROR: Key not found")
                                        print(e)
                                        print("INFO: " + movie_get[3])
                                        the_movie = self.db.get_movie(movie_get[3])
                                    attempt = 1
                                    while the_movie[6] in prev_movies and last_movie in the_movie[3] and attempt < 500:
                                        movie_get = random.choice(movies_list)
                                        movies_list.remove(movie_get)
                                        try:
                                            print("INFO: Movie Title -  " + movie_get[3])
                                            the_movie = self.db.get_movie_by_id(movie_get[6])
                                        except Exception as e:
                                            print("ERROR: Key not found")
                                            print(e)
                                            print("INFO: " + movie_get[3])
                                            the_movie = self.db.get_movie(movie_get[6])
                                        attempt = attempt + 1
                                    attempt = 1
                                    movie_duration = the_movie[4]
                                    while int(movie_duration) < min or movie_duration > max:
                                        if len(movies_list) > 0:
                                            try:
                                                movies_list.remove(the_movie)
                                            except Exception as e:
                                                print(the_movie)
                                                print(e)
                                            movie_get = random.choice(movies_list)
                                            try:
                                                print("INFO: Movie Title -  " + movie_get[3])
                                                the_movie = self.db.get_movie_by_id(movie_get[6])
                                            except Exception as e:
                                                print("ERROR: Key not found")
                                                print(e)
                                                print("INFO: " + movie_get[3])
                                                the_movie = self.db.get_movie(movie_get[3])
                                        else:
                                            the_movie = self.db.get_random_movie_duration(int(min), int(max))
                                            print("ERROR: Falling back to random movie that fits in the duration window")
                                            print("INFO: Movie Title - " + str(the_movie[3]))
                                        attempt = attempt + 1
                                        if attempt > 500:
                                            movie_duration = max
                                        else:
                                            movie_duration = the_movie[4]
                                else:
                                    print("ERROR: Kevin Bacon Mode failed to find a match, selecting random movie")
                                    movies_list = []
                                    movie_search = self.db.get_movies_data("Movies",int(min),int(max),entry[14],entry[15],entry[16],entry[17],entry[18],entry[19])
                                    for movie in movie_search:
                                        if movie not in movies_list and movie[3] not in last_movie:
                                            movies_list.append(movie)
                                    if len(movies_list) < 1:
                                        print("ERROR: xtra args not found, getting random movie")
                                        movie_search = self.db.get_movies_data("Movies",int(min),int(max),None,None,None,None,entry[19],None)
                                        try:
                                            for movie in movie_search:
                                                if movie not in movies_list and movie[3] not in last_movie:
                                                    movies_list.append(movie)
                                        except:
                                            movies_list.append(movie)
                                        movie_get = random.choice(movies_list)
                                        movies_list.remove(movie_get)
                                        try:
                                            print("INFO: Movie Title -  " + movie_get[3])
                                            the_movie = self.db.get_movie_by_id(movie_get[6])
                                        except Exception as e:
                                            print("ERROR: Key not found")
                                            print(e)
                                            print("INFO: " + movie_get[3])
                                            the_movie = self.db.get_movie(movie_get[6])
                                    print("INFO: Movie Title - " + str(the_movie[3]))
                                    print("----------------------------------")
                                    movie_duration = the_movie[4]
                                    attempt = 1
                                    while int(movie_duration) < min or movie_duration > max:
                                        the_movie = self.db.get_random_movie_duration(int(min), int(max))
                                        attempt = attempt + 1
                                        if attempt > 500:
                                            movie_duration = max
                                        else:
                                            movie_duration = the_movie[4]
                                """Updating movies table in the db with lastPlayedDate entry"""
                                self.db.update_movies_table_with_last_played_date(the_movie[3])
                                try:
                                    prev_actors.append(actorID)
                                except:
                                    pass
                                prev_movies.append(the_movie[6])
                                #last_movie = the_movie[3]
                                """Updating movies table in the db with lastPlayedDate entry"""
                                self.db.update_movies_table_with_last_played_date(the_movie[3])
                        else:
                            the_movie = self.db.get_movie(entry[3])
                        if str(entry[3]).lower() == "kevinbacon":
                            media_id = 112
                        else:
                            media_id = 1
                        if the_movie != None:
                            print("----------------------------------")
                            print("NOTICE: Movie Selected - " + the_movie[3])
                            #get plex metadata
                            plex_movie = self.PLEX.fetchItem(the_movie[6])
                            last_data = ""
                            notes_data = ""
                            if str(entry[3]).lower() == "kevinbacon":
                                actors_list_old = actors_list
                                actors_list = {}
                                actor_match = ""
                                print("NOTICE: Replacing Actors List with list from " + the_movie[3])
                                for actor in plex_movie.actors:
                                    actors_list[actor.tag] = actor.id
                                    if actor.tag in actors_list_old.keys():
                                        print("INFO: Match between movies - " + actor.tag)
                                        prev_actors.append(actor.id)
                                        if actor_match == "":
                                            actor_match = actor.tag
                                if actor_match != "":
                                    notes_data = "This movie derived from " + last_movie + " through " + actor_match + "\n"
                                else:
                                    notes_data = ""
                                last_movie = the_movie[3]
                            actors_data = the_movie[12].strip('][').split(',')
                            notes_data = notes_data + "Rated " + str(the_movie[8]) + "</br>Starring: " + str(actors_data[0]) + ", " + str(actors_data[1]) + " and " + str(actors_data[2]) + "</br>" + str(the_movie[10]) + "</br>" + str(the_movie[14])
                            movie = Movie(
                            section, # section_type
                            the_movie[3], # title
                            entry[5], # natural_start_time
                            self.get_end_time_from_duration(entry[5], the_movie[4]), # natural_end_time
                            the_movie[4], # duration
                            entry[7], # day_of_week
                            entry[10], # is_strict_time
                            entry[11], # time_shift
                            entry[12], # overlap_max
                            the_movie[6], # plex id
                            the_movie[7], # custom lib name
                            media_id, # media_id
                            notes_data # notes (for storing kevin bacon data)
                            )
                            self.MEDIA.append(movie)
                        else:
                            print(str("ERROR: Cannot find Movie, {} in the local db".format(entry[3])).encode('UTF-8'))
                    elif section == "Music":
                        the_music = self.db.get_music(entry[3])
                        if the_music != None:
                            music = Music(
                            section, # section_type
                            the_music[3], # title
                            entry[5], # natural_start_time
                            self.get_end_time_from_duration(entry[5], the_music[4]), # natural_end_time
                            the_music[4], # duration
                            entry[7], # day_of_week
                            entry[10], # is_strict_time
                            entry[11], # time_shift
                            entry[12], # overlap_max
                            the_music[6], # plex id
                            the_music[7], # custom lib name
                            )
                            self.MEDIA.append(music)
                        else:
                            print(str("ERROR: Cannot find Music, {} in the local db".format(entry[3])).encode('UTF-8'))
                    elif section == "Video":
                        the_video = self.db.get_video(entry[3])
                        if the_music != None:
                            video = Video(
                            section, # section_type
                            the_video[3], # title
                            entry[5], # natural_start_time
                            self.get_end_time_from_duration(entry[5], the_video[4]), # natural_end_time
                            the_video[4], # duration
                            entry[7], # day_of_week
                            entry[10], # is_strict_time
                            entry[11], # time_shift
                            entry[12], # overlap_max
                            the_video[6], # plex id
                            the_video[7], # custom lib name
                            )
                            self.MEDIA.append(video)
                        else:
                            print(str("ERROR: Cannot find Video, {} in the local db".format(entry[3])).encode('UTF-8'))
                    else:
                        pass
            """If we reached the end of the scheduled items for today, add them to the daily schedule

            """
            if schedule_advance_watcher >= len(schedule):
                print("INFO: Finished processing time entries, generating daily_schedule")
                previous_episode = None
                for entry in self.MEDIA:
                    if previous_episode != None:
                        natural_start_time = datetime.datetime.strptime(entry.natural_start_time, self.APP_TIME_FORMAT_STR)
                        natural_end_time = entry.natural_end_time
                        if entry.is_strict_time.lower() == "true":
                            print("INFO: Strict-time: {}".format(str(entry.title)))
                            entry.end_time = self.get_end_time_from_duration(
                                    self.translate_time(entry.start_time),
                                    entry.duration
                                )
                            if entry.end_time.hour >= 0 and entry.end_time.hour < int(config.dailyUpdateTime[0]):
                                entry.end_time = entry.end_time + datetime.timedelta(days=1)
                            if natural_start_time.hour < int(config.dailyUpdateTime[0]) and entry.end_time.hour >= int(config.dailyUpdateTime[0]):
                                entry.end_time = datetime.datetime.strptime('1900-01-02 0' + str(int(config.dailyUpdateTime[0])-1) + ':59:59.99999', '%y-%m-%d %H:%M:%S.%f')
                            """Get List of Commercials to inject"""
                            if self.USING_COMMERCIAL_INJECTION:
                                list_of_commercials = self.commercials.get_commercials_to_place_between_media(
                                    previous_episode,
                                    entry,
                                    entry.is_strict_time.lower(),
                                    config.dailyUpdateTime
                                )
                                for commercial in list_of_commercials:
                                    self.db.add_media_to_daily_schedule(commercial)
                            self.db.add_media_to_daily_schedule(entry)
                            previous_episode = entry
                            if entry.custom_section_name == "TV Shows" and entry.advance_episode != "no":
                                self.db.update_shows_table_with_last_episode(entry.show_series_title, entry.plex_media_id)
                        elif entry.is_strict_time.lower() == "secondary": #This mode starts a show "already in progress" if the previous episode or movie runs past the start time of this one
                            print("INFO Pre-empt Allowed: {}".format(str(entry.title)))
                            try:
                                prev_end_time = datetime.datetime.strptime(str(previous_episode.end_time), '%Y-%m-%d %H:%M:%S.%f')
                            except ValueError:
                                prev_end_time = datetime.datetime.strptime(str(previous_episode.end_time), '%Y-%m-%d %H:%M:%S')
                            prev_end_time = prev_end_time.strftime(self.APP_TIME_FORMAT_STR)
                            start_time_difference=self.time_diff(str(entry.natural_start_time),str(prev_end_time))
                            start_time_difference=start_time_difference*60
                            print("INFO: Entry Duration = {}".format(str(entry.duration)))
                            print("INFO: Start Time Difference = {}".format(str(start_time_difference)))
                            if start_time_difference > 0:
                                running_duration = entry.duration - abs(start_time_difference)
                                print("INFO: Running Duration = {}".format(str(running_duration)))
                                entry.start_time = datetime.datetime.strptime(entry.natural_start_time, self.APP_TIME_FORMAT_STR) + datetime.timedelta(seconds=abs(start_time_difference))
                                entry.start_time = datetime.datetime.strftime(entry.start_time, self.APP_TIME_FORMAT_STR)
                                print("INFO: New Start Time = {}".format(str(entry.start_time)))
                                entry.end_time = self.get_end_time_from_duration(
                                    self.translate_time(natural_start_time.strftime(self.APP_TIME_FORMAT_STR)),
                                    entry.duration
                                )
                                if entry.end_time.hour >= 0 and entry.end_time.hour < int(config.dailyUpdateTime[0]):
                                    entry.end_time = entry.end_time + datetime.timedelta(days=1)
                                if natural_start_time.hour < int(config.dailyUpdateTime[0]) and entry.end_time.hour >= int(config.dailyUpdateTime[0]):
                                    entry.end_time = datetime.datetime.strptime('1900-01-02 0' + str(int(config.dailyUpdateTime[0])-1) + ':59:59.99999', '%y-%m-%d %H:%M:%S.%f')
                                print("INFO: End Time = {}".format(str(entry.end_time)))
                            overlap_max_seconds=int(entry.overlap_max) * 60
                            print(("INFO: Overlap Max is "+str(overlap_max_seconds)))
                            max_end_time=datetime.datetime.strptime(entry.natural_start_time, self.APP_TIME_FORMAT_STR) + datetime.timedelta(seconds=overlap_max_seconds)
                            if datetime.datetime.strptime(entry.start_time, self.APP_TIME_FORMAT_STR) > max_end_time or datetime.datetime.strptime(entry.start_time, self.APP_TIME_FORMAT_STR) > entry.end_time:
                                print("ALERT: START TIME PAST MAXIMUM ALLOWED TIME, SKIPPING ENTRY")
                                pass
                            else:
                                """Get List of Commercials to Inject"""
                                if self.USING_COMMERCIAL_INJECTION:
                                    list_of_commercials = self.commercials.get_commercials_to_place_between_media(
                                        previous_episode,
                                        entry,
                                        entry.is_strict_time.lower(),
                                        config.dailyUpdateTime
                                    )
                                    for commercial in list_of_commercials:
                                        self.db.add_media_to_daily_schedule(commercial)
                                self.db.add_media_to_daily_schedule(entry)
                                previous_episode = entry
                                if entry.custom_section_name == "TV Shows" and entry.advance_episode != "no":
                                    self.db.update_shows_table_with_last_episode(entry.show_series_title, entry.plex_media_id)
                        else:
                            try:
                                print("INFO: Variable Time: {}".format(str(entry.title).encode(sys.stdout.encoding, errors='replace')))
                            except:
                                pass
                            try:
                                new_starttime = self.calculate_start_time(
                                    previous_episode.end_time,
                                    entry.natural_start_time,
                                    previous_episode.time_shift,
                                    ""
                                )
                            except:
                                print("ERROR: Error in calculate_start_time")
                            print("INFO: New start time:", new_starttime)
                            entry.start_time = datetime.datetime.strptime(new_starttime, self.APP_TIME_FORMAT_STR).strftime(self.APP_TIME_FORMAT_STR)
                            entry.end_time = self.get_end_time_from_duration(entry.start_time, entry.duration)
                            if entry.end_time.hour >= 0 and entry.end_time.hour < int(config.dailyUpdateTime[0]):
                                entry.end_time = entry.end_time + datetime.timedelta(days=1)
                            if natural_start_time.hour < int(config.dailyUpdateTime[0]) and entry.end_time.hour >= int(config.dailyUpdateTime[0]):
                                entry.end_time = datetime.datetime.strptime('1900-01-02 0' + str(int(config.dailyUpdateTime[0])-1) + ':59:59.99999', '%y-%m-%d %H:%M:%S.%f')
                            """Get List of Commercials to inject"""
                            if self.USING_COMMERCIAL_INJECTION:
                                list_of_commercials = self.commercials.get_commercials_to_place_between_media(
                                    previous_episode,
                                    entry,
                                    entry.is_strict_time.lower(),
                                    config.dailyUpdateTime
                                )
                                for commercial in list_of_commercials:
                                    self.db.add_media_to_daily_schedule(commercial)
                            self.db.add_media_to_daily_schedule(entry)
                            previous_episode = entry
                            if entry.custom_section_name == "TV Shows" and entry.advance_episode != "no":
                                self.db.update_shows_table_with_last_episode(entry.show_series_title, entry.plex_media_id)
                    else:
                        self.db.add_media_to_daily_schedule(entry)
                        previous_episode = entry
                        if entry.custom_section_name == "TV Shows" and entry.advance_episode != "no":
                                self.db.update_shows_table_with_last_episode(entry.show_series_title, entry.plex_media_id)
                if self.USING_COMMERCIAL_INJECTION:
                    list_of_commercials = self.commercials.get_commercials_to_place_between_media(
                        previous_episode,
                        "reset",
                        "true",
                        config.dailyUpdateTime
                    )
                    for commercial in list_of_commercials:
                        self.db.add_media_to_daily_schedule(commercial)
                    print("NOTICE: END OF DAY - RESET TIME REACHED")

    def run_commercial_injection(self):

        pass

    def make_xml_schedule(self):

        self.controller.make_xml_schedule(self.db.get_daily_schedule())

    def show_clients(self):

        print("Connected Clients:")
        for i, client in enumerate(self.PLEX.clients()):
            print("INFO: ", str(i + 1)+".", "Client:", client.title)

    def show_schedule(self):

        print("Daily Pseudo Schedule:")
        daily_schedule = self.db.get_daily_schedule()
        for i , entry in enumerate(daily_schedule):
            print(str("INFO {} {} {} {} {} {}".format(str(i + 1)+".", entry[8], entry[11], entry[6], " - ", entry[3])).encode(sys.stdout.encoding, errors='replace'))

    def last_episode(self):
        print("----- Change the 'Last Episode' set for a show. -----")
        print("Enter the name of the show.")
        showName = input("Show Name: ")
        showData = self.db.get_shows(showName)
        #print("SHOW SELECTED: "+showData[3])
        if(showData is not None):
            print("Enter the season and episode numbers for the 'last episode' (episode previous to the episode you wish to be scheduled on next -g run")
            sNo = input("Season Number: ")
            eNo = input("Episode Number: ")
            episodeData = self.db.get_episode_from_season_episode(showName,sNo,eNo)
            if(episodeData is not None):
                print("Setting "+episodeData[7]+" - "+episodeData[3]+" S"+str(episodeData[6])+"E"+str(episodeData[5])+" as the Last Episode in the Shows Database")
                self.db.update_shows_table_with_last_episode(episodeData[7], episodeData[8])
            else:
                print("ERROR: EPISODE NOT FOUND IN PSEUDO CHANNEL DATABASE")
                sys.exit(1)
        else:
            print("ERROR: SHOW NOT FOUND IN PSEUDO CHANNEL DATABASE")
            sys.exit(1)


    def episode_randomizer(self):
        all_shows = list(self.db.get_shows_titles())
        shows_list = []
        for one_show in all_shows:
            shows_list.append(str(one_show[0]))
        for a_show in shows_list:
            a_show = str(a_show)
            try:
                random_episode = self.db.get_random_episode_of_show(a_show)
                print(a_show + " - " + random_episode[3])
                self.db.update_shows_table_with_last_episode(a_show, random_episode[8])
            except TypeError as e:
                print("ERROR: "+a_show)
                print(e)
                random_episode = self.db.get_random_episode_of_show_alt(a_show)
                print(a_show + " - " + random_episode[3])
                self.db.update_shows_table_with_last_episode_alt(a_show, random_episode[8])
                continue

    def write_json_to_file(self, data, fileName):

        fileName = fileName
        writepath = './'
        if os.path.exists(writepath+fileName):
            os.remove(writepath+fileName)
        mode = 'a' if os.path.exists(writepath) else 'w'
        with open(writepath+fileName, mode) as f:
            f.write(data)

    def export_queue(self):

        shows_table = self.db.get_shows_table()
        json_string = json.dumps(shows_table)
        print("NOTICE: Exporting queue ")
        self.write_json_to_file(json_string, "pseudo-queue.json")
        print("NOTICE: Done.")
        self.export_daily_schedule()

    def import_queue(self):

        """Dropping previous shows table before adding the imported data"""
        #self.db.clear_shows_table()
        with open('pseudo-queue.json') as data_file:    
            data = json.load(data_file)
        #print(data)
        for row in data:
            print("lastEpisodeTitle:", row[5])
            self.db.import_shows_table_by_row(
                row[2], 
                row[3], 
                row[4], 
                row[5], 
                row[6], 
                row[7],
            )
        print("NOTICE: Queue Import Complete")
        self.import_daily_schedule()

    def export_daily_schedule(self):

        daily_schedule_table = self.db.get_daily_schedule()
        json_string = json.dumps(daily_schedule_table)
        print("NOTICE: Exporting Daily Schedule ")
        self.write_json_to_file(json_string, "pseudo-daily_schedule.json")
        print("NOTICE: Done.")

    def import_daily_schedule(self):

        """Dropping previous Daily Schedule table before adding the imported data"""
        self.db.remove_all_daily_scheduled_items()
        with open('pseudo-daily_schedule.json') as data_file:    
            data = json.load(data_file)
        #pprint(data)
        for row in data:
            """print row"""
            self.db.import_daily_schedule_table_by_row(
                row[2], 
                row[3], 
                row[4], 
                row[5], 
                row[6], 
                row[7], 
                row[8], 
                row[9], 
                row[10], 
                row[11], 
                row[12],
                row[13],
            )
        print("NOTICE: Daily Schedule Import Complete")

    def get_daily_schedule_cache_as_json(self):

        data = []
        try:
            with open('../.pseudo-cache/daily-schedule.json') as data_file:    
                data = json.load(data_file)
            #pprint(data)
        except IOError as e:
            print("ERROR: Having issues opening the pseudo-cache file.")
            print(e)
        return data

    def save_daily_schedule_as_json(self):

        daily_schedule_table = self.db.get_daily_schedule()
        json_string = json.dumps(daily_schedule_table)
        print("NOTICE: Saving Daily Schedule Cache ")
        self.save_file(json_string, 'daily-schedule.json', '../.pseudo-cache/')

    def save_file(self, data, filename, path="./"):

        fileName = filename
        writepath = path
        if not os.path.exists(writepath):
            os.makedirs(writepath)
        if os.path.exists(writepath+fileName):
            os.remove(writepath+fileName)
        mode = 'w'
        with open(writepath+fileName, mode) as f:
            f.write(data)

    def rotate_log(self):

        try:
            os.remove('../pseudo-channel.log')
        except OSError:
            pass
        try:
            os.remove('./pseudo-channel.log')
        except OSError:
            pass

    def signal_term_handler(self, signal, frame):

        logging.info('NOTICE: got SIGTERM')
        self.controller.stop_media()
        self.exit_app()
        sys.exit(0)

    def exit_app(self):

        logging.info('NOTICE: - Exiting Pseudo TV & cleaning up.')
        for i in self.MEDIA:
            del i
        self.MEDIA = None
        self.controller = None
        self.db = None
        sleep(1)

if __name__ == '__main__':

    pseudo_channel = PseudoChannel()
    banner = textwrap.dedent('''\
#   __              __                        
#  |__)_ _    _| _ /  |_  _  _  _  _|    _    
#  |  _)(-|_|(_|(_)\__| )(_|| )| )(-|.  |_)\/ 
#                                       |  /  

            A Custom TV Channel for Plex
''')
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = banner)
    '''
    * 
    * Primary arguments: "python PseudoChannel.py -u -xml -g -r"
    *
    '''
    parser.add_argument('-u', '--update',
                         action='store_true',
                         help='Update the local database with Plex libraries.')
    parser.add_argument('-um', '--update_movies',
                         action='store_true',
                         help='Update the local database with Plex MOVIE libraries ONLY.')
    parser.add_argument('-utv', '--update_tv',
                         action='store_true',
                         help='Update the local database with Plex TV libraries ONLY.')
    parser.add_argument('-up', '--update_playlist',
                         action='store_true',
                         help='Update the local database with Plex PLAYLIST libraries ONLY.')
    parser.add_argument('-uc', '--update_commercials',
                         action='store_true',
                         help='Update the local database with Plex COMMERCIAL libraries ONLY.')
    parser.add_argument('-xml', '--xml',
                         action='store_true', 
                         help='Update the local database with the pseudo_schedule.xml.')
    parser.add_argument('-g', '--generate_schedule',
                         action='store_true', 
                         help='Generate the daily schedule.')
    parser.add_argument('-r', '--run',
                         action='store_true', 
                         help='Run this program.')
    parser.add_argument('-ep', '--episode_randomizer',
                         action='store_true',
                         help='Randomize all shows episode progress.')
    parser.add_argument('-le', '--last_episode',
                         action='store_true',
                         help='Set last episode for a show. The next time -g is run, it will start with the episode after the one set.')
    '''
    * 
    * Show connected clients: "python PseudoChannel.py -c"
    *
    '''
    parser.add_argument('-c', '--show_clients',
                         action='store_true',
                         help='Show Plex clients.')
    '''
    * 
    * Show schedule (daily): "python PseudoChannel.py -s"
    *
    '''
    parser.add_argument('-s', '--show_schedule',
                         action='store_true',
                         help='Show scheduled media for today.')
    '''
    * 
    * Make XML / HTML Schedule: "python PseudoChannel.py -m"
    *
    '''
    parser.add_argument('-m', '--make_html',
                         action='store_true',
                         help='Makes the XML / HTML schedule based on the daily_schedule table.')
    '''
    * 
    * Export queue: "python PseudoChannel.py -e"
    *
    '''
    parser.add_argument('-e', '--export_queue',
                         action='store_true',
                         help='Exports the current queue for episodes.')
    '''
    * 
    * Import queue: "python PseudoChannel.py -i"
    *
    '''
    parser.add_argument('-i', '--import_queue',
                         action='store_true',
                         help='Imports the current queue for episodes.')
    '''
    * 
    * Export Daily Schedule: "python PseudoChannel.py -eds"
    *
    '''
    parser.add_argument('-eds', '--export_daily_schedule',
                         action='store_true',
                         help='Exports the current Daily Schedule.')
    '''
    * 
    * Import Daily Schedule: "python PseudoChannel.py -ids"
    *
    '''
    parser.add_argument('-ids', '--import_daily_schedule',
                         action='store_true',
                         help='Imports the current Daily Schedule.')
    globals().update(vars(parser.parse_args()))
    args = parser.parse_args()
    if args.update:
        pseudo_channel.update_db()
    if args.update_movies:
        pseudo_channel.update_db_movies()
    if args.update_playlist:
        pseudo_channel.update_db_playlist()
    if args.update_tv:
        pseudo_channel.update_db_tv()
    if args.update_commercials:
        pseudo_channel.update_db_comm()
    if args.xml:
        pseudo_channel.update_schedule()
    if args.episode_randomizer:
        pseudo_channel.episode_randomizer()
    if args.last_episode:
        pseudo_channel.last_episode()
    if args.show_clients:
        pseudo_channel.show_clients()
    if args.show_schedule:
        pseudo_channel.show_schedule()
    if args.export_queue:
        pseudo_channel.export_queue()
    if args.import_queue:
        pseudo_channel.import_queue()
    if args.export_daily_schedule:
        pseudo_channel.export_daily_schedule()
    if args.import_daily_schedule:
        pseudo_channel.import_daily_schedule()
    if args.generate_schedule:
        if pseudo_channel.DEBUG:
            pseudo_channel.generate_daily_schedule()
        else:
            try:
                pseudo_channel.generate_daily_schedule()
            except:
                print("ERROR: Recieved error when running generate_daily_schedule()")
    if args.make_html:
        pseudo_channel.make_xml_schedule()
    if args.run:
        print(banner)
        print("INFO: To run this in the background:")
        print("screen -d -m bash -c 'python PseudoChannel.py -r; exec sh'")
        """Every minute on the minute check the DB startTimes of all media to 
           determine whether or not to play. Also, check the now_time to
           see if it's midnight (or 23.59), if so then generate a new daily_schedule
            
        """
        """Every <user specified day> rotate log"""
        dayToRotateLog = pseudo_channel.ROTATE_LOG.lower()
        schedule.every().friday.at("00:00").do(pseudo_channel.rotate_log)
        logging.info("NOTICE: Running PseudoChannel.py -r")
        def trigger_what_should_be_playing_now():

            def nearest(items, pivot):
                return min(items, key=lambda x: abs(x - pivot))

            #dates_list = [datetime.datetime.strptime(''.join(str(date[8])), pseudo_channel.APP_TIME_FORMAT_STR) for date in daily_schedule]
            now = datetime.datetime.now()
            #now = now.replace(year=1900, month=1, day=1)
            #closest_media = nearest(dates_list, now)
            #print closest_media
            prevItem = None
            db = PseudoChannelDatabase("pseudo-channel.db")
            item = db.get_now_playing()
            item_time = datetime.datetime.strptime(''.join(str(item[8])), pseudo_channel.APP_TIME_FORMAT_STR)
            #if item_time == closest_media:
            #print "Line 1088, Here", item
            elapsed_time = item_time - now
            print("INFO: "+str(elapsed_time.total_seconds()))
            try:
                endTime = datetime.datetime.strptime(item[9], '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                endTime = datetime.datetime.strptime(item[9], '%Y-%m-%d %H:%M:%S')
            # we need to play the content and add an offest
            if elapsed_time.total_seconds() < 0 and \
               endTime > now:
                print(str("NOTICE: Queueing up {} to play right away.".format(item[3])).encode('UTF-8'))
                offset = int(abs(elapsed_time.total_seconds() * 1000))
                try:
                    nat_start = datetime.datetime.strptime(item[9], '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(milliseconds=item[7])
                except:
                    nat_start = datetime.datetime.strptime(item[9], '%Y-%m-%d %H:%M:%S') - datetime.timedelta(milliseconds=item[7])
                schedule_offset = nat_start - datetime.datetime.strptime(item[8], pseudo_channel.APP_TIME_FORMAT_STR)
                schedule_offset = schedule_offset.total_seconds()
                print("INFO: Schedule Offset = " + str(schedule_offset))
                nat_start = nat_start.strftime(pseudo_channel.APP_TIME_FORMAT_STR)
                print("INFO: Natural Start Time:")
                print(nat_start)
                daily_schedule = pseudo_channel.db.get_daily_schedule()
                if schedule_offset < 0:
                    schedule_offset_ms = abs(schedule_offset) * 1000
                    offset_plus = int(offset + abs(schedule_offset_ms))
                    print("INFO: Updated Offset = " + str(offset_plus))
                    pseudo_channel.controller.play(item, daily_schedule, offset_plus)
                else:
                    print("INFO: No Offset Update")
                    pseudo_channel.controller.play(item, daily_schedule, offset)

        def job_that_executes_once(item, schedulelist):

            print(str("NOTICE: Readying media: '{}'".format(item[3])).encode('UTF-8'))
            next_start_time = datetime.datetime.strptime(item[8], pseudo_channel.APP_TIME_FORMAT_STR)
            now = datetime.datetime.now()
            #now = now.replace(year=1900, month=1, day=1)
            time_diff = next_start_time - now
            nat_start = datetime.datetime.strptime(item[9], '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(milliseconds=item[7])
            schedule_offset = nat_start - datetime.datetime.strptime(item[8], pseudo_channel.APP_TIME_FORMAT_STR)
            schedule_offset = schedule_offset.total_seconds()
            print("INFO: Schedule Offset = " + str(schedule_offset))
            nat_start = nat_start.strftime(pseudo_channel.APP_TIME_FORMAT_STR)
            print("INFO: Natural Start Time: " + str(nat_start))
            daily_schedule = pseudo_channel.db.get_daily_schedule()
            if time_diff.total_seconds() > 0:
                nat_start = datetime.datetime.strptime(item[9], '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(milliseconds=item[7])
                schedule_offset = nat_start - datetime.datetime.strptime(item[8], pseudo_channel.APP_TIME_FORMAT_STR)
                schedule_offset = schedule_offset.total_seconds()
                print("INFO: Schedule Offset = " + str(schedule_offset))
                nat_start = nat_start.strftime(pseudo_channel.APP_TIME_FORMAT_STR)
                print("INFO: Natural Start Time: " + str(nat_start))
                print("NOTICE: Sleeping for {} seconds before playing: '{}'".format(time_diff.total_seconds(), item[3]))
                sleep(int(time_diff.total_seconds()))
                if pseudo_channel.DEBUG:
                    print("NOTICE: Woke up!")
                if schedule_offset < 0: #OFFSET CHECKER
                    schedule_offset_ms = abs(schedule_offset) * 1000
                    print("INFO: Updated Offset = " + str(schedule_offset_ms))
                    pseudo_channel.controller.play(item, daily_schedule, schedule_offset_ms)
                else:
                    print("INFO: job_that_executes_once - No offset")
                    pseudo_channel.controller.play(item, daily_schedule)
            else:
                nat_start = datetime.datetime.strptime(item[9], '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(milliseconds=item[7])
                schedule_offset = nat_start - datetime.datetime.strptime(item[8], pseudo_channel.APP_TIME_FORMAT_STR)
                schedule_offset = schedule_offset.total_seconds()
                print("INFO: Schedule Offset = " + str(schedule_offset))
                nat_start = nat_start.strftime(pseudo_channel.APP_TIME_FORMAT_STR)
                print("INFO: Natural Start Time: " + str(nat_start))
                if schedule_offset < 0:
                    schedule_offset_ms = int(abs(schedule_offset) * 1000)
                    print("INFO: Updated Offset = " + str(schedule_offset_ms))
                    pseudo_channel.controller.play(item, daily_schedule, schedule_offset_ms)
                else:
                    print("INFO: job_that_executes_once - No offset 2")
                    pseudo_channel.controller.play(item, daily_schedule)
            return schedule.CancelJob

        def generate_memory_schedule(schedulelist, isforupdate=False):

            print("NOTICE: Generating Memory Schedule.")
            now = datetime.datetime.now()
            #now = now.replace(year=1900, month=1, day=1)
            pseudo_cache = pseudo_channel.get_daily_schedule_cache_as_json()
            prev_end_time_to_watch_for = None
            if pseudo_channel.USE_OVERRIDE_CACHE and isforupdate:
                for cached_item in pseudo_cache:
                    prev_start_time = datetime.datetime.strptime(cached_item[8], pseudo_channel.APP_TIME_FORMAT_STR)
                    try:
                        prev_end_time = datetime.datetime.strptime(cached_item[9], '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        prev_end_time = datetime.datetime.strptime(cached_item[9], '%Y-%m-%d %H:%M:%S')
                    """If update time is in between the prev media start / stop then there is overlap"""
                    if prev_start_time < now and prev_end_time > now:
                        try:
                            print("INFO: It looks like there is update schedule overlap", cached_item[3])
                        except:
                            pass
                        prev_end_time_to_watch_for = prev_end_time
            for item in schedulelist:
                trans_time = datetime.datetime.strptime(item[8], pseudo_channel.APP_TIME_FORMAT_STR).strftime("%H:%M")
                new_start_time = datetime.datetime.strptime(item[8], pseudo_channel.APP_TIME_FORMAT_STR)
                if prev_end_time_to_watch_for == None:
                    schedule.every().day.at(trans_time).do(job_that_executes_once, item, schedulelist).tag('daily-tasks')
                else:
                    """If prev end time is more then the start time of this media, skip it"""
                    if prev_end_time_to_watch_for > new_start_time:
                        try:
                            print("NOTICE: Skipping scheduling item due to cached overlap.", item[3])
                        except:
                            pass
                        continue
                    else:
                        schedule.every().day.at(trans_time).do(job_that_executes_once, item, schedulelist).tag('daily-tasks')
            print("NOTICE: Done.")
        generate_memory_schedule(pseudo_channel.db.get_daily_schedule())
        daily_update_time = datetime.datetime.strptime(
            pseudo_channel.translate_time(
                pseudo_channel.DAILY_UPDATE_TIME
            ),
            pseudo_channel.APP_TIME_FORMAT_STR
        ).strftime('%H:%M')

        def go_generate_daily_sched():

            """Saving current daily schedule as cached .json"""
            pseudo_channel.save_daily_schedule_as_json()

            schedule.clear('daily-tasks')

            sleep(1)

            try:
                pseudo_channel.generate_daily_schedule()
            except:
                print("ERROR: Recieved error when running generate_daily_schedule()")
            generate_memory_schedule(pseudo_channel.db.get_daily_schedule(), True)

        """Commenting out below and leaving all updates to be handled by cron task"""
        """schedule.every().day.at(daily_update_time).do(
            go_generate_daily_sched
        ).tag('daily-update')"""

        sleep_before_triggering_play_now = 1

        '''When the process is killed, stop any currently playing media & cleanup'''
        signal.signal(signal.SIGTERM, pseudo_channel.signal_term_handler)

        try:
            while True:
                schedule.run_pending()
                sleep(0.1)
                if sleep_before_triggering_play_now:
                    logging.info("NOTICE: Successfully started PseudoChannel.py")
                    trigger_what_should_be_playing_now()
                    sleep_before_triggering_play_now = 0
                    #generate_memory_schedule(pseudo_channel.db.get_daily_schedule())
        except KeyboardInterrupt:
            print('ALERT: Manual break by user!')

