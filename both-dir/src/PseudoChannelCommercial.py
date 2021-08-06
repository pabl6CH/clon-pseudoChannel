"""Commercial Functionality
"""
from random import shuffle
import random
import copy
from datetime import datetime
from datetime import timedelta
from src import Commercial
from src import PseudoChannelDatabase

class PseudoChannelCommercial():

    MIN_DURATION_FOR_COMMERCIAL = 1 #seconds
    COMMERCIAL_PADDING_IN_SECONDS = 0
    daily_schedule = []

    def __init__(self, commercials, commercialPadding, useDirtyGapFix):

        self.commercials = commercials
        self.db = PseudoChannelDatabase("pseudo-channel.db")
        self.COMMERCIAL_PADDING_IN_SECONDS = commercialPadding
        self.USE_DIRTY_GAP_FIX = useDirtyGapFix

    def get_random_commercial(self):

        random_commercial = random.choice(self.commercials)
#        random_commercial_dur_seconds = (int(random_commercial[4])/1000)%60
        random_commercial_dur_seconds = (int(random_commercial[4])/1000)
        while random_commercial_dur_seconds < self.MIN_DURATION_FOR_COMMERCIAL:
             random_commercial = random.choice(self.commercials)
             random_commercial_dur_seconds = (int(random_commercial[4])/1000)
