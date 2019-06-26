#!/bin/bash

# Purpose of this script is to update ALL boxes with the most current version of the script.

# Flow of the script
# Go to home directory, identify ALL boxes that need updating
# Run "update-channels-from-git.sh" in all of them.
# System link all databases when complete 
CHANNEL_DIR_INCREMENT_SYMBOL="_"
MASTERDIRECTORY="channels"
BRANCH="develop"


cd ..
BOX_DIR_ARR=( $(find . -maxdepth 1 -type d -name 'channels'"$CHANNEL_DIR_INCREMENT_SYMBOL"'*' -printf "%P\n" | sort -t"$CHANNEL_DIR_INCREMENT_SYMBOL" -n) )
BOX_DIR_ARR+=("${MASTERDIRECTORY}")
echo "+++++ FOUND THE FOLLOWING BOXES: ${BOX_DIR_ARR[@]}"

for BOX in "${BOX_DIR_ARR[@]}"
do
	cd ${BOX}
	echo "+++++ CURRENTLY UPDATING ${BOX}"
	# Sanity check, can we even update?
	if [ ! -e "update-channels-from-git.sh" ]; then
		echo "ERROR AT ${BOX}: No file to update with!"
		exit 75
	fi

	# Update the given box with the gitHub repository branch selected.
	bash ./update-channels-from-git.sh ${BRANCH}

	# Now we need to go in and perform the symlink again
	CHANNEL_DIR_ARR=( $(find . -maxdepth 1 -type d -name '*'"$CHANNEL_DIR_INCREMENT_SYMBOL"'[[:digit:]]*' -printf "%P\n" | sort -t"$CHANNEL_DIR_INCREMENT_SYMBOL" -n) )
	if [ "${#CHANNEL_DIR_ARR[@]}" -gt 1 ]; then
	
		echo "+++++ There are ${#CHANNEL_DIR_ARR[@]} channels detected."
		if [ ! "${BOX}" == "${MASTERDIRECTORY}" ]; then
			echo "+++++ symlinking channels in ${BOX}"
			for i in "${!CHANNEL_DIR_ARR[@]}"
			do
				echo "+++++ Linking Directories in ${CHANNEL_DIR_ARR[i]}"
				cd ${CHANNEL_DIR_ARR[i]}
				MASTER_CHANNEL="../../${MASTERDIRECTORY}/${CHANNEL_DIR_ARR[i]}"
			
				ln -sf "${MASTER_CHANNEL}/pseudo-channel.db"
			
				cd ..
			done
		else
			echo "+++++ NOT symlinking these channels; these are master!!!"

		fi
	fi

	cd ..
done
