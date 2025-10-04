### This is a python interface to manage openvpn using cyberghost under linux. ###

Actually, the "official" cyberghostvpn script does not work properly under ubuntu >22.04. 
This GUI code correct that and will manage openvpn connection directly.

### Configuration ###
To use is you need to :
- install the cyberghostvpn official script from https://my.cyberghostvpn.com/download-hub/desktop/add-linux. It has to be installed as root.
- If you want to be able to connect the VPN as a user you need to :
  - copy the config.ini from /home/root/.cyberghost/config.ini to your /home/<user>/.cyberghost/ (this is needed to be able to retreive the list of servers)
  - Add setcap to openvpn to run as non root user with : 
      sudo setcap CAP_NET_ADMIN=ep /usr/sbin/openvpn
  - create a /home/<user>/.cyberghost/auth file containing user on first line and passwd on second line (these are the token and secret from the config.ini)

### Usage ###
Just run : python3 cyberghost_gui.py
Select a country, then a town, then a server and connect.
To close the connection just click stop

### Credits ###
I was initially inspired by https://github.com/zbabac/cyberghost-ubuntu-fix 

### Screenshots ###
![Screenshot 1](https://raw.githubusercontent.com/ifleg/cyberghost/refs/heads/main/screenshots/screenshot1.png "Screeshot 1")
![Screenshot 2](https://raw.githubusercontent.com/ifleg/cyberghost/refs/heads/main/screenshots/screenshot1.png "Screeshot 2")

