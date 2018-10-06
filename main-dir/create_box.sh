#!/bin/bash

# Purpose of the script is to copy the current "master" channel database and create a new set for a named box
# As the input, simply give the name of a client, this will be appended in the form "channels_<NAME>"

# Flow of the script
# - Go out of directory, and make a new directory
# - Copy from the master folder to this folder
# - Find all channels, go in and remove .db, symlink to the original (running with -sf)

CHANNEL_DIR_INCREMENT_SYMBOL="_"

MASTERDIRECTORY="channels"

NEWDIRECTORY="${MASTERDIRECTORY}_${1}"

# CREATE THE NEW DIRECTORY
cd ..

if [ -d "$NEWDIRECTORY" ]; then
	sudo rm -R ${NEWDIRECTORY}
fi
mkdir $NEWDIRECTORY


# COPY THE ELEMENTS INTO HERE, THEN SET CORRECT PROPERTIES 
sudo cp -r ./${MASTERDIRECTORY}/* ./${NEWDIRECTORY}/
sudo chmod -R 777 ./${NEWDIRECTORY}


# GO INTO EACH CHANNEL, DELETE THE .db FILE, AND SYMLINK TO THE ORIGINAL
cd ${NEWDIRECTORY}
CHANNEL_DIR_ARR=( $(find . -maxdepth 1 -type d -name '*'"$CHANNEL_DIR_INCREMENT_SYMBOL"'[[:digit:]]*' -printf "%P\n" | sort -t"$CHANNEL_DIR_INCREMENT_SYMBOL" -n) )


if [ "${#CHANNEL_DIR_ARR[@]}" -gt 1 ]; then
	
	echo "+++++ There are ${#CHANNEL_DIR_ARR[@]} channels detected."
	
	for i in "${!CHANNEL_DIR_ARR[@]}"
	do
		echo "+++++ Linking Directories in ${CHANNEL_DIR_ARR[i]}"
		cd ${CHANNEL_DIR_ARR[i]}
		MASTER_CHANNEL="../../${MASTERDIRECTORY}/${CHANNEL_DIR_ARR[i]}"

		ln -sf "${MASTER_CHANNEL}/pseudo-channel.db"

		cd ..
	done
fi



