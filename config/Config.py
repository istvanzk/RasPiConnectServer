#!/usr/local/bin/python3.4
# Filename: Config.py
# Version 2.9 09/07/13 BP MiloCreek
# Version 1.0 04.04.2016 IzK (Python3.4)

# set to True if you wish to see debugging output from the server otherwise False
DEBUG = False

#WEB_SERVER_PORT is the port that the RasPiConnect Webserver will be responding to requests from the RasPiConnect App
WEB_SERVER_PORT = 9696

#LOCALURL is the address of your pi. If you poke a hole through your firewall and expose it to the Internet, insert that address here 
#Usually, the port in the URL (9600) will match the WEB_SERVER_PORT above but can be remapped in most routers/firewalls
# Note that the address for your SystemURL in the RasPiConnectApp should be of the form:  http://192.168.1.120:9600/raspi (see manual for more information)
LOCALURL = "192.168.87.110"

#USERNAME is the username that you have entered in the RasPiConnect App.  It must match and is case sensitive
USERNAME = "RPiC"

#PASSWORD is the password that you have entered in the RasPiConnect App.  It must match and is case sensitive
PASSWORD = "pic"

# set to True if you have an I2C bus set up and has an AdaFruit BMP085 and two BlinkM modules (addresses 0xC and 0xB) False if not
I2CDEMO = False 

#RASPICONNECTSERVER Version Number.  Do not change!
VERSIONNUMBER = "3.2"

def hostAddr():
	return LOCALURL.encode('utf-8') 
	
def localURL():
	return ("%s/%d" % (LOCALURL, WEB_SERVER_PORT)).encode('utf-8')

def password():
	return PASSWORD.encode('utf-8')

def username():
	return USERNAME.encode('utf-8') 

def web_server_port():
	return WEB_SERVER_PORT

def version_number():
	return VERSIONNUMBER.encode('utf-8')

def debug():
	return DEBUG;

def i2c_demo():
	return I2CDEMO;

