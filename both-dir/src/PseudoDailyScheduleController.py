#!/usr/bin/env python

import os, sys
import socket
import logging
import logging.handlers
from datetime import datetime
from datetime import time
from datetime import timedelta
from datetime import tzinfo
import pytz
import sqlite3
import _thread,socketserver,http.server
from plexapi.server import PlexServer
from yattag import Doc
from yattag import indent
import pseudo_config as config
class PseudoDailyScheduleController():

    def __init__(self, 
                 server, 
                 token, 
                 clients, 
                 controllerServerPath = '', 
                 controllerServerPort = '8000', 
                 debugMode = False,
                 htmlPseudoTitle = "Daily PseudoChannel"
                 ):

        self.PLEX = PlexServer(server, token)
        self.BASE_URL = server
        self.TOKEN = token
        self.PLEX_CLIENTS = clients
        self.CONTROLLER_SERVER_PATH = controllerServerPath
        self.CONTROLLER_SERVER_PORT = controllerServerPort if controllerServerPort != '' else '80'
        self.DEBUG = debugMode
        self.webserverStarted = False
        self.HTML_PSEUDO_TITLE = htmlPseudoTitle
        try: 
            self.my_logger = logging.getLogger('MyLogger')
            self.my_logger.setLevel(logging.DEBUG)
            self.handler = logging.handlers.SysLogHandler(address = '/dev/log')
            self.my_logger.addHandler(self.handler)
        except:
            pass

    '''
    *
    * Get the full image url (including plex token) from the local db.
    * @param seriesTitle: case-unsensitive string of the series title
    * @return string: full path of to the show image
    *
    '''
    def get_show_photo(self, section, showtitle, durationAmount):

        backgroundImagePath = None
        backgroundImgURL = ''
        # First, we are going to search for movies/commercials
        try:
             movies =  self.PLEX.library.section(section).search(title=showtitle)
             for item in movies:
                    if item.duration == durationAmount:
                        backgroundImagePath = item
                        break
        except:
            return backgroundImgURL
        
        if backgroundImagePath == None:
            # We will try the old way, for the sake of TV Shows
            try:
                backgroundImagePath = self.PLEX.library.section(section).get(showtitle)
            except:
                return backgroundImgURL
        
        if backgroundImagePath != None and isinstance(backgroundImagePath.art, str):
            backgroundImgURL = self.BASE_URL+backgroundImagePath.art+"?X-Plex-Token="+self.TOKEN
        return backgroundImgURL

    def start_server(self):

        if self.webserverStarted == False and self.CONTROLLER_SERVER_PATH != '':
            """Changing dir to the schedules dir."""
            web_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'schedules'))
            os.chdir(web_dir)
            PORT = int(self.CONTROLLER_SERVER_PORT)
            class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

                def log_message(self, format, *args):
                    return

            global httpd
            try:
                # create the httpd handler for the simplehttpserver
                # we set the allow_reuse_address incase something hangs can still bind to port
                class ReusableTCPServer(SocketServer.TCPServer): allow_reuse_address=True
                # specify the httpd service on 0.0.0.0 (all interfaces) on port 80
                httpd = ReusableTCPServer(("0.0.0.0", PORT),MyHandler)
                # thread this mofo
                thread.start_new_thread(httpd.serve_forever,())
            # handle keyboard interrupts
            except KeyboardInterrupt:
                core.print_info("Exiting the SET web server...")
                httpd.socket.close()
            except socket.error as exc:
                print("ERROR: Caught exception socket.error : %s" % exc)
            # handle the rest
            self.webserverStarted = True

    def get_xml_from_daily_schedule(self, currentTime, bgImageURL, datalist):

        now = datetime.now()
        new_day = now + timedelta(days=1)
        time = now.strftime("%B %d, %Y")
        update_time = datetime.strptime(config.dailyUpdateTime,'%H:%M').replace(year=int(now.strftime('%Y')),month=int(now.strftime('%m')),day=int(now.strftime('%d')))
        doc, tag, text, line = Doc(

        ).ttl()
        doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
        with tag('schedule', currently_playing_bg_image=bgImageURL if bgImageURL != None else ''):
            previous_row = None
            for row in datalist:
                try:
                    start_time = datetime.strptime(row[8],'%I:%M:%S %p')
                except:
                    start_time = datetime.strptime(row[8],'%H:%M:%S')
                if start_time > update_time: #checking for after midnight but before reset (from config)
                    try:
                        current_start_time = datetime.strptime(row[8],'%I:%M:%S %p').replace(year=int(now.strftime('%Y')),month=int(now.strftime('%m')),day=int(now.strftime('%d')))
                    except:
                        current_start_time = datetime.strptime(row[8],'%H:%M:%S').replace(year=int(now.strftime('%Y')),month=int(now.strftime('%m')),day=int(now.strftime('%d')))
                else:
                    try:
                        current_start_time = datetime.strptime(row[8],'%I:%M:%S %p').replace(year=int(new_day.strftime('%Y')),month=int(new_day.strftime('%m')),day=int(new_day.strftime('%d')))
                    except:
                        current_start_time = datetime.strptime(row[8],'%H:%M:%S').replace(year=int(new_day.strftime('%Y')),month=int(new_day.strftime('%m')),day=int(new_day.strftime('%d')))
                current_start_time_unix = (current_start_time - datetime(1970,1,1)).total_seconds()
                current_start_time_string = current_start_time.strftime('%H:%M:%S')
                try:
                    if_end_time = datetime.strptime(row[9],'%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    if_end_time = datetime.strptime(row[9],'%Y-%m-%d %H:%M:%S')
                if if_end_time.replace(year=int(now.strftime('%Y')),month=int(now.strftime('%m')),day=int(now.strftime('%d'))) > update_time: #checking for after midnight but before reset (from config)
                    current_end_time = if_end_time.replace(year=int(now.strftime('%Y')),month=int(now.strftime('%m')),day=int(now.strftime('%d')))
                else:
                    current_end_time = if_end_time.replace(year=int(new_day.strftime('%Y')),month=int(new_day.strftime('%m')),day=int(new_day.strftime('%d')))
                current_end_time_unix = (current_end_time - datetime(1970,1,1)).total_seconds()
                current_end_time_string = current_end_time.strftime('%H:%M:%S')
                if previous_row != None:
                    #compare previous end time to current start time
                    try:
                        previous_end_time = datetime.strptime(previous_row[9], '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        previous_end_time = datetime.strptime(previous_row[9], '%Y-%m-%d %H:%M:%S')
                    if previous_end_time > update_time: #checking for after midnight but before reset (from config)
                        previous_end_time = previous_end_time.replace(year=int(now.strftime('%Y')),month=int(now.strftime('%m')),day=int(now.strftime('%d')))
                    else:
                        previous_end_time = previous_end_time.replace(year=int(new_day.strftime('%Y')),month=int(new_day.strftime('%m')),day=int(new_day.strftime('%d')))
                    if previous_end_time > current_start_time:
                        #if previous end time is later than start time, change end time
                        previous_end_time = current_start_time - timedelta(seconds=1)
                    #convert start and end times to unix
                    previous_end_time_unix = (previous_end_time - datetime(1970,1,1)).total_seconds()
                    #convert start and end times to the same readable format
                    previous_end_time_string = previous_end_time.strftime('%H:%M:%S')
                    if str(previous_row[11]) == "Commercials" and self.DEBUG == False:
                        continue
                    try:
                        timeB = datetime.strptime(previous_row[8], '%I:%M:%S %p')
                    except:
                        timeB = datetime.strptime(previous_row[8], '%H:%M:%S')
                    if currentTime == None:
                        with tag('time',
                                ('key', str(previous_row[12])),
                                ('current', 'false'),
                                ('type', str(previous_row[11])),
                                ('show-title', str(previous_row[6])),
                                ('show-season', str(previous_row[5])),
                                ('show-episode', str(previous_row[4])),
                                ('title', str(previous_row[3])),
                                ('duration', str(previous_row[7])),
                                ('time-start', str(previous_start_time_string)),
                                ('time-end', str(previous_end_time.strftime('%H:%M:%S'))),
                                ('time-start-unix', str(previous_start_time_unix)),
                                ('time-end-unix', str(previous_end_time_unix)),
                                ('library', str(previous_row[13])),
                            ):
                            text(previous_row[8])
                    elif currentTime.hour == timeB.hour and currentTime.minute == timeB.minute:
                        with tag('time',
                                ('key', str(previous_row[12])),
                                ('current', 'true'),
                                ('type', str(previous_row[11])),
                                ('show-title', str(previous_row[6])),
                                ('show-season', str(previous_row[5])),
                                ('show-episode', str(previous_row[4])),
                                ('title', str(previous_row[3])),
                                ('duration', str(previous_row[7])),
                                ('time-start', str(previous_start_time_string)),
                                ('time-end', str(previous_end_time.strftime('%H:%M:%S'))),
                                ('time-start-unix', str(previous_start_time_unix)),
                                ('time-end-unix', str(previous_end_time_unix)),
                                ('library', str(previous_row[13])),
                            ):
                            text(previous_row[8])
                    else:
                        with tag('time',
                                ('key', str(previous_row[12])),
                                ('current', 'false'),
                                ('type', str(previous_row[11])),
                                ('show-title', str(previous_row[6])),
                                ('show-season', str(previous_row[5])),
                                ('show-episode', str(previous_row[4])),
                                ('title', str(previous_row[3])),
                                ('duration', str(previous_row[7])),
                                ('time-start', str(previous_start_time_string)),
                                ('time-end', str(previous_end_time.strftime('%H:%M:%S'))),
                                ('time-start-unix', str(previous_start_time_unix)),
                                ('time-end-unix', str(previous_end_time_unix)),
                                ('library', str(previous_row[13])),
                            ):
                            text(previous_row[8])
                previous_start_time = current_start_time
                previous_start_time_unix = current_start_time_unix
                previous_start_time_string = current_start_time_string
                previous_row = row
#            if str(row[11]) == "Commercials" and self.DEBUG == False:
#                continue
            try:
                timeB = datetime.strptime(row[8], '%I:%M:%S %p')
            except:
                timeB = datetime.strptime(row[8], '%H:%M:%S')
            if currentTime == None:
                with tag('time',
                        ('key', str(row[12])),
                        ('current', 'false'),
                        ('type', str(row[11])),
                        ('show-title', str(row[6])),
			('show-season', str(row[5])),
			('show-episode', str(row[4])),
                        ('title', str(row[3])),
			('duration', str(row[7])),
                        ('time-start', str(current_start_time_string)),
			('time-end', str(current_end_time_string)),
                        ('time-start-unix', str(current_start_time_unix)),
                        ('time-end-unix', str(current_end_time_unix)),
			('library', str(row[13])),
                    ):
                    text(row[8])
            elif currentTime.hour == timeB.hour and currentTime.minute == timeB.minute:
                with tag('time',
                        ('key', str(row[12])),
                        ('current', 'true'),
                        ('type', str(row[11])),
	                ('show-title', str(row[6])),
                        ('show-season', str(row[5])),
                        ('show-episode', str(row[4])),
                        ('title', str(row[3])),
                        ('duration', str(row[7])),
                        ('time-start', str(current_start_time_string)),
                        ('time-end', str(current_end_time_string)),
                        ('time-start-unix', str(current_start_time_unix)),
                        ('time-end-unix', str(current_end_time_unix)),
                        ('library', str(row[13])),
                    ):
                    text(row[8])
            else:
                with tag('time',
                        ('key', str(row[12])),
                        ('current', 'false'),
                        ('type', str(row[11])),
                        ('show-title', str(row[6])),
                        ('show-season', str(row[5])),
                        ('show-episode', str(row[4])),
                        ('title', str(row[3])),
                        ('duration', str(row[7])),
                        ('time-start', str(current_start_time_string)),
                        ('time-end', str(current_end_time_string)),
                        ('time-start-unix', str(current_start_time_unix)),
                        ('time-end-unix', str(current_end_time_unix)),
                        ('library', str(row[13])),
                    ):
                    text(row[8])
        return indent(doc.getvalue())

    '''
    *
    * Get the generated html for the .html file that is the schedule. 
    * ...This is used whenever a show starts or stops in order to add and remove various styles.
    * @param currentTime: datetime object 
    * @param bgImageURL: str of the image used for the background
    * @return string: the generated html content
    *
    '''
    def get_html_from_daily_schedule(self, currentTime, bgImageURL, datalist, nowPlayingTitle):

        now = datetime.now()
        now = now.replace(year=1900, month=1, day=1)
        midnight = now.replace(hour=23, minute=59, second=59)
        #mutto233 put this here, because to be honest, isn't the current time always now?
        if currentTime != None:
            currentTime=now
            
            
        time = datetime.now().strftime("%B %d, %Y")
        doc, tag, text, line = Doc(

        ).ttl()
        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('head'):
                with tag('title'):
                    text(time + " - Daily Pseudo Schedule")
                doc.asis('<link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css" rel="stylesheet">')
                doc.asis('<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>')
                doc.asis("""
        <script>
        $(function(){

            var refreshFlag = '';
            """
            +"""var controllerServerPath ='"""+self.CONTROLLER_SERVER_PATH+":"+self.CONTROLLER_SERVER_PORT+"""';

            if(controllerServerPath != ''){

                console.log("here");

                window.setInterval(function(){

                $.ajax({
                        url: controllerServerPath+"/pseudo_refresh.txt",
                        async: true,   // asynchronous request? (synchronous requests are discouraged...)
                        cache: false,   // with this, you can force the browser to not make cache of the retrieved data
                        dataType: "text",  // jQuery will infer this, but you can set explicitly
                        success: function( data, textStatus, jqXHR ) {
                            newFlag = data; 

                            if(refreshFlag != ''){
                            
                                if (refreshFlag != newFlag){

                                    location.reload();

                                } else {

                                    //do nothing
                                    console.log("skip");

                                }

                            } else {

                                refreshFlag = newFlag;

                            }

                        }
                    });
                }, 1000);

            } else {

                setTimeout(function() {location.reload();}, 30000);

            }

        });
        </script>
                            """)
                if bgImageURL != None:
                    doc.asis('<style>body{ background:transparent!important; } html { background: url('+bgImageURL+') no-repeat center center fixed; -webkit-background-size: cover;-moz-background-size: cover;-o-background-size: cover;background-size: cover;}.make-white { padding: 24px; background:rgba(255,255,255, 0.9); }</style>')
            with tag('body'):
                with tag('div', klass='container mt-3'):
                    with tag('div', klass='row make-white'):
                        with tag('div'):
                            with tag('div'):
                                line('h1', self.HTML_PSEUDO_TITLE, klass='col-12 pl-0')
                            with tag('div'):
                                line('h3', time, klass='col-12 pl-1')
                                line('h3', 
                                     "Now Playing: "+nowPlayingTitle, 
                                     klass='col-12 pl-1',
                                     style="color:red;")
                        with tag('table', klass='col-12 table table-bordered table-hover'):
                            with tag('thead', klass='table-info'):
                                with tag('tr'):
                                    with tag('th'):
                                        text('#')
                                    with tag('th'):
                                        text('Type')
                                    with tag('th'):
                                        text('Series')
                                    with tag('th'):
                                        text('Title')
                                    with tag('th'):
                                        text('Start Time')
                            numberIncrease = 0
                            for row in datalist:
                                if str(row[11]) == "Commercials" and self.DEBUG == False:
                                    continue
                                numberIncrease += 1
                                with tag('tbody'):
                                    if currentTime != None:
                                        currentTime = currentTime.replace(year=1900, month=1, day=1)
                                    try:
                                        timeBStart = datetime.strptime(row[8], '%I:%M:%S %p')
                                    except:
                                        timeBStart = datetime.strptime(row[8], '%H:%M:%S')
                                    timeBStart = timeBStart.replace(year=1900, month=1, day=1)
                                    try:
                                        timeBEnd = datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S.%f')
                                        timeBEnd = timeBEnd.replace(day=1)
                                    except:
                                        timeBEnd = datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S')
                                        timeBEnd = timeBEnd.replace(day=1)
                                    if currentTime == None:
                                        with tag('tr'):
                                            with tag('th', scope='row'):
                                                text(numberIncrease)
                                            with tag('td'):
                                                text(row[11])
                                            with tag('td'):
                                                text(row[6])
                                            with tag('td'):
                                                text(row[3])
                                            with tag('td'):
                                                text(row[8])
                                    elif ((currentTime - timeBStart).total_seconds() >= 0 and \
                                         (timeBEnd - currentTime).total_seconds() >= 0) or \
                                         ((timeBStart - timeBEnd).total_seconds() >= 0 and \
                                         (((currentTime-midnight.replace(hour=0,minute=0,second=0)).total_seconds() >= 0 and \
                                          (timeBEnd-currentTime).total_seconds() >= 0) or
                                         ((currentTime-timeBStart).total_seconds() >= 0 and \
                                          (midnight-currentTime).total_seconds() >= 0))):          
                                        
                                            print("INFO: Currently Playing:", row[3])

                                            with tag('tr', klass='bg-info'):
                                                with tag('th', scope='row'):
                                                    text(numberIncrease)
                                                with tag('td'):
                                                    text(row[11])
                                                with tag('td'):
                                                    text(row[6])
                                                with tag('td'):
                                                    text(row[3])
                                                with tag('td'):
                                                    text(row[8])
                                    else:
                                        with tag('tr'):
                                            with tag('th', scope='row'):
                                                text(numberIncrease)
                                            with tag('td'):
                                                text(row[11])
                                            with tag('td'):
                                                text(row[6])
                                            with tag('td'):
                                                text(row[3])
                                            with tag('td'):
                                                text(row[8])
        return indent(doc.getvalue())

    '''
    *
    * Create 'schedules' dir & write the generated html to .html file.
    * @param data: html string
    * @return null
    *
    '''
    def write_schedule_to_file(self, data):

        now = datetime.now()
        fileName = "index.html"
        writepath = './' if os.path.basename(os.getcwd()) == "schedules" else "./schedules/"
        if not os.path.exists(writepath):
            os.makedirs(writepath)
        if os.path.exists(writepath+fileName):
            os.remove(writepath+fileName)
        mode = 'a' if os.path.exists(writepath) else 'w'
        with open(writepath+fileName, mode) as f:
            f.write(data)
        self.start_server()

    '''
    *
    * Create 'schedules' dir & write the generated xml to .xml file.
    * @param data: xml string
    * @return null
    *
    '''
    def write_xml_to_file(self, data):

        now = datetime.now()
        fileName = "pseudo_schedule.xml"
        writepath = './' if os.path.basename(os.getcwd()) == "schedules" else "./schedules/"
        if not os.path.exists(writepath):
            os.makedirs(writepath)
        if os.path.exists(writepath+fileName):
            os.remove(writepath+fileName)
        mode = 'a' if os.path.exists(writepath) else 'w'
        with open(writepath+fileName, mode) as f:
            f.write(data)

    '''
    *
    * Write 0 or 1 to file for the ajax in the schedule.html to know when to refresh
    * @param data: xml string
    * @return null
    *
    '''
    def write_refresh_bool_to_file(self):

        fileName = "pseudo_refresh.txt"
        writepath = './' if os.path.basename(os.getcwd()) == "schedules" else "./schedules/"
        first_line = ''
        if not os.path.exists(writepath):
            os.makedirs(writepath)
        if not os.path.exists(writepath+fileName):
            open(writepath+fileName, 'w').close()
        mode = 'r+'
        with open(writepath+fileName, mode) as f:
            f.seek(0)
            first_line = f.read()  
            if self.DEBUG:
                print("INFO: Html refresh flag: {}".format(first_line))
            if first_line == '' or first_line == "0":
                f.seek(0)
                f.truncate()
                f.write("1")
            else:
                f.seek(0)
                f.truncate()
                f.write("0")

    '''
    *
    * Trigger "playMedia()" on the Python Plex API for specified media.
    * @param mediaType: str: "TV Shows"
    * @param mediaParentTitle: str: "Seinfeld"
    * @param mediaTitle: str: "The Soup Nazi"
    * @return null
    *
    '''
    def play_media(self, mediaType, mediaParentTitle, mediaTitle, offset, customSectionName, durationAmount, mediaID):
         # Check for necessary client override, if we have a folder of "channels_<NAME>"
        cwd = os.getcwd()
        if "channels_" in cwd:
            head,sep,tail = cwd.partition('channels_')
            head,sep,tail = tail.partition('/')
            self.PLEX_CLIENTS = [head]
            print("NOTICE: CLIENT OVERRIDE: %s" % self.PLEX_CLIENTS)
        try:
            if customSectionName == "Playlists":
                try:
                    print("NOTICE: Fetching PLAYLIST ITEM from MEDIA ID")
                    item = self.PLEX.fetchItem(mediaID)
                    for client in self.PLEX_CLIENTS:
                        clientItem = self.PLEX.client(client)
                        clientItem.playMedia(item, offset=offset)
                except:
                    print("ERROR: MEDIA ID FETCH FAILED - Falling Back")
                    mediaItems = self.PLEX.playlist(mediaParentTitle).items()
                    print("NOTICE: Checking Key for a Match: ")
                    for item in mediaItems:
                        if item.key == mediaID:
                            print("NOTICE: MATCH ID FOUND IN %s" % item)
                            for client in self.PLEX_CLIENTS:
                                clientItem = self.PLEX.client(client)
                                clientItem.playMedia(item, offset=offset)
                            break
            elif mediaType == "TV Shows" and customSectionName != "Playlists":
#                print "Here, Trying to play custom type: ", customSectionName
                try:
                    print("NOTICE: Fetching TV Show from MEDIA ID")
                    item = self.PLEX.fetchItem(mediaID)
                    for client in self.PLEX_CLIENTS:
                        clientItem = self.PLEX.client(client)
                        clientItem.playMedia(item, offset=offset)
                except:
                    print("ERROR: MEDIA ID FETCH FAILED - Falling Back")
                    mediaItems = self.PLEX.library.section(customSectionName).get(mediaParentTitle).episodes()
                    for item in mediaItems:
#                        print item.duration
                        if item.title == mediaTitle and item.duration == durationAmount:
                            print("NOTICE: MATCH FOUND in %s" % item)
                            for client in self.PLEX_CLIENTS:
                                clientItem = self.PLEX.client(client)
                                clientItem.playMedia(item, offset=offset)
                            break
                        elif item.key == mediaID:
                            print("NOTICE: MATCHID FOUND IN %s" % item)
                            for client in self.PLEX_CLIENTS:
                                clientItem = self.PLEX.client(client)
                                clientItem.playMedia(item, offset=offset)
                            break
            elif mediaType == "Movies":
                idNum = mediaID.lstrip('/library/metadata/')
                print("INFO: Plex ID Number: "+idNum)
                try:
                    print("NOTICE: Fetching MOVIE from MEDIA ID")
                    movie = self.PLEX.fetchItem(mediaID)
#                    movies = self.PLEX.library.section(customSectionName).get(mediaTitle)
                except:
                    print("ERROR: MEDIA ID FETCH FAILED - Falling Back")
                    movies = self.PLEX.library.section(customSectionName).search(title=mediaTitle) #movie selection
                    print("NOTICE: Checking ID for a Match: ")
                    for item in movies:
                        if item.key == mediaID:
                            print("NOTICE: ID MATCH FOUND IN %s" % item.title.upper())
                            movie = item
                            break
                for client in self.PLEX_CLIENTS:
                        clientItem = self.PLEX.client(client)
                        print("INFO: Playing "+movie.title.upper())
                        clientItem.playMedia(movie, offset=offset)
            elif mediaType == "Commercials":
                # This one is a bit more complicated, since we have the dirty gap fix possible
                # Basically, we are going to just assume it isn't a dirty gap fix, and if it is,
                # We will just play the first value
                COMMERCIAL_PADDING = config.commercialPadding
                try:
                    print("NOTICE: Fetching COMMERCIAL from MEDIA ID")
                    movie = self.PLEX.fetchItem(mediaID)
#                    movies = self.PLEX.library.section(customSectionName).get(mediaTitle)
                except:
                    print("ERROR: MEDIA ID FETCH FAILED - Falling Back")
                    movies = self.PLEX.library.section(customSectionName).search(title=mediaTitle)
                    print("NOTICE: Checking for a Match: ")
                    for item in movies:
                        if item.key == mediaID:
                            print("NOTICE: ID MATCH FOUND in %s" % item)
                            movie = item
                            break
                        elif (item.duration+1000*COMMERCIAL_PADDING) == durationAmount or item.duration == durationAmount:
                            print("NOTICE: DURATION MATCH FOUND in %s" % item)
                            movie = item
                            break
                try:
                    movie
                except:
                    print("ERROR: Commercial is NOT FOUND, my guess is this is the dirty gap.  Picking first one")
                    movies = self.PLEX.library.section(customSectionName).search(title=mediaTitle)
                    movie = movies[0]
                    
                for client in self.PLEX_CLIENTS:
                        clientItem = self.PLEX.client(client)
                        clientItem.playMedia(movie, offset=offset)
            else:
                print("NOTICE: Not sure how to play {}".format(customSectionName))
            print("NOTICE: Done.")
        except Exception as e:
            print(e.__doc__)
            print(e.message)
            print("ERROR: There was an error trying to play the media.")
            pass
        
    def stop_media(self):

        try:
            self.my_logger.debug('Trying to stop media.')
            for client in self.PLEX_CLIENTS:
                clientItem = self.PLEX.client(client)
                clientItem.stop(mtype='video')
                self.my_logger.debug('Done.')
        except Exception as e:
            self.my_logger.debug('stop_media - except.', e)
            pass
    '''
    *
    * If tv_controller() does not find a "startTime" for scheduled media, search for an "endTime" match for now time.
    * ...This is useful for clearing the generated html schedule when media ends and there is a gap before the next media.
    * @param null
    * @return null
    *
    '''
    def check_for_end_time(self, datalist):

        currentTime = datetime.now()
        """c.execute("SELECT * FROM daily_schedule")
        datalist = list(c.fetchall())
        """
        for row in datalist:
            try:
                endTime = datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                endTime = datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S')
            if currentTime.hour == endTime.hour:
                if currentTime.minute == endTime.minute:
                    if currentTime.second == endTime.second:
                        if self.DEBUG:
                            print("INFO: Ok end time found")
                        self.write_schedule_to_file(self.get_html_from_daily_schedule(None, None, datalist))
                        self.write_xml_to_file(self.get_xml_from_daily_schedule(None, None, datalist))
                        self.write_refresh_bool_to_file()
                        break

    def play(self, row, datalist, offset=0):

        print(str("NOTICE: Starting Media: '{}'".format(row[3])).encode('UTF-8'))
        print(str("NOTICE: Media Offset: '{}' seconds.".format(int(offset / 1000))).encode('UTF-8'))
        if self.DEBUG:
            print(str(row).encode('UTF-8'))
        try:
            timeB = datetime.strptime(row[8], '%I:%M:%S %p')
        except:
            timeB = datetime.strptime(row[8], '%H:%M:%S')

        print("INFO: Here, row[13]", row[13])

        self.play_media(row[11], row[6], row[3], offset, row[13], row[7], row[12])
        self.write_schedule_to_file(
            self.get_html_from_daily_schedule(
                timeB,
                self.get_show_photo(
                    row[13], 
                    row[6] if row[11] == "TV Shows" else row[3], row[7]
                ),
                datalist,
                row[6] + " - " + row[3] if row[11] == "TV Shows" else row[3]
            )
        )
        self.write_refresh_bool_to_file()
        """Generate / write XML to file
        """
        self.write_xml_to_file(
            self.get_xml_from_daily_schedule(
                timeB,
                self.get_show_photo(
                    row[13], 
                    row[6] if row[11] == "TV Shows" else row[3], row[7]
                ),
                datalist
            )
        )
        try:
            self.my_logger.debug('INFO: Trying to play: ' + row[3])
        except:
            pass

    '''
    *
    * Check DB / current time. If that matches a scheduled shows startTime then trigger play via Plex API
    * @param null
    * @return null
    *
    '''
    def tv_controller(self, datalist):

        datalistLengthMonitor = 0;
        currentTime = datetime.now()
        """c.execute("SELECT * FROM daily_schedule ORDER BY datetime(startTimeUnix) ASC")
        datalist = list(c.fetchall())"""
        try:
            self.my_logger.debug('TV Controller')
        except:
            pass
        for row in datalist:
            try:
                timeB = datetime.strptime(row[8], '%I:%M:%S %p')
            except:
                timeB = datetime.strptime(row[8], '%H:%M:%S')
            if currentTime.hour == timeB.hour:
                if currentTime.minute == timeB.minute:
                    if currentTime.second == timeB.second:
                        print("NOTICE: Starting Media: " + row[3])
                        print(row)
                        self.play_media(row[11], row[6], row[3], row[13], row[7], row[12])
                        self.write_schedule_to_file(
                            self.get_html_from_daily_schedule(
                                timeB,
                                self.get_show_photo(
                                    row[13], 
                                    row[6] if row[11] == "TV Shows" else row[3], row[7]
                                ),
                                datalist,
                                row[6] + " - " + row[3] if row[11] == "TV Shows" else row[3]
                            )
                        )
                        self.write_refresh_bool_to_file()
                        """Generate / write XML to file
                        """
                        self.write_xml_to_file(
                            self.get_xml_from_daily_schedule(
                                timeB,
                                self.get_show_photo(
                                    row[13], 
                                    row[6] if row[11] == "TV Shows" else row[3], row[7]
                                ),
                                datalist
                            )
                        )
                        try:
                            self.my_logger.debug('Trying to play: ' + row[3])
                        except:
                            pass
                        break
            datalistLengthMonitor += 1
            if datalistLengthMonitor >= len(datalist):
                self.check_for_end_time(datalist)

    def manually_get_now_playing_bg_image(self, currentTime, datalist):
        now = datetime.now()
        now = now.replace(year=1900, month=1, day=1)
        midnight = now.replace(hour=23, minute=59, second=59)
        increase_var = 0

        for row in datalist:
            #print row[8]
            #print row[9]
            if str(row[11]) == "Commercials" and self.DEBUG == False:
                continue
            try:
                timeBStart = datetime.strptime(row[8], '%I:%M:%S %p')
            except:
                timeBStart = datetime.strptime(row[8], '%H:%M:%S')
            timeBStart = timeBStart.replace(year=1900, month=1, day=1)
            try:
                timeBEnd = datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S.%f')
                timeBEnd = timeBEnd.replace(day=1)
            except:
                timeBEnd = datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S')
                timeBEnd = timeBEnd.replace(day=1)
            if ((currentTime - timeBStart).total_seconds() >= 0 and \
                 (timeBEnd - currentTime).total_seconds() >= 0) or \
                 ((timeBStart - timeBEnd).total_seconds() >= 0 and \
                 (((currentTime-midnight.replace(hour=0,minute=0,second=0)).total_seconds() >= 0 and \
                  (timeBEnd-currentTime).total_seconds() >= 0) or
                 ((currentTime-timeBStart).total_seconds() >= 0 and \
                  (midnight-currentTime).total_seconds() >= 0))): 

                print("INFO: Made the conditional & found item: {}".format(row[6]))

                return self.get_show_photo(
                    row[13], 
                    row[6] if row[11] == "TV Shows" else row[3], row[7]
                )
            
            else:

                pass

            increase_var += 1

        if len(datalist) >= increase_var:
            print("INFO: In 'manually_get_now_playing_bg_image()'. " 
                  "Reached the end of the schedule. No bgImages found.")
            return None

    def manually_get_now_playing_title(self, currentTime, datalist):
        now = datetime.now()
        now = now.replace(year=1900, month=1, day=1)
        midnight = now.replace(hour=23, minute=59, second=59)
        increase_var = 0

        for row in datalist:
            """if str(row[11]) == "Commercials" and self.DEBUG == False:
                continue"""
            try:
                timeBStart = datetime.strptime(row[8], '%I:%M:%S %p')
            except:
                timeBStart = datetime.strptime(row[8], '%H:%M:%S')
            timeBStart = timeBStart.replace(year=1900, month=1, day=1)
            try:
                timeBEnd = datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S.%f')
                timeBEnd = timeBEnd.replace(day=1)
            except:
                timeBEnd = datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S')
                timeBEnd = timeBEnd.replace(day=1)
            if ((currentTime - timeBStart).total_seconds() >= 0 and \
                 (timeBEnd - currentTime).total_seconds() >= 0) or \
                 ((timeBStart - timeBEnd).total_seconds() >= 0 and \
                 (((currentTime-midnight.replace(hour=0,minute=0,second=0)).total_seconds() >= 0 and \
                  (timeBEnd-currentTime).total_seconds() >= 0) or
                 ((currentTime-timeBStart).total_seconds() >= 0 and \
                  (midnight-currentTime).total_seconds() >= 0))):          

                print("NOTICE: Made the conditional & found item: {}".format(row[6]))

                return row[6] + " - " + row[3] if row[11] == "TV Shows" else row[3]

            else:

                pass

            increase_var += 1

        if len(datalist) >= increase_var:
            print("NOTICE: In 'manually_get_now_playing_title()'. " 
                  "Reached the end of the schedule. No bgImages found.")
            return ''

    def make_xml_schedule(self, datalist):

        print("NOTICE: ", "Writing XML / HTML to file.")
        now = datetime.now()
        now = now.replace(year=1900, month=1, day=1)

        bgImage = self.manually_get_now_playing_bg_image(now, datalist)

        itemTitle = self.manually_get_now_playing_title(now, datalist)

        print("NOTICE: The path to the bgImage: {}".format(bgImage))

        self.write_refresh_bool_to_file()
        self.write_schedule_to_file(self.get_html_from_daily_schedule(now, bgImage, datalist, itemTitle))
        self.write_xml_to_file(self.get_xml_from_daily_schedule(None, None, datalist))
