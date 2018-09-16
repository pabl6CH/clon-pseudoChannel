#!/bin/bash
# file: update-channels-from-git.sh

#----
# Simple script to update every channel with updates from the github repo. 
# BACKUP EACH XML/DB IN EACH CHANNEL.
# Code will take in one argument: To take from the master or development branch
# For ALL installs, simply place this file in the location you would like your channels to be installed/updated
#----

#---- 
# To Use:
# chmod +x update-channels-from-git.sh
# ./update-channels-from-git.sh
#----

#----BEGIN EDITABLE VARS----

if [ $# -gt 1 ]; then
	echo "ERROR: Please only supply one argument"
	exit 9999
elif [ "$1" == "develop" ]; then
	echo "Downloading the develop branch"
	SCRIPT_TO_EXECUTE_PLUS_ARGS='git clone https://github.com/mutto233/pseudo-channel . --branch develop'

else
	echo "Downloading the master branch"
	SCRIPT_TO_EXECUTE_PLUS_ARGS='git clone https://github.com/mutto233/pseudo-channel . --branch master'
fi

OUTPUT_PREV_CHANNEL_PATH=.

CHANNEL_DIR_INCREMENT_SYMBOL="_"

FIRST_INSTALL=false

#----END EDITABLE VARS-------



# First, we need to figure out if we have actually installed this already
# To do this, we are going to check if we go up one level we have the folder "channels"
# We will also check if the current directory has "channels"
# FIRST_INSTALL=true

# if [ -d "$INSTALL_FOLDER" ] || [ -d "../$INSTALL_FOLDER" ]; then
	# echo "This is NOT the first install"
	# FIRST_INSTALL=false
# else
	# echo "This IS the first install, installing 'channels' directory in current directory with five starting channels."
	# FIRST_INSTALL=true
# fi


# If this is our first install, we will now make all necessary directories to prepare for install
if [ "$FIRST_INSTALL" == "true" ]; then

	for (( num=1; num<=5; num++ ))
	do
		mkdir "pseudo-channel_$num"
	done
fi


#### Next, let's download the latest master version of information from GitHub and store it in a temporary folder
mkdir github_download
cd github_download
$SCRIPT_TO_EXECUTE_PLUS_ARGS

#### If necessary, install the required elements as defined by requirements.txt
if [ "$FIRST_INSTALL" == "true" ]; then
	echo "INSTALLING REQUIREMENTS because this is a FIRST RUN"
	sudo pip install -r requirements.txt
fi

cd ..


#### With information downloaded, we will first go to each channel folder and update important things
#### This will take the following form
#### - Enter folder
#### - Copy database, xml, and config file to temporary folder
#### - copy all files from the download/channel-dir and download/both-dir to the channel folder.
#### - Replace files that were originally removed

# Scan the dir to see how many channels there are, store them in an arr.
CHANNEL_DIR_ARR=( $(find . -maxdepth 1 -type d -name '*'"$CHANNEL_DIR_INCREMENT_SYMBOL"'[[:digit:]]*' -printf "%P\n" | sort -t"$CHANNEL_DIR_INCREMENT_SYMBOL" -n) )

if [ "${#CHANNEL_DIR_ARR[@]}" -gt 1 ]; then
	echo "+++++ There are ${#CHANNEL_DIR_ARR[@]} channels detected."
	for channel in "${CHANNEL_DIR_ARR[@]}"
	do
		echo "+++++ Trying to update channel:"./"$channel"
		cd "$channel"
		
		# Export critical files
		mkdir ../.pseudo-temp
		
		cp ./pseudo-channel.db ../.pseudo-temp 2>/dev/null

		cp ./pseudo_schedule.xml ../.pseudo-temp 2>/dev/null

		cp ./pseudo_config.py ../.pseudo-temp 2>/dev/null
		
		# Copy new elements
		
		cp -r ../github_download/channel-dir/* .
		cp -r ../github_download/both-dir/* .
		
		# Replace the files originally moved
		
		cp ../.pseudo-temp/pseudo-channel.db . 2>/dev/null

		cp ../.pseudo-temp/pseudo_schedule.xml . 2>/dev/null
 
		cp ../.pseudo-temp/pseudo_config.py . 2>/dev/null
		
		rm -rf ../.pseudo-temp
		
		cd ..
	done
fi

#### Now we will return to the original file, and ensure that everything is in the main folder
#### This will include the following form
#### - Return to folder
#### - Copy config, db, and tolken file
#### - Copy relevant files from github
#### - Replace files originally removed
echo "Updating channels folder"

# Export critical files
mkdir .pseudo-temp

cp ./pseudo-channel.db .pseudo-temp 2>/dev/null

cp ./pseudo_config.py .pseudo-temp 2>/dev/null

cp ./plex_token.py .pseudo-temp 2>/dev/null

# Copy new elements

cp -r ./github_download/main-dir/* .
cp -r ./github_download/both-dir/* .

# Replace the files originally moved

cp ./.pseudo-temp/pseudo-channel.db . 2>/dev/null

cp ./.pseudo-temp/pseudo_config.py . 2>/dev/null

cp ./.pseudo-temp/plex_token.py  . 2>/dev/null

rm -rf ./.pseudo-temp

rm -rf ./github_download

#### Change permissions to 777 for all files, so that things will run
sudo chmod -R 777 .

echo "Update Complete"
