# PseudoChannel.py - Your Home-Brewed TV Channels

![Generated HTML schedule](https://i.imgur.com/CUgxb1W.gif)

## How to Use:

- The instructions below are all for configuring the **"controller"** device (i.e. a laptop or raspberry pi running linux). This is the device this app runs on to control the Plex client. The **"client"** device should be a Raspberry Pi running Rasplex hooked up to your TV via HDMI - although I'm sure other clients work great too. 

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
% ./install.sh develop
```

You need to have your Plex server IP and [Plex Token](https://bit.ly/2p7RtOu) handy as the install script will ask for them. If you run into issues or want to know more about customizing/configuring PseudoChannel, check out the wiki for details. If you need further help, have some ideas or just want to chat all things FakeTV, visit our FakeTV Discord chat here: https://discord.gg/7equn68
