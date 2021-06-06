# micropython
  my micropython tools and toys
  
  #### Assuming FW loaded as in:
    http://docs.micropython.org/en/v1.15/esp8266/tutorial/intro.html

## COM4 Quick Notes Example

  ### Test micropython connection:

    esptool --port COM4 chip_id
    
  ### REPL

    http://docs.micropython.org/en/v1.15/esp8266/tutorial/repl.html
  
  #### Start PUTTY serial console:

    COM4 115200
    Use about 40 rows

  #### wlan.ifconfig()

    assumes webrepl_setup done
    assumes micropython/boot.py
    assumes micropython/main.py
    
  #### Webrepl Connection (IP 10.0.0.178 station mode)

    http://micropython.org/webrepl/#10.0.0.178:8266/

