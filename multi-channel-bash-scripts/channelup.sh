#!/bin/bash

# file: channelup.sh

#----
# Simple script to cycle through multiple pseudo-channel instances - triggering start / stop.
#----

#---- 
# To Use:
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
# --channelup.sh <--- on the same level as the 3 channels. 
#----

# Make sure that each channel dir ends with a "_" + an incrementing number as seen above.

#----BEGIN EDITABLE VARS----

SCRIPT_TO_EXECUTE='startstop.sh'

OUTPUT_PREV_CHANNEL_PATH=.

OUTPUT_PREV_CHANNEL_FILE=".prevplaying"

CHANNEL_DIR_INCREMENT_SYMBOL="_"

#----END EDITABLE VARS-------

FIRST_RUN=false

# If the previous channel txt file doesn't exist already create it (first run?)
if [ ! -e "$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE" ]; then

	echo 1 > "$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE"

	FIRST_RUN=true

fi

# If the file exists b

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

# If this script see's there are multiple channels, 
# then read file, get prevchannel, increment, and trigger next channel:
if [ "${#CHANNEL_DIR_ARR[@]}" -gt 1 ]; then

	#NEXT_CHANNEL=""

	PREV_CHANNEL_FOUND=false

	#PREV_CHANNEL_DIR=""

	echo "+++++ There are ${#CHANNEL_DIR_ARR[@]} channels detected."

	#PREV_CHANNEL=$(<$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE)

	# We are now going to do the same thing here, just with previous channel
	PREV_CHANNEL=$(echo $(<$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE) | sed "s/^0*//")	
	if [ -z $PREV_CHANNEL ]; then
	PREV_CHANNEL=0
	fi
	
	echo "+++++ It looks like the previous channel was: $PREV_CHANNEL"


	# This is our modified way of searching for the correct directory for the previous channel
	for i in "${!CHANNEL_DIR_NUMBERS[@]}"
	do
		item_compare=${CHANNEL_DIR_NUMBERS[i]}
		if [ $item_compare -eq $PREV_CHANNEL ]; then
			echo "PREVIOUS CHANNEL MATCH: ${CHANNEL_DIR_SORTED[$i]}"
			PREV_CHANNEL_DIR=${CHANNEL_DIR_SORTED[$i]}
			if [ $((i+1)) -gt $((${#CHANNEL_DIR_SORTED[@]}-1)) ]; then
				NEXT_CHANNEL=${CHANNEL_DIR_SORTED[0]}
			else
				NEXT_CHANNEL=${CHANNEL_DIR_SORTED[$((i+1))]}
			fi
			break
		fi
	done

	echo "+++++ The next channel is: $NEXT_CHANNEL"

	# Write next channel to previous channel file to reference later
	echo "$NEXT_CHANNEL" | cut -d "_" -f2  > "$OUTPUT_PREV_CHANNEL_PATH/$OUTPUT_PREV_CHANNEL_FILE"

	# Finally let's trigger the startstop script in both the previous channel and the next channel dirs.
	# This will stop the previous channels playback & trigger the next channels playback

	if [ "$FIRST_RUN" = false ]; then
		cd "$OUTPUT_PREV_CHANNEL_PATH"/"$PREV_CHANNEL_DIR" && ./"$SCRIPT_TO_EXECUTE"
		cd ../"$NEXT_CHANNEL" && ./"$SCRIPT_TO_EXECUTE"
	else

		cd "$OUTPUT_PREV_CHANNEL_PATH"/"$NEXT_CHANNEL" && ./"$SCRIPT_TO_EXECUTE"

	fi

	sleep 1
	

fi

exit 0