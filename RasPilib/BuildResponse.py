#!/usr/local/bin/python3
# Filename: BuildResponse.py
# Version 1.0 03/17/13 RV MiloCreek
# Version 2.0 04.04.2016 IzK (Python3.4)

import xml.etree.ElementTree as ET
import Config

def buildHeader(root):


	objectServerID = root.find("./OBJECTSERVERID").text
	objectID = root.find("./OBJECTID").text
	objectType = root.find("./OBJECTTYPE").text
	objectFlags = root.find("./OBJECTFLAGS").text
	
	if (Config.debug()):
		print(("objectServerID = %s" % objectServerID))
	
	header ="<XMLCOMMAND><OBJECTID>"
	header += objectID

	header +="</OBJECTID><OBJECTSERVERID>"

	header += objectServerID

	header += "</OBJECTSERVERID><OBJECTTYPE>"
	header += objectType
	header += "</OBJECTTYPE>"

	header += "<OBJECTFLAGS>"
	header += objectFlags
	header += "</OBJECTFLAGS>"
	
	header += "<RASPICONNECTSERVERVERSIONNUMBER>"
	header += Config.version_number().decode('utf-8')
	header += "</RASPICONNECTSERVERVERSIONNUMBER>"

	return header 



def buildResponse(response):
	responseData = "<RESPONSE>"
	responseData +="<![CDATA["
	responseData += response
	responseData += "]]>"	
	responseData += "</RESPONSE>"

	return responseData

def buildFooter():
	footerData ="</XMLCOMMAND>"

	return footerData




# End of Buildresponse.py
				
