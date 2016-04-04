#!/usr/local/bin/python3
# Filename: Validate.py
# Version 1.0 03/17/13 RV MiloCreek
# Version 3.0 04.04.2016 IzK (Python3.4+)

import xml.etree.ElementTree as ET


def checkForValidate(root):


	validateFound = root.find("./VALIDATE")

	if (validateFound == None):
		validate="NO"
	else:
		validate = root.find("./VALIDATE").text

	return validate 



def buildValidateResponse(response):
	
	responseData = "<RESPONSE>"
	responseData +="<![CDATA["

	if (response == "YES"):
		responseData += "VALIDATED";
	else:
		responseData += "INVALID RASPICONNECT CODE";	

	responseData += "]]>"	
	responseData += "</RESPONSE>"


	return responseData



# End of Validate.py
				
