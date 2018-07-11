#!/bin/bash

# Function will call stop-all-channels.sh on ALL current boxes. 
# The purpose of this falls mainly to a kind of soft "reset", as well as for channel updating.

CHANNEL_DIR_INCREMENT_SYMBOL="_"
MASTERDIRECTORY="channels"


cd ..
BOX_DIR_ARR=( $(find . -maxdepth 1 -type d -name 'channels'"$CHANNEL_DIR_INCREMENT_SYMBOL"'*' -printf "%P\n" | sort -t"$CHANNEL_DIR_INCREMENT_SYMBOL" -n) )
BOX_DIR_ARR+=("${MASTERDIRECTORY}")
echo "+++++ FOUND THE FOLLOWING BOXES: ${BOX_DIR_ARR[@]}"


for BOX in "${BOX_DIR_ARR[@]}"
do
	cd ${BOX}
	echo "+++++ CURRENTLY STOPPING ${BOX}"

	sudo ./stop-all-channels.sh 

	cd ..
done

