#!/usr/bin/env python

import sqlite3
import datetime
import time
import random

class PseudoChannelDatabase():

    def __init__(self, db):

        self.db = db
        self.conn = sqlite3.connect(self.db, check_same_thread=False)
        self.cursor = self.conn.cursor()

    """Database functions.
        Utilities, etc.
    """
    def create_tables(self):

        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'movies(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'unix INTEGER, mediaID INTEGER, title TEXT, duration INTEGER, '
                  'lastPlayedDate TEXT, plexMediaID TEXT, customSectionName Text, rating TEXT, summary TEXT, releaseYear TEXT, genres TEXT, actors TEXT, collections TEXT, studio TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'videos(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'unix INTEGER, mediaID INTEGER, title TEXT, duration INTEGER, plexMediaID TEXT, customSectionName Text)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'music(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'unix INTEGER, mediaID INTEGER, title TEXT, duration INTEGER, plexMediaID TEXT, customSectionName Text)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'shows(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'unix INTEGER, mediaID INTEGER, title TEXT, duration INTEGER, '
                  'lastEpisodeTitle TEXT, premierDate TEXT, plexMediaID TEXT, customSectionName Text, rating TEXT, genres TEXT, actors TEXT, similar TEXT, studio TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'episodes(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                  'unix INTEGER, mediaID INTEGER, title TEXT, duration INTEGER, '
                  'episodeNumber INTEGER, seasonNumber INTEGER, showTitle TEXT, plexMediaID TEXT, customSectionName Text, rating TEXT, airDate TEXT, summary TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'commercials(id INTEGER PRIMARY KEY AUTOINCREMENT, unix INTEGER, '
                  'mediaID INTEGER, title TEXT, duration INTEGER, plexMediaID TEXT, customSectionName Text)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'schedule(id INTEGER PRIMARY KEY AUTOINCREMENT, unix INTEGER, '
                  'mediaID INTEGER, title TEXT, duration INTEGER, startTime TEXT, '
                  'endTime TEXT, dayOfWeek TEXT, startTimeUnix INTEGER, section TEXT, '
                  'strictTime TEXT, timeShift TEXT, overlapMax TEXT, xtra TEXT, rerun INTEGER, year INTEGER, genres TEXT, actors TEXT, collections TEXT, rating TEXT, studio TEXT, seasonEpisode TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'daily_schedule(id INTEGER PRIMARY KEY AUTOINCREMENT, unix INTEGER, '
                  'mediaID INTEGER, title TEXT, episodeNumber INTEGER, seasonNumber INTEGER, '
                  'showTitle TEXT, duration INTEGER, startTime TEXT, endTime TEXT, '
                  'dayOfWeek TEXT, sectionType TEXT, plexMediaID TEXT, customSectionName TEXT, notes TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'app_settings(id INTEGER PRIMARY KEY AUTOINCREMENT, version TEXT)')
        #index
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_episode_plexMediaID ON episodes (plexMediaID);')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_movie_plexMediaID ON movies (plexMediaID);')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_shows_plexMediaID ON shows (plexMediaID);')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_video_plexMediaID ON videos (plexMediaID);')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_music_plexMediaID ON music (plexMediaID);')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_commercial_plexMediaID ON commercials (plexMediaID);')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_settings_version ON app_settings (version);')
        """Setting Basic Settings
        """
        try:
            self.cursor.execute("INSERT OR REPLACE INTO app_settings "
                      "(version) VALUES (?)", 
                      ("0.1",))
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def drop_db(self):

        pass

    def drop_schedule(self):

        pass

    def drop_daily_schedule_table(self):

        sql = "DROP TABLE IF EXISTS daily_schedule"
        self.cursor.execute(sql)
        self.conn.commit()

    def create_daily_schedule_table(self):

        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                  'daily_schedule(id INTEGER PRIMARY KEY AUTOINCREMENT, unix INTEGER, '
                  'mediaID INTEGER, title TEXT, episodeNumber INTEGER, seasonNumber INTEGER, '
                  'showTitle TEXT, duration INTEGER, startTime TEXT, endTime TEXT, '
                  'dayOfWeek TEXT, sectionType TEXT, plexMediaID TEXT, customSectionName TEXT, notes TEXT)')
        self.conn.commit()

    def remove_all_scheduled_items(self):

        sql = "DELETE FROM schedule WHERE id > -1"
        self.cursor.execute(sql)
        self.conn.commit()

    def remove_all_daily_scheduled_items(self):

        sql = "DELETE FROM daily_schedule"
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def clear_shows_table(self):

        sql = "DELETE FROM shows"
        self.cursor.execute(sql)
        self.conn.commit()

    """Database functions.
        Setters, etc.
    """
    def add_movies_to_db(
        self, 
        mediaID, 
        title, 
        duration, 
        plexMediaID, 
        customSectionName,
        rating,
        summary,
        releaseYear,
        genres,
        actors,
        collections,
        studio):

        unix = int(time.time())
        try:
            self.cursor.execute("REPLACE INTO movies "
                      "(unix, mediaID, title, duration, plexMediaID, customSectionName, rating, summary, releaseYear, genres, actors, collections, studio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (unix, mediaID, title, duration, plexMediaID, customSectionName, rating, summary, releaseYear, genres, actors, collections, studio))
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def add_videos_to_db(
        self, 
        mediaID, 
        title, 
        duration, 
        plexMediaID, 
        customSectionName):

        unix = int(time.time())
        try:
            self.cursor.execute("REPLACE INTO videos "
                      "(unix, mediaID, title, duration, plexMediaID, customSectionName) VALUES (?, ?, ?, ?, ?, ?)", 
                      (unix, mediaID, title, duration, plexMediaID, customSectionName))

            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def add_shows_to_db(
        self, 
        mediaID, 
        title, 
        duration, 
        lastEpisodeTitle, 
        premierDate, 
        plexMediaID, 
        customSectionName,
        rating,
        genres,
        actors,
        similar,
        studio):

        unix = int(time.time())
        try:
            self.cursor.execute("INSERT OR IGNORE INTO shows "
                      "(unix, mediaID, title, duration, lastEpisodeTitle, premierDate, plexMediaID, customSectionName, rating, genres, actors, similar, studio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (unix, mediaID, title, duration, lastEpisodeTitle, premierDate, plexMediaID, customSectionName, rating, genres, actors, similar, studio))
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def add_playlist_entries_to_db(
        self, 
        mediaID, 
        title, 
        duration, 
        episodeNumber, 
        seasonNumber, 
        showTitle, 
        plexMediaID, 
        customSectionName,
        rating,
        airDate,
        summary):

        unix = int(time.time())
        try:
            self.cursor.execute("INSERT INTO episodes "
                "(unix, mediaID, title, duration, episodeNumber, seasonNumber, showTitle, plexMediaID, customSectionName, rating, airDate, summary) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (unix, mediaID, title, duration, episodeNumber, seasonNumber, showTitle, plexMediaID, customSectionName, rating, airDate, summary))
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def add_episodes_to_db(
        self, 
        mediaID, 
        title, 
        duration, 
        episodeNumber, 
        seasonNumber, 
        showTitle, 
        plexMediaID, 
        customSectionName,
        rating,
        airDate,
        summary):

        unix = int(time.time())
        try:
            self.cursor.execute("REPLACE INTO episodes "
                "(unix, mediaID, title, duration, episodeNumber, seasonNumber, showTitle, plexMediaID, customSectionName, rating, airDate, summary) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (unix, mediaID, title, duration, episodeNumber, seasonNumber, showTitle, plexMediaID, customSectionName, rating, airDate, summary)) 
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def add_commercials_to_db(
        self, 
        mediaID, 
        title, 
        duration, 
        plexMediaID, 
        customSectionName):

        unix = int(time.time())
        try:
            self.cursor.execute("REPLACE INTO commercials "
                      "(unix, mediaID, title, duration, plexMediaID, customSectionName) VALUES (?, ?, ?, ?, ?, ?)", 
                      (unix, mediaID, title, duration, plexMediaID, customSectionName))
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            print("ERROR: "+str(plexMediaID))
            print(e)
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def add_schedule_to_db(self, 
                           mediaID, 
                           title, 
                           duration, 
                           startTime, 
                           endTime, 
                           dayOfWeek, 
                           startTimeUnix, 
                           section, 
                           strictTime, 
                           timeShift, 
                           overlapMax,
                           xtra,
                           rerun,
                           year,
                           genres,
                           actors,
                           collections,
                           rating,
                           studio,
                           seasonEpisode):
        unix = int(time.time())
        try:
            self.cursor.execute("REPLACE INTO  schedule "
                "(unix, mediaID, title, duration, startTime, endTime, dayOfWeek, startTimeUnix, section, strictTime, timeShift, overlapMax, xtra, rerun, year, genres, actors, collections, rating, studio, seasonEpisode) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (unix, mediaID, title, duration, startTime, endTime, dayOfWeek, startTimeUnix, section, strictTime, timeShift, overlapMax, xtra, rerun, year, genres, actors, collections, rating, studio, seasonEpisode))
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def add_daily_schedule_to_db(
            self,
            mediaID, 
            title, 
            episodeNumber, 
            seasonNumber, 
            showTitle, 
            duration, 
            startTime, 
            endTime, 
            dayOfWeek, 
            sectionType,
            plexMediaID,
            customSectionName,
            notes
            ):

        unix = int(time.time())
        try:
            self.cursor.execute("INSERT OR REPLACE INTO daily_schedule "
                      "(unix, mediaID, title, episodeNumber, seasonNumber, "
                      "showTitle, duration, startTime, endTime, dayOfWeek, sectionType, plexMediaID, customSectionName, notes) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (
                        unix, 
                        mediaID, 
                        title, 
                        episodeNumber, 
                        seasonNumber, 
                        showTitle, 
                        duration, 
                        startTime, 
                        endTime, 
                        dayOfWeek, 
                        sectionType,
                        plexMediaID,
                        customSectionName,
                        notes
                        ))
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def add_media_to_daily_schedule(self, media):
        try:
            mediaPrint = media.start_time + ": " + media.show_series_title + " - " + media.title + " | " + str(media.duration/1000) + " | " + media.custom_section_name
        except:
            mediaPrint = media.start_time + ": " + media.title + " | " + str(media.duration/1000) + " | " + media.custom_section_name
        try:
            print(mediaPrint)
            #print(str("{}: {} - {}".format(media.start_time, media.title, media.custom_section_name)).encode('UTF-8'))
        except:
            print("ERROR: Not outputting media info due to ascii code issues.")
        if media.media_id != 3:
            notes = media.notes
        else:
            notes = ""
        if media.__class__.__name__ == "Episode":
            seriesTitle = media.show_series_title
        else:
            seriesTitle = ''
        self.add_daily_schedule_to_db(
                media.media_id,
                media.title,
                media.episode_number if media.__class__.__name__ == "Episode" else 0,
                media.season_number if media.__class__.__name__ == "Episode" else 0,
                seriesTitle,
                media.duration,
                media.start_time,
                media.end_time,
                media.day_of_week,
                media.section_type,
                media.plex_media_id,
                media.custom_section_name,
                notes
            )

    def import_shows_table_by_row(
            self, 
            mediaID, 
            title, 
            duration, 
            lastEpisodeTitle, 
            fullImageURL, 
            plexMediaID):

        unix = int(time.time())
        try:
            self.cursor.execute('UPDATE shows SET lastEpisodeTitle = ? WHERE title = ?', (lastEpisodeTitle, title))
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    def import_daily_schedule_table_by_row(
            self, 
            mediaID, 
            title, 
            episodeNumber, 
            seasonNumber, 
            showTitle, 
            duration,
            startTime,
            endTime,
            dayOfWeek,
            sectionType,
            plexMediaID,
            customSectionName):

        unix = int(time.time())
        try:
            self.cursor.execute("REPLACE INTO daily_schedule "
                      '''(unix, 
                          mediaID, 
                          title, 
                          episodeNumber, 
                          seasonNumber, 
                          showTitle, 
                          duration,
                          startTime,
                          endTime,
                          dayOfWeek,
                          sectionType,
                          plexMediaID,
                          customSectionName
                         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                      (unix, 
                       mediaID, 
                       title, 
                       episodeNumber, 
                       seasonNumber, 
                       showTitle, 
                       duration,
                       startTime,
                       endTime,
                       dayOfWeek,
                       sectionType,
                       plexMediaID,
                       customSectionName))
            self.conn.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.conn.rollback()
            raise e

    """Database functions.
        Updaters, etc.
    """

    def update_shows_table_with_last_episode(self, showTitle, lastEpisodeTitle):
        sql1 = "UPDATE shows SET lastEpisodeTitle = ? WHERE title LIKE ? COLLATE NOCASE"
        self.cursor.execute(sql1, (lastEpisodeTitle, showTitle, ))
        self.conn.commit()

    def update_shows_table_with_last_episode_alt(self, showTitle, lastEpisodeTitle):
        sql1 = "UPDATE shows SET lastEpisodeTitle = ? WHERE title LIKE ? COLLATE NOCASE"
        self.cursor.execute(sql1, (lastEpisodeTitle, '%'+showTitle+'%', ))
        self.conn.commit()

    def update_shows_table_with_last_episode_by_id(self, showKey, lastEpisodeKey):
        sql1 = "UPDATE shows SET lastEpisodeTitle = ? WHERE plexMediaID LIKE ? COLLATE NOCASE"
        self.cursor.execute(sql1, (lastEpisodeKey, showKey, ))
        self.conn.commit()

    def update_movies_table_with_last_played_date(self, movieTitle):

        now = datetime.datetime.now()
        lastPlayedDate = now.strftime('%Y-%m-%d')
        sql = "UPDATE movies SET lastPlayedDate = ? WHERE title LIKE ? COLLATE NOCASE"
        self.cursor.execute(sql, (lastPlayedDate, movieTitle, ))
        self.conn.commit()

    """Database functions.
        Getters, etc.
    """

    def get_shows_titles(self):
        self.cursor.execute("SELECT title FROM shows")
        datalist = self.cursor.fetchall()
        return datalist

    def get_shows_table(self):

        sql = "SELECT * FROM shows"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_episode_from_season_episode(self, title, seasonNumber, episodeNumber):
        sql = "SELECT * FROM episodes WHERE (showTitle LIKE ?) AND (seasonNumber LIKE ?) AND (episodeNumber LIKE ?) LIMIT 1"
        self.cursor.execute(sql, (title, seasonNumber, episodeNumber, ))
        return self.cursor.fetchone()

    def get_media(self, title, mediaType):

        print("INFO: title:", title)
        if(title is not None):
            media = mediaType
            sql = "SELECT * FROM "+media+" WHERE (title LIKE ?) COLLATE NOCASE"
            self.cursor.execute(sql, ("%"+title+"%", ))
            media_item = self.cursor.fetchone()
            return media_item
        else:
            pass

    def get_media_by_id(self, plex_media_id, mediaType):
        print("INFO: plex_media_id:", plex_media_id)
        if(plex_media_id is not None):
            media = mediaType
            sql = "SELECT * FROM "+media+" WHERE (plexMediaID LIKE ?) COLLATE NOCASE"
            self.cursor.execute(sql, (plex_media_id, ))
            media_item = self.cursor.fetchone()
            return media_item
        else:
            pass

    def get_schedule(self):

        self.cursor.execute("SELECT * FROM schedule ORDER BY datetime(startTime) ASC")
        datalist = list(self.cursor.fetchall())
        return datalist

    def get_schedule_alternate(self,time):
        t = str("%02d"%int(time[0]))
        sql = ("SELECT * FROM schedule WHERE substr(startTime,1,2) >= ? ORDER BY datetime(startTime) ASC")
        self.cursor.execute(sql, [t])
        datalist = list(self.cursor.fetchall())
        sql = ("SELECT * FROM schedule WHERE substr(startTime,1,2) < ? ORDER BY datetime(startTime) ASC")
        self.cursor.execute(sql, [t])
        secondHalf = list(self.cursor.fetchall())
        datalist.extend(secondHalf)
        return datalist

    def get_daily_schedule(self):

        print("NOTICE Getting Daily Schedule from DB.")
        self.cursor.execute("SELECT * FROM daily_schedule ORDER BY datetime(startTime) ASC")
        datalist = list(self.cursor.fetchall())
        print("NOTICE: Done.")
        return datalist

    def get_movie(self, title):

        media = "movies"
        return self.get_media(title, media)

    def get_movie_by_id(self, plex_media_id):

        media = "movies"
        return self.get_media_by_id(plex_media_id, media)

    def get_shows(self, title):

        media = "shows"
        return self.get_media(title, media)

    def get_music(self, title):

        media = "music"
        return self.get_media(title, media)

    def get_video(self, title):

        media = "videos"
        return self.get_media(title, media)

    def get_episodes(self, title):

        media = "episodes"
        return self.get_media(title, media)

    def get_commercials(self):

        self.cursor.execute("SELECT * FROM commercials ORDER BY duration ASC")
        datalist = list(self.cursor.fetchall())
        return datalist
        
    def get_random_commercial_duration(self,min,max):
        sql = "SELECT * FROM commercials WHERE (duration BETWEEN ? and ?) ORDER BY RANDOM() LIMIT 1"
        self.cursor.execute(sql, (min, max, ))
        return self.cursor.fetchone()        

    def get_movies(self):

        self.cursor.execute("SELECT * FROM movies ORDER BY date(lastPlayedDate) ASC")
        datalist = list(self.cursor.fetchall())
        return datalist

    def get_movies_xtra(self,min,max,xtra=None):
        xtraArgs = ['rating','releaseYear','decade','genre','actor','collection','studio']
        xtraDict = {}
        xtraDict['rating']=None
        xtraDict['release']=None
        xtraDict['decade']=None
        xtraDict['genre']=None
        xtraDict['actor']=None
        xtraDict['collection']=None
        xtraDict['studio']=None
        print("INFO: xtra = " + str(xtra))
        if xtra != None:
            for x in xtra:
                x = x.replace("'",r"''")
                x = x.replace('"',r'""')
                x = x.split(':')
                if x[0] in xtraArgs and x[1] != None:
                    xtraDict[x[0]] = []
                    if ',' in x[1]:
                        data = x[1].split(',')
                        for eachArg in data:
                            xtraDict[x[0]].append(eachArg)
                    else:
                        xtraDict[x[0]].append(x[1])
        cursor_execute = "SELECT * FROM movies WHERE (duration BETWEEN "+str(min)+" and "+str(max)+")"
        if xtraDict['rating'] != None:
            cursor_execute = cursor_execute + "and rating LIKE \""+xtraDict['rating'][0]+"\""
        if xtraDict['release'] != None:
            cursor_execute = cursor_execute + " and releaseYear LIKE "+str(xtraDict['release'][0])+"\""
        elif xtraDict['decade'] != None:
            dec = str(xtraDict['decade'][0][0:3])
            cursor_execute = cursor_execute + "and releaseYear LIKE \""+dec+"%\""
        if xtraDict['genre'] != None:
             for g in xtraDict['genre']:
                if g != '':
                    cursor_execute = cursor_execute + " and genres LIKE \"%" + g + "%\""
        if xtraDict['actor'] != None:
            for a in xtraDict['actor']:
                if a != '':
                    cursor_execute = cursor_execute + " and (actors LIKE \"%"+a+"%\")"
        if xtraDict['collection'] != None:
            for a in xtraDict['collection']:
                if a != '':
                    cursor_execute = cursor_execute + " and (collections LIKE \"%"+a+"%\")"
        if xtraDict['studio'] != None:
            cursor_execute = cursor_execute + "and studio LIKE \"%"+xtraDict['studio'][0]+"%\""
        cursor_execute = cursor_execute + " ORDER BY date(lastPlayedDate) ASC"
        print("ACTION: " + cursor_execute)
        self.cursor.execute(cursor_execute)
        datalist = self.cursor.fetchall()
        return datalist

    def get_movies_data(self,section,min,max,year,genres,actors,collections,rating,studios):
        print("INFO: " + str(min) + ', ' + str(max) + ', ' + str(year) + ', ' + str(genres) + ', ' + str(actors) + ', ' + str(collections) + ', ' + str(rating) + ', ' + str(studios))
        genresList = []
        actorsList = []
        collectionsList = []
        studiosList = []
        movieRatingsUS = ['G','PG','PG-13','R','NC-17','NR']
        movieRatingsAUS = ['AUS-G','AUS-PG','AUS-M','MA15+','R18+','X18+']
        movieRatingsCA = ['G','PG','14A','18A','R','A']
        movieRatingsUK = ['U','12A','15','18','R18']
        tvRatingsUS = ['TV-Y','TV-Y7','TV-G','TV-PG','TV-14','TV-MA','NR']
        tvRatingsAUS = ['C','P','G','PG','M','MA15+','AV15+','R18+','E']
        tvRatingsCA = ['C','C8','G','PG','14+','18+','Exempt']
        tvRatingsUK = ['U','12A','15','18','R18']
        print("INFO: "+section)
        if rating != None:
            ratingsAllowed = []
            rating=rating.split(',')
            if rating[0] == 'US' and section == 'Movies':
                ratingsList = movieRatingsUS
            elif rating[0] == 'US' and section == 'TV Shows':
                ratingsList = tvRatingsUS
            elif rating[0] == 'AUS' and section == 'Movies':
                ratingsList = movieRatingsAUS
            elif rating[0] == 'AUS' and section == 'TV Shows':
                ratingsList = tvRatingsAUS
            elif rating[0] == 'CA' and section == 'Movies':
                ratingsList = movieRatingsCA
            elif rating[0] == 'CA' and section == 'TV Shows':
                ratingsList = tvRatingsCA
            elif rating[0] == 'UK' and section == 'Movies':
                ratingsList = movieRatingsUK
            elif rating[0] == 'UK' and section == 'TV Shows':
                ratingsList  = tvRatingsUK
            else:
                if section == 'Movies':
                    ratingsList = movieRatingsUS
                elif section == 'TV Shows':
                    ratingsList = tvRatingsUS
            if rating[2] == '=':
                print("INFO: Rating = " + rating[0] +', ' + rating[1])
                ratingsAllowed.append(rating[1])
            elif rating[2] == '<':
                ratingPos = ratingsList.index(rating[1])
                ratings = ''
                while ratingPos >= 0:
                    ratings = ratings + ', ' + ratingsList[ratingPos]
                    ratingsAllowed.append(ratingsList[ratingPos])
                    ratingPos = ratingPos - 1
            elif rating[2] == '>':
                ratingPos = ratingsList.index(rating[1])
                ratings = ''
                ratingsListLength = len(ratingsList)
                print("INFO: Rating = " + rating[0] +', ')
                while ratingPos < ratingsListLength:
                    ratings = ratings + ', ' + ratingsList[ratingPos]
                    ratingsAllowed.append(ratingsList[ratingPos])
                    ratingPos = ratingPos + 1
        if year != None:
            if year[3] == '*':
                print("INFO: Decade = " + str(year))
                decade=year
                release=None
            else:
                print("INFO: Year = " + str(year))
                release=year
                decade=None
        else:
            release=None
            decade=None
        if genres != None and ',' in genres:
            genres=genres.replace("'",r"''").replace('"',r'""').split(',')
            for genre in genres:
                print("INFO: Genre = " + genre)
                genresList.append(genre)
        elif genres != None:
            genres=genres.replace("'",r"''").replace('"',r'""')
            print("INFO: Genre = " + genres)
            genresList.append(genres)
        if actors != None:
            if type(actors) == list:
                for actor in actors:
                    print("INFO: Actor = " + actor)
                    actor=actor.replace("'",r"''").replace('"',r'""')
                    actorsList.append(actor)
            else:
                print("INFO: Actor = " + actors)
                actors=actors.replace("'",r"''").replace('"',r'""')
                actorsList.append(actors)
        if collections != None and ',' in collections:
            collections=collections.replace("'",r"''")
            collections=collections.replace('"',r'""')
            collections=collections.split(',')
            for collection in collections:
                print("INFO: Collection = " + collection)
                collectionsList.append(collection)
        elif collections != None:
            collections=collections.replace("'",r"''").replace('"',r'""')
            print("INFO: Collection = " + collections)
            collectionsList.append(collections)
        if studios != None and ',' in studios:
            studios=studios.replace("'",r"''").replace('"',r'""').split(',')
            for studio in studios:
                print("INFO: Studio = " + studio)
                studiosList.append(studio)
        elif studios != None:
            studios=studio.replace("'",r"''").replace('"',r'""')
            print("INFO: Studio = " + studios)
            studiosList.append(studios)
        cursor_execute = "SELECT * FROM movies WHERE (duration BETWEEN "+str(min)+" and "+str(max)+")"
        if rating != None:
            if len(ratingsAllowed) == 1:
                cursor_execute = cursor_execute + " and rating LIKE \""+rating[1]+"\""
            elif len(ratingsAllowed) > 0:
                c = 0
                for r in ratingsAllowed:
                    if c == 0:
                        cursor_execute = cursor_execute + " and (rating IN (\""+r+"\""
                    else:
                        cursor_execute = cursor_execute + ", \""+r+"\""
                    c = c + 1
                cursor_execute = cursor_execute + "))"
        if release != None:
            cursor_execute = cursor_execute + " and releaseYear LIKE "+str(release)+"%\""
        elif decade != None:
            dec = str(decade[0:3])
            cursor_execute = cursor_execute + " and releaseYear LIKE \""+dec+"%\""
        if genresList != None:
             for g in genresList:
                if g != '':
                    cursor_execute = cursor_execute + " and genres LIKE \"%" + g + "%\""
        if actorsList != None:
            for a in actorsList:
                if a != '':
                    cursor_execute = cursor_execute + " and (actors LIKE \"%"+a+"%\")"
        if collectionsList != None:
            for c in collectionsList:
                if c != '':
                    cursor_execute = cursor_execute + " and (collections LIKE \"%"+c+"%\")"
        if studiosList != None:
            for s in studiosList:
                if s != '':
                    cursor_execute = cursor_execute + "and studio LIKE \"%"+s+"%\""
        cursor_execute = cursor_execute + " ORDER BY date(lastPlayedDate) ASC"
        print("ACTION: " + cursor_execute)
        self.cursor.execute(cursor_execute)
        datalist = self.cursor.fetchall()
        return datalist

    def get_specific_episode(self, tvshow, season=None, episode=None):
        if season is None and episode is None:
            print("ERROR: Season and Episode Numbers Not Found")
            pass
        elif season is None:
            episode = str(episode)
            sql = ("SELECT * FROM episodes WHERE ( showTitle LIKE ? and episodeNumber LIKE ?) ORDER BY RANDOM()")
            self.cursor.execute(sql, (tvshow, "%"+episode+"&", ))
        elif episode is None:
            season = str(season)
            sql = ("SELECT * FROM episodes WHERE ( showTitle LIKE ? and seasonNumber LIKE ?) ORDER BY RANDOM()")
            self.cursor.execute(sql, (tvshow, "%"+season+"%", ))
        else:
            episode = str(episode)
            season = str(season)
            sql = ("SELECT * FROM episodes WHERE ( showTitle LIKE ? and seasonNumber LIKE ? and episodeNumber LIKE ?) ORDER BY RANDOM()")
            self.cursor.execute(sql, (tvshow, "%"+season+"%", "%"+episode+"%", ))
        media_item = self.cursor.fetchone()
        return media_item

    def get_first_episode(self, tvshow):

        sql = ("SELECT id, unix, mediaID, title, duration, MIN(episodeNumber), MIN(seasonNumber), "
                "showTitle, plexMediaID, customSectionName FROM episodes WHERE ( showTitle LIKE ?) COLLATE NOCASE")
        self.cursor.execute(sql, (tvshow, ))
        first_episode = self.cursor.fetchone()
        return first_episode

    def get_first_episode_by_id(self, tvshow):

        sql = ("SELECT id, unix, mediaID, title, duration, MIN(episodeNumber), MIN(seasonNumber), "
                "showTitle, plexMediaID, customSectionName FROM episodes WHERE ( mediaID LIKE ?) COLLATE NOCASE")
        self.cursor.execute(sql, (tvshow, ))
        first_episode = self.cursor.fetchone()
        return first_episode

    '''
    *
    * When incrementing episodes in a series I am advancing by "id" 
    *
    '''
    def get_episode_id(self, episodeTitle):
        sql = "SELECT id FROM episodes WHERE ( title LIKE ?) COLLATE NOCASE"
        self.cursor.execute(sql, (episodeTitle, ))
        episode_id = self.cursor.fetchone()
        return episode_id

    def get_episode_from_plexMediaID(self,plexMediaID):
        sql = "SELECT * FROM episodes WHERE (plexMediaID LIKE ?) COLLATE NOCASE"
        self.cursor.execute(sql, (plexMediaID, ))
        episode = self.cursor.fetchone()
        return episode

    ####mutto233 made this one#### UPDATED 5/2/2020
    def get_episode_id_alternate(self,plexMediaID,series):
        sql = "SELECT id FROM episodes WHERE (showTitle LIKE ? AND plexMediaID LIKE ?) COLLATE NOCASE"
        self.cursor.execute(sql, (series,plexMediaID, ))
        episode_id = self.cursor.fetchone()
        return episode_id
    ####mutto233 made this one####

    def get_episode_from_id(self,ID):
        print("NOTICE: Getting episode of by matching ID")
        sql = ("SELECT * FROM episodes WHERE ( id = "+str(ID)+") ORDER BY id LIMIT 1 COLLATE NOCASE")
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def get_episode_id_by_show_id(self,plexMediaID,series):
        sql = "SELECT id FROM episodes WHERE (mediaID LIKE ? AND plexMediaID LIKE ?) COLLATE NOCASE"
        self.cursor.execute(sql, (series,plexMediaID, ))
        episode_id = self.cursor.fetchone()
        return episode_id

    def get_random_episode(self):

        sql = "SELECT * FROM episodes WHERE id IN (SELECT id FROM episodes ORDER BY RANDOM() LIMIT 1)"
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def get_random_episode_duration(self,min,max):
        sql = "SELECT * FROM episodes WHERE (customSectionName NOT LIKE 'playlist' AND duration BETWEEN ? and ?) ORDER BY RANDOM() LIMIT 1"
        self.cursor.execute(sql, (min, max, ))
        return self.cursor.fetchone()

    ####mutto233 made this one####
    def get_random_episode_alternate(self,series):

        sql = "SELECT * FROM episodes WHERE (showTitle LIKE ? AND id IN (SELECT id FROM episodes ORDER BY RANDOM() LIMIT 1))"
        self.cursor.execute(sql, (series, ))
        return self.cursor.fetchone()
    ####mutto233 made this one####

    def get_random_movie(self):

        sql = "SELECT * FROM movies WHERE id IN (SELECT id FROM movies ORDER BY RANDOM() LIMIT 1)"
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def get_random_movie_duration(self,min,max):

        sql = "SELECT * FROM movies WHERE (duration BETWEEN ? and ?) ORDER BY RANDOM() LIMIT 1"
        self.cursor.execute(sql, (min, max, ))
        return self.cursor.fetchone()

    ###added 5/4/2020###
    def get_random_episode_of_show(self,series):
        print(series.upper())
        sql = "SELECT * FROM episodes WHERE (showTitle LIKE ?) ORDER BY RANDOM() LIMIT 1"
        self.cursor.execute(sql, (series, ))
        return self.cursor.fetchone()

    def get_random_episode_of_show_alt(self,series):
        sql = "SELECT * FROM episodes WHERE (showTitle LIKE '%"+series+"%') ORDER BY RANDOM() LIMIT 1"
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def get_random_episode_of_show_duration(self,series,min,max):
        sql = "SELECT * FROM episodes WHERE (showTitle LIKE '%"+series+"%' AND duration BETWEEN ? and ?) ORDER BY RANDOM() LIMIT 1"
        self.cursor.execute(sql (min, max, ))
        return self.cursor.fetchone()

    def get_random_show(self):
        sql = "SELECT * FROM shows WHERE (customSectionName NOT LIKE 'playlist' AND id IN (SELECT id FROM shows ORDER BY RANDOM() LIMIT 1))"
        self.cursor.execute(sql)
        return self.cursor.fetchone()
    ###
    def get_random_show_duration(self,min,max):
        sql = "SELECT * FROM shows WHERE (customSectionName NOT LIKE 'playlist' AND duration BETWEEN ? and ?) ORDER BY RANDOM() LIMIT 1"
        self.cursor.execute(sql, (min, max, ))
        return self.cursor.fetchone()

    def get_random_show_data(self,section,min,max,airDate,genres,actors,similar,rating,studios):
        print("INFO: " + str(min) + ', ' + str(max) + ', ' + str(airDate) + ', ' + str(genres) + ', ' + str(actors) + ', ' + str(similar) + ', ' + str(rating) + ', ' + str(studios))
        if airDate != None:
            if str(airDate)[3] == '*':
                print("INFO: Decade = " + str(airDate)[0:3])
                datestring=str(airDate)[0:3]
            else:
                print("INFO: Air Date = " + str(airDate))
                datestring=airDate
        else:
            datestring = None
        genresList = []
        actorsList = []
        similarList = []
        studiosList = []
        tvRatingsUS = ['TV-Y','TV-Y7','TV-G','TV-PG','TV-14','TV-MA','NR']
        tvRatingsAUS = ['C','P','G','PG','M','MA15+','AV15+','R18+','E']
        tvRatingsCA = ['C','C8','G','PG','14+','18+','Exempt']
        tvRatingsUK = ['U','12A','15','18','R18']
        print("INFO: "+section)
        if rating != None:
            ratingsAllowed = []
            rating=rating.split(',')
            if rating[0] == 'US':
                ratingsList = tvRatingsUS
            elif rating[0] == 'AUS':
                ratingsList = tvRatingsAUS
            elif rating[0] == 'CA':
                ratingsList = tvRatingsCA
            elif rating[0] == 'UK':
                ratingsList  = tvRatingsUK
            else:
                ratingsList = tvRatingsUS
            if rating[2] == '=':
                print("INFO: Rating = " + rating[0] +', ' + rating[1])
                ratingsAllowed.append(rating[1])
            elif rating[2] == '<':
                ratingPos = ratingsList.index(rating[1])
                ratings = ''
                while ratingPos >= 0:
                    ratings = ratings + ', ' + ratingsList[ratingPos]
                    ratingsAllowed.append(ratingsList[ratingPos])
                    ratingPos = ratingPos - 1
            elif rating[2] == '>':
                ratingPos = ratingsList.index(rating[1])
                ratings = ''
                ratingsListLength = len(ratingsList)
                print("INFO: Rating = " + rating[0] +', '+rating[1])
                while ratingPos < ratingsListLength:
                    ratings = ratings + ', ' + ratingsList[ratingPos]
                    ratingsAllowed.append(ratingsList[ratingPos])
                    ratingPos = ratingPos + 1
        if genres != None and ',' in genres:
            genres=genres.replace("'",r"''").replace('"',r'""').split(',')
            for genre in genres:
                print("INFO: Genre = " + genre)
                genresList.append(genre)
        elif genres != None:
            genres=genres.replace("'",r"''").replace('"',r'""')
            print("INFO: Genre = " + genres)
            genresList.append(genres)
        if actors != None:
            if type(actors) == list:
                for actor in actors:
                    print("INFO: Actor = " + actor)
                    actor=actor.replace("'",r"''").replace('"',r'""')
                    actorsList.append(actor)
            else:
                print("INFO: Actor = " + actors)
                actors=actors.replace("'",r"''").replace('"',r'""')
                actorsList.append(actors)
        if similar != None and ',' in similar:
            similar=similar.replace("'",r"''")
            similar=similar.replace('"',r'""')
            similar=similar.split(',')
            for s in similar:
                print("INFO: Similar = " + s)
                similarList.append(s)
        elif similar != None:
            similar=similar.replace("'",r"''").replace('"',r'""')
            print("INFO: Similar = " + similar)
            similarList.append(similar)
        if studios != None and ',' in studios:
            studios=studios.replace("'",r"''").replace('"',r'""').split(',')
            for studio in studios:
                print("INFO: Studio = " + studio)
                studiosList.append(studio)
        elif studios != None:
            studios=studio.replace("'",r"''").replace('"',r'""')
            print("INFO: Studio = " + studios)
            studiosList.append(studios)
        cursor_execute = "SELECT * FROM shows WHERE (customSectionName LIKE \"TV Shows\")"
        leading_and = True
        if rating != None:
            if len(ratingsAllowed) == 1:
                cursor_execute = cursor_execute + " and rating LIKE \""+rating[1]+"\""
                leading_and = True
            elif len(ratingsAllowed) > 0:
                c = 0
                for r in ratingsAllowed:
                    if c == 0:
                        cursor_execute = cursor_execute + " and (rating IN (\""+r+"\""
                    else:
                        cursor_execute = cursor_execute + ", \""+r+"\""
                    c = c + 1
                cursor_execute = cursor_execute + "))"
        if genresList != None:
            for g in genresList:
                if g != '':
                    cursor_execute = cursor_execute + " and genres LIKE \"%" + g + "%\""
                    leading_and = True
        if actorsList != None:
            for a in actorsList:
                if a != '':
                    cursor_execute = cursor_execute + " and (actors LIKE \"%"+a+"%\")"
                    leading_and = True
        if similarList != None:
            for sim in similarList:
                if sim != '':
                    cursor_execute = cursor_execute + " and (similar LIKE \"%"+sim+"%\")"
                    leading_and = True
        if studiosList != None:
            for s in studiosList:
                if s != '':
                    cursor_execute = cursor_execute + " and studio LIKE \"%"+s+"%\""
                    leading_and = True
        cursor_execute = cursor_execute + " ORDER BY mediaID ASC"
        print("ACTION: " + cursor_execute)
        self.cursor.execute(cursor_execute)
        showslist = self.cursor.fetchall()
        if datestring != None:
            episode_execute = "SELECT * FROM episodes WHERE (duration BETWEEN "+str(min)+" and "+str(max)+") and airDate LIKE \""+str(datestring)+"%\" ORDER BY mediaID ASC"
            print("INFO: " + episode_execute)
            self.cursor.execute(episode_execute)
            episodelist = self.cursor.fetchall()
            datalist = []
        else:
            episode_execute = "SELECT * FROM episodes WHERE (duration BETWEEN "+str(min)+" and "+str(max)+") ORDER BY mediaID ASC"
            print("INFO: " + episode_execute)
            self.cursor.execute(episode_execute)
            episodelist = self.cursor.fetchall()
            datalist = []
        for one_episode in episodelist:
            for one_show in showslist:
                if one_episode[2] == one_show[2] and one_show not in datalist:
                    datalist.append(one_show)
        print("INFO: " + str(len(showslist)) + " shows found.")
        if datalist != []:
            print("INFO: " + str(len(datalist)) + " matching shows found")
            the_show = random.choice(datalist)
        else:
            print("INFO: NO MATCHING SHOWS FOUND, TRYING AGAIN WITHOUT SOME METADATA")
            #get shows list with only length, rating and date filters
            cursor_execute = "SELECT * FROM shows WHERE (customSectionName LIKE \"TV Shows\")"
            if rating != None:
                if len(ratingsAllowed) == 1:
                    cursor_execute = cursor_execute + " and rating LIKE \""+rating[1]+"\""
                    leading_and = True
                elif len(ratingsAllowed) > 0:
                    c = 0
                    for r in ratingsAllowed:
                        if c == 0:
                            cursor_execute = cursor_execute + " and (rating IN (\""+r+"\""
                        else:
                            cursor_execute = cursor_execute + ", \""+r+"\""
                        c = c + 1
                    cursor_execute = cursor_execute + "))"
            cursor_execute = cursor_execute + " ORDER BY mediaID ASC"
            print("ACTION: " + cursor_execute)
            self.cursor.execute(cursor_execute)
            showslist = self.cursor.fetchall()
            episode_execute = "SELECT * FROM episodes WHERE (duration BETWEEN "+str(min)+" and "+str(max)+") ORDER BY mediaID ASC"
            print("INFO: " + episode_execute)
            self.cursor.execute(episode_execute)
            episodelist = self.cursor.fetchall()
            datalist = []
            for one_episode in episodelist:
                for one_show in showslist:
                    if one_episode[2] == one_show[2] and one_show not in datalist:
                        datalist.append(one_show)
            print("INFO: " + str(len(showslist)) + " shows found.")
            if datalist != []:
                print("INFO: " + str(len(datalist)) + " matching shows found")
                the_show = random.choice(datalist)
        #print(str(the_show))
        return the_show

    def get_random_episode_of_show_by_data(self, seriesID, min, max, date, season=None, episode=None):
        print("INFO: "+ str(seriesID) + ', ' + str(min) + ', ' + str(max) + ', ' + str(date) + ', Season: ' + str(season) + ', Episode: ' + str(episode))
        cursor_execute = "SELECT * FROM episodes WHERE mediaID LIKE \""+str(seriesID)+"\" AND duration BETWEEN \""+str(min)+"\" and \""+str(max)+"\""
        if season != None:
            cursor_execute = cursor_execute + " and seasonNumber LIKE \""+str(season)+"\""
        if episode != None:
            cursor_execute = cursor_execute + " and episodeNumber LIKE \""+str(episode)+"\""
        if date != None:
            if str(date)[3] == '*':
                date = str(date)[0:3]
            cursor_execute = cursor_execute + " and airDate LIKE \""+str(date)+"%\""
        cursor_execute = cursor_execute + " ORDER BY RANDOM() LIMIT 1"
        print("INFO: " + cursor_execute)
        self.cursor.execute(cursor_execute)
        return self.cursor.fetchone()

    def get_random_episode_of_show_by_data_alt(self, series, min, max, date, season=None, episode=None):
        print("INFO: "+ str(series) + ', ' + str(min) + ', ' + str(max) + ', ' + str(date) + ', Season: ' + str(season) + ', Episode: ' + str(episode))
        cursor_execute = "SELECT * FROM episodes WHERE showTitle LIKE \""+series+"\" AND duration BETWEEN \""+str(min)+"\" and \""+str(max)+"\""
        if season != None:
            cursor_execute = cursor_execute + " and seasonNumber LIKE \""+str(season)+"\""
        if episode != None:
            cursor_execute = cursor_execute + " and episodeNumber LIKE \""+str(episode)+"\""
        if date != None:
            cursor_execute = cursor_execute + " and airDate LIKE \""+date+"%\""
        cursor_execute = cursor_execute + " ORDER BY RANDOM() LIMIT 1"
        print("INFO: " + cursor_execute)
        self.cursor.execute(cursor_execute)
        random_episode = self.cursor.fetchone()
        print("INFO: "+str(random_episode))
        return random_episode

    ####mutto233 made this one####
    def get_next_episode(self, series):
        '''
        *
        * As a way of storing a "queue", I am storing the *next episode title in the "shows" table so I can 
        * determine what has been previously scheduled for each show
        *
        '''
        self.cursor.execute("SELECT lastEpisodeTitle FROM shows WHERE title LIKE ? COLLATE NOCASE", (series, ))
        last_title_list = self.cursor.fetchone()
        '''
        *
        * If the last episode stored in the "shows" table is empty, then this is probably a first run...
        *
        '''
        if last_title_list and last_title_list[0] == '':

            '''
            *
            * Find the first episode of the series
            *
            '''
            first_episode = self.get_first_episode(series)
            first_episode_title = first_episode[8]
            '''
            *
            * Add this episdoe title to the "shows" table for the queue functionality to work
            *
            '''
            #self.update_shows_table_with_last_episode(series, first_episode_title)
            return first_episode

        elif last_title_list:
            '''
            *
            * The last episode stored in the "shows" table was not empty... get the next episode in the series
            *
            '''
            """
            *
            * If this isn't a first run, then grabbing the next episode by incrementing id
            *
            """
            try:
                print("NOTICE: Getting next episode of "+series.upper()+ " by matching ID and series or playlist name")
                sql = ("SELECT * FROM episodes WHERE ( id > "+str(self.get_episode_id_alternate(last_title_list[0],series)[0])+
                       " AND showTitle LIKE ? ) ORDER BY id LIMIT 1 COLLATE NOCASE")
            except TypeError:
                try:
                    print("NOTICE: Getting next episode by matching title")
                    sql = ("SELECT * FROM episodes WHERE ( id > "+str(self.get_episode_id(last_title_list[0])[0])+
                       " AND showTitle LIKE ? ) ORDER BY id LIMIT 1 COLLATE NOCASE")
                    print("NOTICE: We have an old school last episode title. Using old method, then converting to new method")
                except TypeError:
                    sql = ""
                    print("ERROR: For some reason, episode was not stored correctly.  Maybe you updated your database and lost last episode?  Reverting to first episode")
            if sql=="":
                first_episode = self.get_first_episode(series)
                #self.update_shows_table_with_last_episode(series, first_episode[8])
                return first_episode
                
            self.cursor.execute(sql, (series, ))
            '''
            *
            * Try and advance to the next episode in the series, if it returns None then that means it reached the end...
            *
            '''
            next_episode = self.cursor.fetchone()
#            if next_episode != None and not last_title_list[0].startswith('/library/'):
#                # We have a case of an old style of last episode, so call that instead
#                print("+++++ We have an old school last episode title. Using old method, then converting to new method")
#                sql = ("SELECT * FROM episodes WHERE ( id > "+str(self.get_episode_id(last_title_list[0])[0])+
#                   " AND showTitle LIKE ? ) ORDER BY seasonNumber LIMIT 1 COLLATE NOCASE")
#                self.cursor.execute(sql, (series, ))
            
            if next_episode != None:
                #self.update_shows_table_with_last_episode(series, next_episode[8])
                return next_episode
            else:
                print("NOTICE: Not grabbing next episode restarting series, series must be over. Restarting from episode 1.")
                first_episode = self.get_first_episode(series)
                #self.update_shows_table_with_last_episode(series, first_episode[8])
                return first_episode

    def get_next_episode_alt(self, series, ID):
        '''
        *
        * As a way of storing a "queue", I am storing the *next episode title in the "shows" table so I can 
        * determine what has been previously scheduled for each show
        *
        *
        * If the last episode stored in the "shows" table is empty, then this is probably a first run...
        *
        '''
        if ID == '':

            '''
            *
            * Find the first episode of the series
            *
            '''
            first_episode = self.get_first_episode(series)
            first_episode_title = first_episode[8]
            '''
            *
            * Add this episdoe title to the "shows" table for the queue functionality to work
            *
            '''
            return first_episode

        else:
            '''
            *
            * The last episode stored in the "shows" table was not empty... get the next episode in the series
            *
            '''
            """
            *
            * If this isn't a first run, then grabbing the next episode by incrementing id
            *
            """
            try:
                print("NOTICE: Getting next episode of "+series.upper()+ " by matching ID and series or playlist name")
                sql = ("SELECT * FROM episodes WHERE ( id > "+str(ID)+
                       " AND showTitle LIKE ? ) ORDER BY id LIMIT 1 COLLATE NOCASE")
            except TypeError:
                try:
                    print("NOTICE: Getting next episode by matching ID and series or playlist name")
                    sql = ("SELECT * FROM episodes WHERE ( id > "+str(ID)+
                       " AND showTitle LIKE ? ) ORDER BY id LIMIT 1 COLLATE NOCASE")
                    print("NOTICE: We have an old school last episode title. Using old method, then converting to new method")
                except TypeError:
                    sql = ""
                    print("ERROR: For some reason, episode was not stored correctly.  Maybe you updated your database and lost last episode?  Reverting to first episode")
            if sql=="":
                first_episode = self.get_first_episode(series)
                #self.update_shows_table_with_last_episode(series, first_episode[8])
                return first_episode
                
            self.cursor.execute(sql, (series, ))
            '''
            *
            * Try and advance to the next episode in the series, if it returns None then that means it reached the end...
            *
            '''
            next_episode = self.cursor.fetchone()
            if next_episode != None:
                #self.update_shows_table_with_last_episode(series, next_episode[8])
                return next_episode
            else:
                print("NOTICE: Not grabbing next episode restarting series, series must be over. Restarting from episode 1.")
                first_episode = self.get_first_episode(series)
                #self.update_shows_table_with_last_episode(series, first_episode[8])
                return first_episode


    def get_last_episode(self, series):
        '''
        *
        * As a way of storing a "queue", I am storing the *next episode title in the "shows" table so I can 
        * determine what has been previously scheduled for each show
        *
        '''
        self.cursor.execute("SELECT lastEpisodeTitle FROM shows WHERE mediaID LIKE ? COLLATE NOCASE", (series, ))
        last_title_list = self.cursor.fetchone()
        '''
        *
        * If the last episode stored in the "shows" table is empty, then this is probably a first run...
        *
        '''
        if last_title_list and last_title_list[0] == '':

            '''
            *
            * Find the first episode of the series
            *
            '''
            first_episode = self.get_first_episode_by_id(series)
            first_episode_title = first_episode[8]
            '''
            *
            * Add this episdoe title to the "shows" table for the queue functionality to work
            *
            '''
            return first_episode

        elif last_title_list:
            '''
            *
            * The last episode stored in the "shows" table was not empty... get the next episode in the series
            *
            '''
            """
            *
            * If this isn't a first run, then grabbing the next episode by incrementing id
            *
            """
            try:
                print("NOTICE: Getting last episode of "+str(series)+ " by matching ID and series or playlist ID")
                sql = ("SELECT * FROM episodes WHERE ( id = "+str(self.get_episode_id_by_show_id(last_title_list[0],series)[0])+
                       " AND mediaID LIKE ? ) ORDER BY id LIMIT 1 COLLATE NOCASE")
            except TypeError as e:
                print("ERROR: " + str(e))
                try:
                    print("NOTICE: Getting last episode by matching title")
                    sql = ("SELECT * FROM episodes WHERE ( id = "+str(self.get_episode_id(last_title_list[0])[0])+
                       " AND mediaID LIKE ? ) ORDER BY id LIMIT 1 COLLATE NOCASE")
                    print("NOTICE: We have an old school last episode title. Using old method, then converting to new method")
                except TypeError:
                    sql = ""
                    print("ERROR: For some reason, episode was not stored correctly.  Maybe you updated your database and lost last episode?  Reverting to first episode")
            if sql=="":
                first_episode = self.get_first_episode_by_id(series)
                return first_episode
                
            self.cursor.execute(sql, (series, ))
            next_episode = self.cursor.fetchone()
            if next_episode != None:
                return next_episode
            else:
                print("NOTICE: Not grabbing next episode restarting series, series must be over. Restarting from episode 1.")
                first_episode = self.get_first_episode_by_id(series)
                return first_episode

    def get_last_episode_alt(self, series):
        '''
        *
        * As a way of storing a "queue", I am storing the *next episode title in the "shows" table so I can 
        * determine what has been previously scheduled for each show
        *
        '''
        self.cursor.execute("SELECT lastEpisodeTitle FROM shows WHERE title LIKE ? COLLATE NOCASE", (series, ))
        last_title_list = self.cursor.fetchone()
        '''
        *
        * If the last episode stored in the "shows" table is empty, then this is probably a first run...
        *
        '''
        if last_title_list and last_title_list[0] == '':

            '''
            *
            * Find the first episode of the series
            *
            '''
            first_episode = self.get_first_episode(series)
            first_episode_title = first_episode[8]
            '''
            *
            * Add this episdoe title to the "shows" table for the queue functionality to work
            *
            '''
            return first_episode

        elif last_title_list:
            '''
            *
            * The last episode stored in the "shows" table was not empty... get the next episode in the series
            *
            '''
            """
            *
            * If this isn't a first run, then grabbing the next episode by incrementing id
            *
            """
            try:
                print("NOTICE: Getting last episode of "+str(series)+ " by matching ID and series or playlist name")
                sql = ("SELECT * FROM episodes WHERE ( id = "+str(self.get_episode_id_alternate(last_title_list[0],series)[0])+
                       " AND showTitle LIKE ? ) ORDER BY id LIMIT 1 COLLATE NOCASE")
            except TypeError as e:
                print("ERROR: " + str(e))
                try:
                    print("NOTICE: Getting last episode by matching title")
                    sql = ("SELECT * FROM episodes WHERE ( id = "+str(self.get_episode_id(last_title_list[0])[0])+
                       " AND showTitle LIKE ? ) ORDER BY id LIMIT 1 COLLATE NOCASE")
                    print("NOTICE: We have an old school last episode title. Using old method, then converting to new method")
                except TypeError:
                    sql = ""
                    print("ERROR: For some reason, episode was not stored correctly.  Maybe you updated your database and lost last episode?  Reverting to first episode")
            if sql=="":
                first_episode = self.get_first_episode(series)
                return first_episode
                
            self.cursor.execute(sql, (series, ))
            next_episode = self.cursor.fetchone()
            if next_episode != None:
                return next_episode
            else:
                print("NOTICE: Not grabbing next episode restarting series, series must be over. Restarting from episode 1.")
                first_episode = self.get_first_episode_by_id(series)
                return first_episode

    def get_commercial(self, title):

        media = "commercials"
        sql = "SELECT * FROM "+media+" WHERE (title LIKE ?) COLLATE NOCASE"
        self.cursor.execute(sql, (title, ))
        datalist = list(self.cursor.fetchone())
        if datalist > 0:
            print(datalist)
            return datalist
        else:
            return None

    def get_now_playing(self):
        print("NOTICE: Getting Now Playing Item from Daily Schedule DB.")
        sql = "SELECT * FROM daily_schedule WHERE (time(endTime) >= time('now','localtime') AND time(startTime) <= time('now','localtime')) ORDER BY time(startTime) ASC"
        self.cursor.execute(sql)
        datalist = list(self.cursor.fetchone())
        print("NOTICE: Done.")
        return datalist
