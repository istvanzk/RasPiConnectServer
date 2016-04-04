#!/usr/local/bin/python3
# Filename: ExecuteServerStatus.py
# Version 2.7 07/29/13 RV MiloCreek
# Version 3.0 04.04.2016 IzK (Python3.4+)

import Config

import subprocess
import xml.etree.ElementTree as ET

import Validate
import BuildResponse

import time

if (Config.i2c_demo()):
	from pyblinkm import BlinkM, Scripts


def Execute_Server_Status(root):

	# find the interface object type

	objectServerID = root.find("./OBJECTSERVERID").text
	objectFlags = root.find("./OBJECTFLAGS").text

	validate = Validate.checkForValidate(root)

	if (Config.debug()):
		print("VALIDATE=%s" % validate)

	outgoingXMLData = BuildResponse.buildHeader(root)


	if (Config.debug()):
		print("objectServerID = %s" % objectServerID)

	# we have the objectServerID so now we can choose the correct
	# program



	if (objectServerID == "SS-1"):

		#check for validate request
		if (validate == "YES"):
			outgoingXMLData += Validate.buildValidateResponse("YES")
			outgoingXMLData += BuildResponse.buildFooter()

			return outgoingXMLData




		responseData = "2"


		outgoingXMLData += BuildResponse.buildResponse(responseData)


	else:

		# invalid RaspiConnect Code
		outgoingXMLData += Validate.buildValidateResponse("NO")


	outgoingXMLData += BuildResponse.buildFooter()
	if (Config.debug()):
		print(outgoingXMLData)

	return outgoingXMLData


# End of ExecuteServerStatus.py
				
