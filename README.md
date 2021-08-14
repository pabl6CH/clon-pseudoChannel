# PseudoChannel.py - Your Home-Brewed TV Channels

![Generated HTML schedule](https://i.imgur.com/3NoZVBJ.jpg)

## How to Use:
- Pseudo Channel is a script that interfaces with the Plex API, it runs independently of both server and client. Current supported clients are those that show on in the plex API clients page (http://<your-plex-ip-and-port>/clients?X-Plex-Token=<your-plex-token>). Pseudo Channel is capable of managing schedules for multiple channels. When a channel is activated, Pseudo Channel directs Plex, through the API, to play movies and shows according to a schedule. The script also supports filling time between media with any libraries defined as 'commercials'. The ![web interface](https://github.com/FakeTV/Web-Interface-for-Pseudo-Channel) allows for easy 

0. Update:

```bash
% sudo apt update
```

1. Install python-pip & Git:

```bash
% sudo apt install python-pip git -y
```

2. Create "/channels" dir, change to that directory, and download the install.sh script to the new directory:

```bash
% mkdir ./channels && cd ./channels && wget https://raw.githubusercontent.com/FakeTV/pseudo-channel/master/main-dir/install.sh .
```

3. Make the "install.sh" executable:

```bash
% chmod +x ./install.sh
```

4. Run the install and follow the prompts:

```bash
% ./install.sh
```

You need to have your Plex server IP and [Plex Token](https://bit.ly/2p7RtOu) handy as the install script will ask for them. If you run into issues or want to know more about customizing/configuring PseudoChannel, check out the wiki for details. If you need further help, have some ideas or just want to chat all things FakeTV, visit our FakeTV Discord chat here: https://discord.gg/7equn68
