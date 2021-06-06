wlan = network.WLAN(network.STA_IF) # create station interface
wlan.active(True)       # activate the interface
wlan.connect('Everyone', 'Hastheir0wn') # connect to an AP
wlan.ifconfig()         # get the interface's IP/netmask/gw/DNS addresses
      22 shell.py
#wlan = network.WLAN(network.STA_IF) # create station interface
#wlan.active(True)       # activate the interface
#wlan.scan()             # scan for access points
#wlan.isconnected()      # check if the station is connected to an AP
#wlan.connect('Everyone', 'Hastheir0wn') # connect to an AP
#wlan.config('mac')      # get the interface's MAC adddress
#wlan.ifconfig()         # get the interface's IP/netmask/gw/DNS addresses
