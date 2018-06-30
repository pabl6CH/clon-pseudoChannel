#!/bin/bash

# Credits: irodimus 

# file: manual.sh

#----
# Simple script to change to specific channel given - triggering start / stop. 
#----

#---- 
# To Use:
# Run script by including the channel you'd like to run as an argument: ex. ./manual.sh 2, ./manual.sh 9
#
# Configure something (a tv remote or alexa) to trigger this script. Make sure you move this script just 
# outside of the pseudo-channel directories:
# -------------------
# -channels/
# --pseudo-channel_1/
# ---startstop.sh
# --pseudo-channel_2/
# ---startstop.sh
# --pseudo-channel_3/
# ---startstop.sh
# --manual.sh <--- on the same level as the 3 channels. 
#----

# Make sure that each channel dir ends with a "_" + an incrementing number as seen above.

#----BEGIN EDITABLE VARS----

SCRIPT_TO_EXECUTE='startstop.sh'

OUTPUT_PREV_CHANNEL_PATH=.

OUTPUT_PREV_CHANNEL_FILE=".prevplaying"

CHANNEL_DIR_INCREMENT_SYMBOL="_"

#----END EDITABLE VARS-------

FIRST_RUN=false

# Scan the dir to see how many channels there are, store them in an arr.
CHANNEL_DIR_ARR=( $(find . -maxdepth 1 -type d -name '*'"$CHANNEL_DIR_INCREMENT_SYMBOL"'[[:digit:]]*' -printf "%P\n" | sort -t"$CHANNEL_DIR_INCREMENT_SYMBOL" -n) )

# Since leading zeros may be an issue, we need to correctly sort the channels.  The best way to do this seems to be in python
# So a script will take in the channels as they are, then output them in the correct, sorted order in Channels_Sorted.txt.
# We will run the script, then read in the results.
sudo python ./Channel_Sorter.py ${CHANNEL_DIR_ARR[@]}

filename="./Channels_Sorted.txt"
i=0
while read -r line
do
	name="$line"
	CHANNEL_DIR_SORTED[i]=$name
	i=$((i+1))
done < "$filename"


# We need to add on top of this a "buffer" where we remove all leading zeros to compare everything on the same level
# This simply leaves us with the number at the end.  NOTE: We should have already sorted things, so this should not be a problem
for i in "${!CHANNEL_DIR_ARR[@]}"
do
	CHANNEL_DIR_NUMBERS[i]=$(echo ${CHANNEL_DIR_SORTED[i]} | sed "s/^pseudo-channel${CHANNEL_DIR_INCREMENT_SYMBOL}0*//")
	if [ -z ${CHANNEL_DIR_NUMBERS[i]} ]; then
		CHANNEL_DIR_NUMBERS[i]=0
	fi
done





# If the previous channel txt file doesn't exist already create it (first run?)
if [ ! -e "$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE" ]; then

	#FIRST_RUN_NUM=$((${#CHANNEL_DIR_ARR[@]}))
	echo 1 > "$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE"

	echo "First run being conducted"

	FIRST_RUN=true

fi

# If this script see's there are multiple channels, 
# then read file, get prevchannel and nextchannel, and trigger next channel:
if [ "${#CHANNEL_DIR_ARR[@]}" -gt 1 ]; then
	echo "+++++ There are ${#CHANNEL_DIR_ARR[@]} channels detected."

	#NEXT_CHANNEL=$1

	#NEXT_CHANNEL_DIR=( $(find . -maxdepth 1 -type d -name '*'"$CHANNEL_DIR_INCREMENT_SYMBOL""$NEXT_CHANNEL" -printf "%P\n") )
	
	# We now need to read in the next channel and ALSO strip it of any leading zeros for correct comparison
	NEXT_CHANNEL=$(echo $1 | sed "s/^0*//")

	if [ -z $NEXT_CHANNEL ]; then
	NEXT_CHANNEL=0
	fi
	
	PREV_CHANNEL_FOUND=false

	#PREV_CHANNEL=$(<$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE)

	# PREV_CHANNEL_DIR=( $(find . -maxdepth 1 -type d -name '*'"$CHANNEL_DIR_INCREMENT_SYMBOL""$PREV_CHANNEL" -printf "%P\n") )

	# We are now going to do the same thing here, just with previous channel
	PREV_CHANNEL=$(echo $(<$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE) | sed "s/^0*//")
	if [ -z $PREV_CHANNEL ]; then
	PREV_CHANNEL=0
	fi

	
	echo "+++++ It looks like the previous channel was: $PREV_CHANNEL"

	echo "+++++ The next channel is: $NEXT_CHANNEL"

	# This is our modified way of searching for the correct directory for the next channel
	for i in "${!CHANNEL_DIR_NUMBERS[@]}"
	do
		item_compare=${CHANNEL_DIR_NUMBERS[i]}
		if [ $item_compare -eq $NEXT_CHANNEL ]; then
			echo "NEXT CHANNEL MATCH: ${CHANNEL_DIR_SORTED[$i]}"
			NEXT_CHANNEL_DIR=${CHANNEL_DIR_SORTED[$i]}
			break
		fi

		#echo "TESTING"
		#echo $i
		#echo ${#CHANNEL_DIR_NUMBERS[@]}
		if [ $i -eq $((${#CHANNEL_DIR_NUMBERS[@]} - 1)) ]; then
			echo "No NEXT CHANNEL MATCH found, reverting to first element"
			NEXT_CHANNEL_DIR=${CHANNEL_DIR_SORTED[0]}
			NEXT_CHANNEL=${CHANNEL_DIR_NUMBERS[0]}
		fi

	done
	
	# This is our modified way of searching for the correct directory for the previous channel
	for i in "${!CHANNEL_DIR_NUMBERS[@]}"
	do
		item_compare=${CHANNEL_DIR_NUMBERS[i]}
		if [ $item_compare -eq $PREV_CHANNEL ]; then
			echo "PREVIOUS CHANNEL MATCH: ${CHANNEL_DIR_SORTED[$i]}"
			PREV_CHANNEL_DIR=${CHANNEL_DIR_SORTED[$i]}
			break
		fi
	done

	
	# Write next channel to previous channel file to reference later
	echo "$NEXT_CHANNEL"  > "$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE"

	# Finally let's trigger the startstop script in both the previous channel and the next channel dirs.
	# This will stop the previous channels playback & trigger the next channels playback

	if [ "$FIRST_RUN" = false ]; then
		cd "$OUTPUT_PREV_CHANNEL_PATH"/"$PREV_CHANNEL_DIR" && ./"$SCRIPT_TO_EXECUTE"
		cd ../"$NEXT_CHANNEL_DIR" && ./"$SCRIPT_TO_EXECUTE"
	else

		cd "$OUTPUT_PREV_CHANNEL_PATH"/"$NEXT_CHANNEL_DIR" && ./"$SCRIPT_TO_EXECUTE"

	fi

	sleep 1
	

fi

exit 0