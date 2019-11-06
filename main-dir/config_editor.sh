#!/bin/bash
#### Script to make changes to config files

#Allow command argument $1 to indicate channel to edit config
#If $1 == '' Choose main config file or specific channel
#cd into channel directory if necessary
source config.cache
re='^[0-9]+$'
number_of_channels=$(ls | grep pseudo-channel_ | wc -l)
channel_number=$1
loop_or_exit=loop

clear
echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
echo "Welcome to the CONFIG EDITOR script."
if [[ $channel_number == '' ]] # IF NO ARGUMENT PROVIDED, ASK IF USER WANTS TO EDIT THE MAIN CONFIG OR SELECT A CHANNEL
	then
	echo "No channel number specified. Edit the main config file?"
	read -p 'Y/N: ' edit_main_config
        while [[ "$edit_main_config" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
		do
                echo "No CHANNEL NUMBER specified. Edit the MAIN CONFIG file?"
                read -p 'Y/N: ' edit_main_config
                done
	if [[ "$edit_main_config" == @(Y|y|Yes|yes|YES) ]]
		then
	        echo "Now editing MAIN CONFIG file." # IF THE USER WANTS TO EDIT THE MAIN CONFIG
		sleep 1
		else
		echo "Enter CHANNEL NUMBER between 1 and $number_of_channels" # IF THE USER WANTS TO EDIT A CHANNEL CONFIG, ASKING FOR CHANNEL NUMBER
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
		echo "Now editing CHANNEL $channel_number file"
		sleep 1
	fi
elif ! [[ $channel_number =~ $re ]] # VALIDATES ARGUMENT IS A NUMBER, IF NOT, PROMPT FOR RE-ENTRY
	then
	echo "ERROR! INVALID CHANNEL SPECIFIED"
	echo "Enter CHANNEL NUMBER"
	read -p 'Channel Number: ' channel_number
	while ! [[ $channel_number =~ $re ]]
	do
	echo "Enter CHANNEL NUMBER"
	read -p 'Channel Number: ' channel_number
	done
elif ! [[ $channel_number -ge 1 && $channel_number -le $number_of_channels ]] # VALIDATES ARGUMENT IS A VALID CHANNEL NUMBER, PROMPT FOR RE-ENTRY IF NOT
	then
	echo "ERROR! SPECIFIED CHANNEL DOES NOT EXIST"
	echo "Channels must be between 1 and $number_of_channels"
	echo "Enter CHANNEL NUMBER"
	read -p 'Channel Number: ' channel_number
	while ! [[ $channel_number -ge 1 && $channel_number -le $number_of_channels ]]
		do
		echo "ERROR! SPECIFIED CHANNEL DOES NOT EXIST"
		echo "Channels must be between 1 and $number_of_channels"
		echo "Enter CHANNEL NUMBER"
		read -p 'Channel Number: ' channel_number
	done
fi
if [[ $channel_number -ge 1 && $channel_number -le 9 ]] # SET DIRECTORY TO SELECTED CHANNEL
		then
		cd pseudo-channel_0"$channel_number"
	elif [[ $channel_number -ge 10 ]]
		then
		cd pseudo-channel_"$channel_number"
fi
while [[ $loop_or_exit == "loop" ]]
do
sleep 1
clear
echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
select category in "BASIC OPTIONS" "ADVANCED OPTIONS" "QUIT" # MAIN MENU
	do
	if [[ "$category" == "BASIC OPTIONS" && $channel_number == '' ]] # BASIC OPTIONS FOR MAIN CONFIG
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
		echo "CHOOSE an OPTION to SET VALUE in CONFIG"
		select config_option in "Plex Server URL" "Plex Client" "Plex Libraries" "Plex Token" "Daily Reset Time" "Back"
		do
		break
		done
	elif [[ "$category" == "BASIC OPTIONS" && $channel_number != '' ]] # BASIC OPTIONS FOR CHANNEL CONFIG
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
		echo "CHOOSE an OPTION to SET VALUE in CONFIG"
		select config_option in "Plex Client" "Plex Libraries" "Use Commercials?" "Back"
		do
		break
		done
	elif [[ "$category" == "ADVANCED OPTIONS" && $channel_number == '' ]] # ADVANCED OPTIONS FOR MAIN CONFIG
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
		echo "CHOOSE an OPTION to SET VALUE in CONFIG"
		select config_option in "Use Daily Overlap Cache" "Dirty Gap Fix" "Debug Mode" "Commercial Padding" "Back"
		do
		break
		done
	elif [[ "$category" == "ADVANCED OPTIONS" && $channel_number != '' ]] # ADVANCED OPTIONS FOR CHANNEL CONFIG
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
		echo "CHOOSE an OPTION to SET VALUE in CONFIG"
		select config_option in "Debug Mode" "TV Guide Page" "Use Daily Overlap Cache" "Dirty Gap Fix" "Commercial Padding" "Back"
		do
		break
		done
	elif [[ "$category" == "QUIT" ]] # QUIT THE SCRIPT
		then
		echo "PREPARING TO EXIT CONFIG EDITOR..."
		sleep 1
		if [[ $channel_number == '' ]]
			then
			clear
			echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
			echo "Changes to MAIN CONFIG file have been saved."
			echo "COPY changes to ALL CONFIG FILES?"
			echo "(WARNING: Copying changes will overwrite all"
			echo "channel-specific settings)"
			read -p 'Y/N: ' write_to_all
			while [[ "$write_to_all" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
	                        do
        	                echo "COPY changes to ALL CONFIG FILES?"
                	        read -p 'Y/N: ' write_to_all
			done
			if [[ "$write_to_all" == @(Y|y|Yes|yes|YES) ]]
				then
				echo "There are $number_of_channels channels detected."
				channel=1
				while [[ $channel -le $number_of_channels ]]
				do
					if [[ $channel -ge 1 && $channel -le 9 ]] # SET DIRECTORY TO SELECTED CHANNEL
				                then
					                cd pseudo-channel_0"$channel"
				        elif [[ $channel -ge 10 ]]
				                then
				                cd pseudo-channel_"$channel"
					fi
					cp ../pseudo_config.py ./
					echo "CONFIG FILE copied to CHANNEL $channel of $number_of_channels"
					cd ..
					((channel++))
				done
			fi
			else
			echo "CHANGES to the CHANNEL $channel_number CONFIG FILE have been SAVED."
			sleep 1
		fi

		echo "EXITING CONFIG EDITOR..."
		sleep 1
		clear
		exit 0
	fi
	break
	done
if [[ "$config_option" == "Plex Server URL" ]] # CHANGE THE PLEX SERVER URL AND PORT STORED IN THE PLEX_TOKEN.PY FILE
	then
	clear
	echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
	#GET PLEX SERVER IP AND PORT
	if [[ $server_ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]
		then
		echo "PLEX SERVER IP detected as $server_ip"
		echo "Press ENTER to save $server_ip as your PLEX SERVER IP address"
		echo "or enter the new PLEX SERVER IP address below."
		read -p "Plex Server IP ($server_ip): " server_ip_entry
		if [[ $server_ip_entry == '' ]]
			then
			echo "PLEX SERVER IP is $server_ip"
			else
			server_ip="$server_ip_entry"
		fi
		else
		echo "ENTER the IP ADDRESS of your PLEX SERVER"
		read -p 'Plex Server IP: ' server_ip
	fi
	echo "ENTER the PORT number for your PLEX SERVER"
	read -p "Public Port (default: $server_port): " server_port_entry
	if [ "$server_port_entry" != '' ]
		then
		server_port="$server_port_entry"
	fi
	echo "PLEX SERVER is $server_ip:$server_port"
	sed -i "s/baseurl =.*/baseurl = \'http:\/\/$server_ip:$server_port\'/" plex_token.py
	sed -i "s/server_ip=.*/server_ip=$server_ip/" config.cache
	sed -i "s/server_port=.*/server_port=$server_port/" config.cache
	sleep 1
elif [[ "$config_option" == "Plex Token" ]] # CHANGE THE PLEX AUTH TOKEN VALUE IN THE PLEX_TOKEN.PY FILE
	then
	clear
	echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
        if [ "$server_token" != '' ]
                then
		echo "AUTH TOKEN is currently set to $server_token"
		echo "PRESS ENTER to KEEP THIS as your AUTH TOKEN"
		echo "or ENTER your new PLEX AUTH TOKEN."
		echo "(for help finding token, check here: https://bit.ly/2p7RtOu)"
		else
		echo "ENTER your PLEX AUTHENTICATION TOKEN" # GET PLEX SERVER AUTH TOKEN
	        echo "(for help finding token, check here: https://bit.ly/2p7RtOu)"
        fi
	read -p 'Plex Auth Token: ' server_token_entry
	if [ "$server_token_entry" == '' ]
		then
		echo "PLEX AUTH TOKEN saved as $server_token"
		server_token="\'$server_token\'"
		else
		server_token=$server_token_entry
                echo "PLEX AUTH TOKEN saved as $server_token"
		server_token="\'$server_token\'"
	fi
	sed -i "s/token =.*/token = $server_token/" plex_token.py
	sed -i "s/server_token=.*/server_token=$server_token/" config.cache
	sleep 1
elif [[ "$config_option" == "Plex Client" ]] # CHANGE PLEX CLIENT
	then
	clear
	echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
	clientlist=$(xmllint --xpath "//Server/@name" "http://$serverip_ip:$server_port/clients" | sed "s|name=||g" | sed "s|^ ||g" && echo -e " Other") # GET LIST OF CLIENTS
	eval set $clientlist
	select ps_client_entry in "$@"
		do
		if [[ "$ps_client_entry" == "Other" ]]
			then
			read -p 'Client Name: ' ps_client_entry
			ps_client_entry=$(eval echo $ps_client_entry)
		fi
		ps_client="[\"$ps_client_entry\"]"
		sed -i "s/plexClients = .*/plexClients = $ps_client/" pseudo_config.py
		echo "Plex Client set to $ps_client_entry in the config"
		sleep 1
		break
	done
elif [[ "$config_option" == "Plex Libraries" ]] #CHANGE PLEX LIBRARIES
	then
	clear
	echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
	if [[ $channel_number =~ $re ]]
		then
		echo "++++++CHANNEL $channel_number PLEX LIBRARIES++++++"
		echo "Add LIBRARIES to use with CHANNEL $channel_number"
		else
		echo "Add ALL LIBRARIES that may be used for ANY CHANNEL here."
	fi
	echo "ENTER the name of EACH desired Plex library defined as TV SHOWS"
	enter_tv_shows=yes
	echo -n "[" > tv-libraries.temp
	while [[ "$enter_tv_shows" == @(Y|y|Yes|yes|YES) ]]
		do
		read -p 'TV Show Library Name: ' tv_library_entry
		echo -n "\"$tv_library_entry\"" >> tv-libraries.temp
		echo "ENTER another TV SHOW LIBRARY?"
		read -p 'Y/N: ' enter_tv_shows
		while [[ "$enter_tv_shows" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
			do
			echo "ENTER another TV SHOW LIBRARY?"
			read -p 'Y/N: ' enter_tv_shows
			done
		if [[ "$enter_tv_shows" == @(Y|y|Yes|yes|YES) ]]
			then
			echo -n ", " >> tv-libraries.temp
		fi
		done
		echo -n "]," >> tv-libraries.temp
		echo "ENTER the name of EACH Plex library defined as MOVIES"
		enter_movies=yes
		echo -n "[" > movie-libraries.temp
	while [[ "$enter_movies" == @(Y|y|Yes|yes|YES) ]]
		do
		read -p 'Movie Library Name: ' movie_library_entry
		echo -n "\"$movie_library_entry\"" >> movie-libraries.temp
		echo "ENTER another MOVIE LIBRARY?"
		read -p 'Y/N: ' enter_movies
		while [[ "$enter_movies" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
			do
			echo "ENTER another MOVIE LIBRARY?"
			read -p 'Y/N: ' enter_movies
			done
		if [[ "$enter_movies" == @(Y|y|Yes|yes|YES) ]]
			then
			echo -n ", " >> movie-libraries.temp
		fi
		done
		echo -n "]," >> movie-libraries.temp
		echo "Use COMMERCIALS in between scheduled content?"
		read -p 'Y/N: ' enter_commercials
	while [[ "$enter_commercials" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
		do
			echo "Use COMMERCIALS in between scheduled content?"
			read -p 'Y/N: ' enter_commercials
                done
	if [[ "$enter_commercials" == @("Y"|"y"|"yes"|"Yes"|"YES") ]]
                then
	                commercials_true=true
			echo "ENTER the name of EACH Plex library defined as COMMERCIALS"
			echo -n "[" > commercial-libraries.temp
	fi
	while [[ "$enter_commercials" == @(Y|y|Yes|yes|YES) ]]
		do
			read -p 'Commercial Library Name: ' commercial_library_entry
			echo -n "\"$commercial_library_entry\", " >> commercial-libraries.temp
			echo "ENTER another COMMERCIAL LIBRARY?"
                                read -p 'Y/N: ' enter_commercials
                                while [[ "$enter_commercials" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
                                        do
                                        echo "ENTER another COMMERCIAL LIBRARY?"
                                        read -p 'Y/N: ' enter_commercials
                                done
		done
	if [[ "$commercials_true" == "true" ]]
		then
			truncate -s-2 commercial-libraries.temp
	                echo -n "]," >> commercial-libraries.temp
			commercial_libraries=$(cat commercial-libraries.temp)
	                sed -i "/.\"Commercials\" :*./c\     \"Commercials\" : $commercial_libraries" pseudo_config.py
	fi
	tv_libraries=$(cat tv-libraries.temp)
	sed -i "/.\"TV Shows\" :*./c\     \"TV Shows\" : $tv_libraries" pseudo_config.py # WRITE TV LIBRARIES TO CONFIG
	movie_libraries=$(cat movie-libraries.temp)
	sed -i "/.\"Movies\" :*./c\     \"Movies\"   : $movie_libraries" pseudo_config.py # WRITE MOVIE LIBRARIES TO CONFIG
elif [[ "$config_option" == "Daily Reset Time" ]]
	then
	clear
	echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
	        echo "Set the TIME for PSEUDO CHANNEL to GENERATE the DAILY SCHEDULE"
        	echo "USE 24H FORMAT (ex: 23:00)"
	        read -p 'Daily Reset Time: ' reset_time_entry
#		if [[ $reset_time_entry =~ ^[01][0-9]:[0-5][0-9]|2[0-3]:[0-5][0-9]$ ]]
#			then
			echo "Saving DAILY RESET TIME as $reset_time_entry..."
			sleep 1
#			else
#			echo "Set the TIME for PSEUDO CHANNEL to GENERATE the DAILY SCHEDULE"
#			echo "USE 24H FORMAT (ex: 23:00)"
#			read -p 'Daily Reset Time: ' reset_time_entry
#		fi
	        reset_time_formatted=$(echo $reset_time_entry | sed -e "s|^[0-9]:.*|0$reset_time_entry|g")
	        reset_time_hour="${reset_time_formatted:0:2}"
	        reset_time_hour="$(echo $reset_time_hour | sed -e s/^[0]//)"
	        reset_time_minute="${reset_time_formatted: -2}"
	        reset_time_minutes="$(echo $reset_time_minutes | sed -e s/^[0]//)"
	        # SET UP CRON JOB TO RUN DAILY RESET
		crontab -l | grep -v 'daily-cron.sh' | crontab -
	        echo \#\!/bin/bash > ./daily-cron.sh && echo "cd $PWD" >> ./daily-cron.sh && echo "bash ./generate-channels-daily-schedules.sh" >> ./daily-cron.sh
		( crontab -l ; echo "$reset_time_minute $reset_time_hour * * * $PWD/daily-cron.sh" ) | crontab -
		sed -i "s/dailyUpdateTime.*/dailyUpdateTime = \"$reset_time_entry\"/" pseudo_config.py
	elif [[ "$config_option" == "Use Commercials?" ]]
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
	        echo "Use COMMERCIALS in between scheduled content?"
	        read -p 'Y/N: ' use_commercials
	        while [[ "$use_commercials" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
	                do
	                echo "Use COMMERCIALS in between scheduled content?"
	                read -p 'Y/N: ' use_commercials
                done
	        if [[ "$use_commercials" == "true" ]]
	                then
			commercials_true=true
			sed -i "s/useCommercialInjection =.*/useCommercialInjection = \"true\"/" pseudo_config.py
			echo "COMMERCIAL INJECTION has been turned ON"
			else
			sed -i "s/useCommercialInjection =.*/useCommercialInjection = \"false\"/" pseudo_config.py
			echo "COMMERCIAL INJECTION has been turned OFF"
	        fi
	elif [[ "$config_option" == "Use Daily Overlap Cache" ]]
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
			echo "When the schedule updates every 24 hours,"
			echo "it's possible that it will interrupt any"
			echo "shows / movies that were playing from the"
			echo "previous day. To fix this, this option saves"
			echo "a cached schedule from the previous day to"
			echo "override any media that is trying to play"
			echo "while the previous day is finishing."
			echo "This option is off by default."
			echo "Turn on DAILY OVERLAP CACHE?"
			read -p 'Y/N: ' use_daily_overlap
			if [[ "$use_daily_overlap" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
				then
				echo "Turn on DAILY OVERLAP CACHE?"
	                        read -p 'Y/N: ' use_daily_overlap
			fi
			if [[ "$use_daily_overlap" = @(Y|y|Yes|yes|YES) ]]
				then
				sed -i "s/useDailyOverlapCache =.*/useDailyOverlapCache = True/" pseudo_config.py
				echo "DAILY OVERLAP CACHE has been set to TRUE"
				else
				sed -i "s/useDailyOverlapCache =.*/useDailyOverlapCache = False/" pseudo_config.py
				echo "DAILY OVERLAP CACHE has been set to FALSE"
			fi
	elif [[ "$config_option" == "Dirty Gap Fix" ]]
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
			echo "When this option is turned off, commercials"
			echo "are selected to fit in the gap between the last"
			echo "commercial and the next scheduled item. If this"
			echo "option is turned on, the script will not take"
			echo "length into account when choosing the last commercial."
			echo "This may result in partial playback until the next show"
			echo "or movie starts. However, it may be preferred if your"
			echo "commercial library is small or doesn't contain any"
			echo "shorter (5-15 second) videos in the commercials library."
			echo "Turn on DIRTY GAP FIX?"
			read -p 'Y/N: ' use_dirty_gap
			if [[ "$use_dirty_gap" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
                                then
				echo "Turn on DIRTY GAP FIX?"
				read -p 'Y/N: ' use_dirty_gap
			fi
			if [[ "$use_dirty_gap" = @(Y|y|Yes|yes|YES) ]]
                                then
                                sed -i "s/useDirtyGapFix =.*/useDirtyGapFix = True/" pseudo_config.py
				echo "DIRTY GAP FIX has been set to TRUE"
                                else
                                sed -i "s/useDirtyGapFix =.*/useDirtyGapFix = False/" pseudo_config.py
				echo "DIRTY GAP FIX has been set to FALSE"
                        fi

	elif [[ "$config_option" == "Debug Mode" ]]
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
			echo "Debug mode provides more terminal output and writes"
			echo "the entire daily schedule (including commercials) to"
			echo "the web and xml file outputs."
			echo "Turn on DEBUG MODE?"
			read -p 'Y/N: ' use_debug_mode
	                if [[ "$use_debug_mode" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
                                then
                                echo "Turn on DEBUG MODE?"
                                read -p 'Y/N: ' use_debug_mode
                        fi
                        if [[ "$use_debug_mode" = @(Y|y|Yes|yes|YES) ]]
                                then
                                sed -i "s/debug_mode.*/debug_mode = True/" pseudo_config.py
				echo "DEBUG MODE has been set to TRUE"
                                else
                                sed -i "s/debug_mode =.*/debug_mode = False/" pseudo_config.py
				echo "DEBUG MODE has been set to FALSE"
                        fi
	elif [[ "$config_option" == "TV Guide Page" ]]
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
		echo "Setting these options will run a simple http webserver"
		echo "to display the daily schedule in any web browser with"
		echo "network access to the device. If you decline to set the"
		echo "IP address and port number, you will still have the option"
		echo "to set the page title for if you decide to run your own"
		echo "webserver and symlink the html files into the appropriate"
		echo "directory."
		echo "NOTE: This option must be set individually per channel and"
		echo "each channel must have a unique port number."
                echo "Use Simple http Webserver?"
                        read -p 'Y/N: ' use_webserver
                        if [[ "$use_webserver" != @(Y|y|Yes|yes|YES|N|n|No|no|NO) ]]
                                then
                                echo "Use Simple http Webserver?"
                                read -p 'Y/N: ' use_webserver
                        fi
                        if [[ "$use_webserver" = @(Y|y|Yes|yes|YES) ]]
                                then
				local_ip=$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')
				echo "Your IP address is $local_ip"
				sed -i "s/controllerServerPath =.*/controllerServerPath = \"$local_ip\"/" pseudo_config.py
				echo "Enter the PORT NUMBER to use with THIS CHANNEL"
				read -p 'Port Number: ' port_number
				sed -i "s/controllerServerPort =.*/controllerServerPort = \"$port_number\"/" pseudo_config.py
				echo "Set the CHANNEL TITLE for the SCHEDULE PAGE"
				read -p 'Channel Title: ' channel_name
				sed -i "s/htmlPseudoTitle =.*/htmlPseudoTitle = \"$channel_name\"/" pseudo_config.py
				echo "$channel_name's daily schedule will be accessible at http://$local_ip:$port_number"
				echo "To access this page from OUTSIDE your LOCAL NETWORK, add a port forward rule in"
				echo "your router for $port_number to $local_ip."
				else
				sed -i "s/controllerServerPath =.*/controllerServerPath = \"\"/" pseudo_config.py
				sed -i "s/controllerServerPort =.*/controllerServerPort = \"\"/" pseudo_config.py
				echo "Set the CHANNEL TITLE for the SCHEDULE PAGE"
				read -p 'Channel Title: ' channel_name
				sed -i "s/htmlPseudoTitle =.*/htmlPseudoTitle = \"$channel_name\"/" pseudo_config.py
				echo "CHANNEL TITLE set to $channel_name"
			fi
	elif [[ "$config_option" == "Commercial Padding" ]]
		then
		clear
		echo "++++++++++++++++++++PSEUDO CHANNEL CONFIG EDITOR++++++++++++++++++++"
		echo "The COMMERCIAL PADDING value is the number of seconds in"
		echo "between the end of a commercial, movie or show and the"
		echo "start of the next. This accounts for lag in starting"
		echo "the previous item by allowing time for it to end before"
		echo "the next one starts."
		echo "Set the COMMERCIAL PADDING value (in SECONDS)"
		read -p 'Commercial Padding: ' commercial_padding
		if ! [[ $commercial_padding =~ $re ]]
			then
			echo "Set the COMMERCIAL PADDING value (in SECONDS)"
                        read -p 'Commercial Padding: ' commercial_padding
		fi
		sed -i "s/commercialPadding =.*/commercialPadding = $commercial_padding/" pseudo_config.py

	elif [[ "$config_option" == "Back" ]]
		then
		echo "Going BACK to MAIN MENU"
		sleep 1
fi
done