#             random_commercial_dur_seconds = (int(random_commercial[4])/1000)%60
        return random_commercial



    def timedelta_milliseconds(self, td):

        return td.days*86400000 + td.seconds*1000 + td.microseconds/1000

    def pad_the_commercial_dur(self, commercial):

        commercial_as_list = list(commercial)
        commercial_as_list[4] = int(commercial_as_list[4]) + (self.COMMERCIAL_PADDING_IN_SECONDS * 1000)
        commercial = tuple(commercial_as_list)
        return commercial

    def get_commercials_to_place_between_media(self, last_ep, now_ep, strict_time, reset_time):

        reset_time = datetime.strptime(reset_time,'%H:%M')
        prev_item_end_time = datetime.strptime(last_ep.end_time.strftime('%Y-%m-%d %H:%M:%S.%f'), '%Y-%m-%d %H:%M:%S.%f')
        prev_item_start_time = datetime.strptime(last_ep.start_time, '%H:%M:%S')
        if(now_ep != "reset"):
            curr_item_start_time = datetime.strptime(now_ep.start_time, '%H:%M:%S')
        else:
            curr_item_start_time = reset_time
            curr_item_start_time += timedelta(days=1)
            #if(curr_item_start_time < reset_time):
                #curr_item_start_time = curr_item_start_time.replace(day=1)
            #else:
                #curr_item_start_time = curr_item_start_time.replace(day=2)

        # mutto233 has added some logic at this point
        # - All dates are now changed to 1/1/90 so midnight doesn't cause issues
        # - Issues with day skips again being adressed
        now = datetime.now()
        now = now.replace(year=1900, month=1, day=1)
        midnight = now.replace(hour=0,minute=0,second=0) 
        if(curr_item_start_time < reset_time):
            #curr_item_start_time = curr_item_start_time.replace(day=2)
            curr_item_start_time += timedelta(days=1)
        if(prev_item_end_time < reset_time):
            #prev_item_end_time = prev_item_end_time.replace(day=2)
            prev_item_end_time += timedelta(days=1)
        #else:
            #prev_item_end_time = prev_item_end_time.replace(day=1)
        if prev_item_start_time.hour < reset_time.hour and prev_item_end_time.hour >= reset_time.hour:
            prev_item_end_time = datetime.strptime('1900-01-02 0' + str(int(reset_time.hour)-1) + ':59:59', '%Y-%m-%d %H:%M:%S')
        time_diff = (curr_item_start_time - prev_item_end_time)
        
        if prev_item_end_time.replace(microsecond=0) > curr_item_start_time and strict_time == "false":
            # NOTE: This is just for the logic of this function, I have noticed that this 
            # may cause other issues in other functions, since now the day is off.
            print("NOTICE: WE MUST BE SKIPPING A DAY, ADDING A DAY TO THE START TIME")
            #curr_item_start_time  = curr_item_start_time.replace(day=2)
            curr_item_start_time  += timedelta(days=1)

        
        print("INFO: Last Item End Time -  %s" % prev_item_end_time.replace(microsecond=0))
        print("INFO: Next Item Start Time -  %s" % curr_item_start_time)
        print("INFO: Time to Fill - %s" % time_diff)
        
        count = 0
        commercial_list = []
        commercial_dur_sum = 0
        time_diff_milli = self.timedelta_milliseconds(time_diff)
        last_commercial = None
        time_watch = prev_item_end_time 
        new_commercial_start_time = prev_item_end_time + timedelta(seconds=1)
        while curr_item_start_time > new_commercial_start_time:
            time_diff = (curr_item_start_time - new_commercial_start_time)
            time_diff_milli = self.timedelta_milliseconds(time_diff)
            #random_commercial_without_pad = self.get_random_commercial()
            random_commercial_without_pad = self.db.get_random_commercial_duration(self.MIN_DURATION_FOR_COMMERCIAL*1000,time_diff_milli)
            """
            Padding the duration of commercials as per user specified padding.
            """
            try:
                random_commercial = self.pad_the_commercial_dur(random_commercial_without_pad)
            except Exception as e:
                print("ERROR: " + str(e))
                random_commercial_without_pad = self.db.get_random_commercial_duration(1,time_diff_milli)
                try:
                    random_commercial = self.pad_the_commercial_dur(random_commercial_without_pad)
                except Exception as e:
                    print("ERROR: " + str(e))
                    break
            raw_commercial_milli = int(random_commercial_without_pad[4])
            new_commercial_milli = int(random_commercial[4])
            commercial_dur_sum += new_commercial_milli
            if last_commercial != None:
                new_commercial_start_time = last_commercial.end_time + timedelta(seconds=1)
                new_commercial_end_time = new_commercial_start_time + \
                                          timedelta(milliseconds=int(new_commercial_milli))
            else:
                new_commercial_start_time = prev_item_end_time + timedelta(seconds=1)
                new_commercial_end_time = new_commercial_start_time + \
                                          timedelta(milliseconds=int(new_commercial_milli))
            formatted_time_for_new_commercial = new_commercial_start_time.strftime('%H:%M:%S')
            print("INFO: Time Left to Fill - " + str(time_diff))
            print("INFO: " + str(formatted_time_for_new_commercial) + " - " + str(random_commercial[3]) + " | " + str(random_commercial[4]/1000))
            new_commercial = Commercial(
                "Commercials",
                random_commercial[3],
                formatted_time_for_new_commercial, # natural_start_time
                new_commercial_end_time,
                random_commercial[4],
                "everyday", # day_of_week
                "true", # is_strict_time
                "1", # time_shift 
                "0", # overlap_max
                random_commercial[5], # plex_media_id
                random_commercial[6], # custom lib name
                "3", #media_id,
                None #notes
            )
            last_commercial = new_commercial
            if last_commercial != None:
                new_commercial_start_time = last_commercial.end_time + timedelta(seconds=1)
                new_commercial_end_time = new_commercial_start_time + \
                                          timedelta(milliseconds=int(new_commercial_milli))
            else:
                new_commercial_start_time = prev_item_end_time + timedelta(seconds=1)
                new_commercial_end_time = new_commercial_start_time + \
                                          timedelta(milliseconds=int(new_commercial_milli))
            while new_commercial_end_time - timedelta(seconds=self.COMMERCIAL_PADDING_IN_SECONDS) > curr_item_start_time:
                print("NOTICE: Commercial Runs Too Long. Rerolling")
                time_diff_milli = time_diff_milli - 250
                if time_diff_milli <= 100:
                    break
                random_commercial = self.db.get_random_commercial_duration(self.MIN_DURATION_FOR_COMMERCIAL*1000,time_diff_milli)
                if last_commercial != None:
                    new_commercial_start_time = last_commercial.end_time + timedelta(seconds=1)
                    new_commercial_end_time = new_commercial_start_time + \
                                              timedelta(milliseconds=int(new_commercial_milli))
                else:
                    new_commercial_start_time = prev_item_end_time + timedelta(seconds=1)
                    new_commercial_end_time = new_commercial_start_time + \
                                              timedelta(milliseconds=int(new_commercial_milli))
                print("INFO: Time Left to Fill - " + str(time_diff))
                try:
                    print("INFO: " + str(formatted_time_for_new_commercial) + " - " + str(random_commercial[3]) + " | " + str(random_commercial[4]/1000))
                except Exception as e:
                    print("ERROR: " + str(e))
                    break
                new_commercial = Commercial(
                    "Commercials",
                    random_commercial[3],
                    formatted_time_for_new_commercial, # natural_start_time
                    new_commercial_end_time,
                    random_commercial[4],
                    "everyday", # day_of_week
                    "true", # is_strict_time
                    "1", # time_shift 
                    "0", # overlap_max
                    random_commercial[5], # plex_media_id
                    random_commercial[6], # custom lib name
                    "3", #media_id,
                    None #notes
                )
                if random_commercial != None:
                    break
            
            '''if new_commercial_end_time > curr_item_start_time:

                # Fill up gap with commercials even if the last commercial gets cutoff
                if self.USE_DIRTY_GAP_FIX:
                    
                    commercial_list.append(new_commercial)
                # Find the best fitting final commercial and break
                else:

                    # If the gap is smaller than the shortest commercial, break.
                    gapToFill = curr_item_start_time - datetime.strptime(new_commercial.natural_start_time, '%H:%M:%S')
                    if int(self.commercials[0][4]) > self.timedelta_milliseconds(gapToFill):

                        break
                    else:

                        print("NOTICE: Finding correct FINAL commercial to add to List.")

                        last_comm = None
                        #for comm in self.commercials:

                        #if int(comm[4]) >= self.timedelta_milliseconds(gapToFill) and last_comm != None:

                        #random_final_comm = last_comm
                        random_final_comm = self.db.get_random_commercial_duration(self.timedelta_milliseconds(gapToFill)-1000,self.timedelta_milliseconds(gapToFill))

                        formatted_time_for_final_commercial = datetime.strptime(new_commercial.natural_start_time, '%H:%M:%S').strftime('%H:%M:%S')

                        final_commercial_end_time = datetime.strptime(new_commercial.natural_start_time, '%H:%M:%S') + \
                                      timedelta(milliseconds=int(random_final_comm[4])) 

                        final_commercial = Commercial(
                            "Commercials",
                            random_final_comm[3],
                            formatted_time_for_final_commercial, # natural_start_time
                            final_commercial_end_time,
                            random_final_comm[4],
                            "everyday", # day_of_week
                            "true", # is_strict_time
                            "1", # time_shift 
                            "0", # overlap_max
                            random_final_comm[5], # plex_media_id
                            random_final_comm[6], # custom lib name
                            "3", #media_id
                            None #notes
                        )
                        commercial_list.append(final_commercial)
                        #break
                        #last_comm = comm
                break'''
            commercial_list.append(new_commercial)
        return commercial_list
