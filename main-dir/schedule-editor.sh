#!/bin/bash
main_dir=$(pwd)
source config.cache
re='^[0-9]+$'
number_of_channels=$(ls | grep pseudo-channel_ | wc -l)
channel_number=$1
loop_or_exit=loop

time_entry() {
sleep 1
#clear
echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
echo "ENTER the START TIME for THIS ENTRY in 24h format"
read -p 'Time (24h): ' start_time
echo "START TIME set to $start_time"
sleep 1
#clear
echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
echo "Choose MEDIA TYPE to start at $start_time"
select media_type in "Movie" "TV Series" "Random TV Episode"
        do
        sleep 1
	clear
	echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
	if [[ "$media_type" == "Movie" ]]
		then
		type="\"movie\""
		entry="MOVIE"
		#echo "ENTER the MOVIE TITLE"
		#read -p 'Title: ' title
		title="\"random\""
	elif [[ "$media_type" == "TV Series" ]]
		then
		type="\"series\""
		echo "ENTER the TV SERIES title"
		read -p 'Title: ' title
		entry="SHOW"
		title=$(echo $title | recode ..html)
		title="\"$title\""
	elif [[ "$media_type" == "Random TV Episode" ]]
		then
		type="\"random\""
		echo "ENTER the NAME of the TV SHOW to schedule RANDOM EPISODES from"
		read -p 'Title: ' title
		entry="SHOW"
		title=$(echo $title | recode ..html)
		title="\"$title\""
	fi
        break
done
sleep 1
clear
echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
echo "Start this $entry to start at the EXACT TIME specified or AFTER"
echo "the PREVIOUS show or movie ENDS?"
select strict_time_entry in "Exact Time" "After Previous"
	do
	if [[ $strict_time_entry == "Exact Time" ]]
		then
		strict_time="\"true\""
		time_shift="\"1\""
		echo "The $entry $title will play at exactly $start_time"
	elif [[ $strict_time_entry == "After Previous" ]]
		then
		sleep 1
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
		strict_time="\"false\""
		echo "TIME SHIFT VALUE"
		echo "This value will determine how much commercial time will be placed"
		echo "in between the end of the previous show or movie and the start of this $entry"
		echo "The value entered will restrict the start time to a time that ends in that number"
		echo "FOR EXAMPLE: A value of 5 will allow the $entry to start at"
		echo "5, 10, 15, 20, etc. after the hour. A value of 30 will only allow the $entry to"
		echo "start on the half-hour. A value of 2 will restrict start times to even-numbered minutes only."
		echo "ENTER the TIME SHIFT value"
		read -p 'Time Shift: ' time_shift_entry
		time_shift="\"$time_shift_entry\""
		while ! [[ $time_shift_entry =~ $re ]]
			do
			echo "ENTER the TIME SHIFT value"
			read -p 'Time Shift: ' time_shift_entry
			time_shift="\"$time_shift_entry\""
		done
	fi
break
done
if [[ $media_type == "Movie" ]]
	then
	sleep 1
	clear
	echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
	echo "Restrict RANDOM MOVIE selection based on available PLEX METADATA?"
	read -p 'Y/N: ' add_xtra
	while [[ "$add_xtra" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
		do
		echo "Restrict RANDOM MOVIE selection based on available PLEX METADATA?"
		read -p 'Y/N: ' add_xtra
	done
	if [[ "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
		then
		sleep 1
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
		select xtra_tag in "Studio" "MPAA Rating" "Year" "Decade" "Genre" "Director" "Writer" "Actor" "Collection"
			do
			sleep 1
			clear
			echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
			if [[ "$xtra_tag" == "Studio" ]]
				then
				echo "Enter the NAME of the MOVIE STUDIO(S) to FILTER by (Example: Amblin Entertainment)."
				enter_studio=yes
				echo -n "studio:" > xtra.temp
				while [[ "$enter_studio" == @(Y|y|Yes|yes|YES) ]]
					do
					read -p 'Studio(s) :' xtra_studio
					echo -n "$xtra_studio" >> xtra.temp
					echo "ENTER another STUDIO?"
					echo "Multiples are treated as an AND, not OR. Results will be filtered by ALL VALUES."
					read -p 'Y/N: ' enter_studio
					while [[ "$enter_studio" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
						do
						echo "ENTER another STUDIO?"
						read -p 'Y/N: ' enter_studio
					done
				if [[ "$enter_studio" == @(Y|y|Yes|yes|YES) ]]
					then
					echo -n "," >> xtra.temp
				fi
				done
			fi
                        if [[ "$xtra_tag" == "MPAA Rating" ]]
				then
				echo "ADD the MPAA RATING(s) to FILTER by (Example: PG-13)"
				enter_rating=yes
				echo -n "contentRating:" > xtra.temp
				while [[ "$enter_rating" == @(Y|y|Yes|yes|YES) ]]
					do
					read -p 'Rating(s): ' xtra_rating
					echo -n "$xtra_rating" >> xtra.temp
					echo "ENTER another RATING?"
					echo "Multiples are treated as an AND, not OR. Results will be filtered by ALL VALUES."
					read -p 'Y/N: ' enter_rating
					while [[ "$enter_rating" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
						do
						echo "ENTER another RATING?"
						read -p 'Y/N: ' enter_rating
					done
				if [[ "$enter_rating" == @(Y|y|Yes|yes|YES) ]]
					then
					echo -n "," >> xtra.temp
				fi
				done
			fi
                        if [[ "$xtra_tag" == "Year" ]]
				then
				echo "ADD RELEASE YEAR(S) to FILTER by (Example: 1982)"
				echo -n "year:" > xtra.temp
				read -p 'Year(s): ' xtra_year
				echo -n "$xtra_year" >> xtra.temp
			fi
                        if [[ "$xtra_tag" == "Decade" ]]
				then
				echo "ADD the DECADE of release to FILTER by (Example: 1980)"
				echo -n "decade:" > xtra.temp
				read -p 'Decade: ' xtra_decade
				echo -n "$xtra_decade" >> xtra.temp
			fi
                        if [[ "$xtra_tag" == "Genre" ]]
				then
				echo "ENTER GENRES to the RANDOM MOVIE FILTER (Example: Action)"
				enter_genre=yes
				echo -n "genre:" > xtra.temp
				while [[ "$enter_genre" == @(Y|y|Yes|yes|YES) ]]
					do
					read -p 'Genre: ' xtra_genre
					echo -n "$xtra_genre" >> xtra.temp
					echo "ENTER another GENRE?"
					echo "Multiples are treated as an AND, not OR. Results will be filtered by ALL VALUES."
					read -p 'Y/N: ' enter_genre
					while [[ "$enter_genre" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
						do
						echo "ENTER another GENRE?"
						read -p 'Y/N: ' enter_genre
					done
				if [[ "$enter_genre" == @(Y|y|Yes|yes|YES) ]]
					then
					echo -n "," >> xtra.temp
				fi
				done
			fi
                        if [[ "$xtra_tag" == "Director" ]]
				then
				echo "FILTER by the following DIRECTOR(S) (Example: Taika Waititi)"
				enter_director=yes
				echo -n "director:" > xtra.temp
				while [[ "$enter_director" == @(Y|y|Yes|yes|YES) ]]
					do
					read -p 'Director: ' xtra_director
					echo -n "$xtra_genre" >> xtra.temp
					echo "ENTER another GENRE?"
					echo "Multiples are treated as an AND, not OR. Results will be filtered by ALL VALUES."
					read -p 'Y/N: ' enter_director
					while [[ "$enter_director" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
						do
						echo "ENTER another DIRECTOR?"
						read -p 'Y/N: ' enter_director
					done
				if [[ "$enter_director" == @(Y|y|Yes|yes|YES) ]]
					then
					echo -n "," >> xtra.temp
				fi
				done
			fi
                        if [[ "$xtra_tag" == "Writer" ]]
				then
				echo "ADD WRITER(S) to FILTER by (Example: Sandra Bullock)"
				enter_writer=yes
				echo -n "Writer:" > xtra.temp
				while [[ "$enter_writer" == @(Y|y|Yes|yes|YES) ]]
					do
					read -p 'Writer: ' xtra_writer
					echo -n "$xtra_writer" >> xtra.temp
					echo "ENTER another WRITER?"
					echo "Multiples are treated as an AND, not OR. Results will be filtered by ALL VALUES."
					read -p 'Y/N: ' enter_writer
					while [[ "$enter_writer" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
						do
						echo "ENTER another writer?"
						read -p 'Y/N: ' enter_writer
					done
				if [[ "$enter_writer" == @(Y|y|Yes|yes|YES) ]]
					then
					echo -n "," >> xtra.temp
				fi
				done
			fi
                        if [[ "$xtra_tag" == "Actor" ]]
				then
				echo "ADD ACTOR(S) to FILTER by (Example: Sandra Bullock)"
				enter_actor=yes
				echo -n "Actor:" > xtra.temp
				while [[ "$enter_actor" == @(Y|y|Yes|yes|YES) ]]
					do
					read -p 'Actor: ' xtra_writer
					echo -n "$xtra_actor" >> xtra.temp
					echo "ENTER another ACTOR?"
					echo "Multiples are treated as an AND, not OR. Results will be filtered by ALL VALUES."
					read -p 'Y/N: ' enter_actor
					while [[ "$enter_actor" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
						do
						echo "ENTER another actor?"
						read -p 'Y/N: ' enter_actor
					done
				if [[ "$enter_actor" == @(Y|y|Yes|yes|YES) ]]
					then
					echo -n "," >> xtra.temp
				fi
				done
			fi
			if [[ "$xtra_tag" == "Collection" ]]
				then
				echo "A COLLECTION is a user-defined TAG. Any selection of MOVIES can be added to a COLLECTION"
				echo "and DEFINED here to be FILTERED by. (Example: Marvel Movies or Halloween Movies)"
				echo -n "collection:" > xtra.temp
				read -p 'Collection(s): ' xtra_collection
				echo -n "$xtra_collection" >> xtra.temp
			fi
                        xtra=$(cat xtra.temp)
                        xtra="\"$xtra\""
                        break
		done
		else
		> xtra.temp
	fi
fi
overlap_max="\"30\""
}
clear
echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
if [[ $channel_number == '' ]] # IF NO ARGUMENT PROVIDED, ASK IF USER WANTS TO EDIT THE MAIN CONFIG OR SELECT A CHANNEL
        then
	echo "CHOOSE which CHANNEL SCHEDULE to create."
	echo "Enter CHANNEL NUMBER between 1 and $number_of_channels"
                read -p 'Channel Number: ' channel_number
                while ! [[ $channel_number =~ $re ]] # VALIDATES THAT CHANNEL NUMBER IS ACTUALLY A NUMBER
                        do
                        echo "Enter CHANNEL NUMBER"
                        read -p 'Channel Number: ' channel_number
                done
                while ! [[ $channel_number -ge 1 && $channel_number -le $number_of_channels ]] # VALIDATES CHANNEL NUMBER AGAINST ACTUAL CHANNELS
                        do
                        echo "ERROR: Channel NOT FOUND."
                        echo "Channels must be between 1 and $number_of_channels"
                        echo "Enter CHANNEL NUMBER"
                        read -p 'Channel Number: ' channel_number
                done
fi
                echo "Now editing the schedule for CHANNEL $channel_number"
		if [[ $channel_number -ge 1 && $channel_number -le 9 ]] # SET DIRECTORY TO SELECTED CHANNEL
                	then
	                cd pseudo-channel_0"$channel_number"
	        elif [[ $channel_number -ge 10 ]]
        	        then
                	cd pseudo-channel_"$channel_number"
		fi
sleep 1
clear
echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
echo "Backing up CURRENT SCHEDULE FILE..."
sleep 1
cp pseudo_schedule.xml pseudo_schedule.backup
echo "Creating NEW SCHEDULE FILE..."
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" > pseudo_schedule.xml
echo "<schedule>" >> pseudo_schedule.xml
sleep 1
clear
echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
echo "CHOOSE which DAY to SCHEDULE"
select day_of_week in "Sunday" "Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday" "Weekends" "Weekdays" "Every Day" "Exit"
	do
	sleep 1
	clear
	echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
	if [[ "$day_of_week" == "Sunday" ]]
		then
		echo "<sundays>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</sundays>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Monday" ]]
		then
		echo "<mondays>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</mondays>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Tuesday" ]]
		then
		echo "<tuesdays>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</tuesdays>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Wednesday" ]]
		then
		echo "<wednesdays>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</wednesdays>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Thursday" ]]
		then
		echo "<thursdays>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</thursdays>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Friday" ]]
		then
		echo "<fridays>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</fridays>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Saturday" ]]
		then
		echo "<saturdays>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</saturdays>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Weekends" ]]
		then
		echo "<weekends>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</weekends>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Weekdays" ]]
		then
		echo "<weekdays>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</weekdays>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Every Day" ]]
		then
		echo "<everyday>" >> pseudo_schedule.xml
		enter_time=yes
		while [[ $enter_time == @(Y|y|Yes|yes|YES) ]]
			do
			time_entry
			if [[ "$entry" == "MOVIE" && "$add_xtra" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max xtra=$xtra>$start_time</time>" >> pseudo_schedule.xml
				else
				echo "<time title=$title type=$type strict-time=$strict_time time-shift=$time_shift overlap_max=$overlap_max>$start_time</time>" >> pseudo_schedule.xml
			fi
			echo "ADD another SHOW or MOVIE?"
			read -p 'Y/N: ' enter_time
			while [[ "$enter_time" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				do
				echo "ADD another SHOW or MOVIE?"
				read -p 'Y/N: ' enter_time
			done
		done
		echo "</everyday>" >> pseudo_schedule.xml
	fi
	if [[ "$day_of_week" == "Exit" ]]
		then
		echo "FINALIZING SCHEDULE FORMATTING..."
		echo "</schedule>" >> pseudo_schedule.xml
		#sudo ./updatexml.sh
		echo "CLEANING UP TEMPORARY FILES"
		rm xtra.temp
		echo "REMOVE BACKUP of Channel $channel_number's previous schedule?"
		read -p 'Y/N: ' remove_backup_schedule
			while [[ "$remove_backup_schedule" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
			do
			clear
			echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
			echo "REMOVE BACKUP of Channel $channel_number's previous schedule?"
			read -p 'Y/N: ' remove_backup_schedule
			done
		if [[ "$remove_backup_schedule" == @(Y|y|Yes|yes|YES) ]]
			then
			rm pseudo_schedule.backup
		fi
		cd $main_dir
		(bash ./updatexml.sh)
		exit 0
	fi
sleep 1
clear
echo "++++++++++++++++++++PSEUDO CHANNEL SCHEDULE EDITOR++++++++++++++++++++"
echo "CHOOSE which DAY to SCHEDULE"
echo "1) Sunday       4) Wednesday   7) Saturday   10) Every Day"
echo "2) Monday       5) Thursday    8) Weekends   11) Exit"
echo "3) Tuesday      6) Friday      9) Weekdays"
done
