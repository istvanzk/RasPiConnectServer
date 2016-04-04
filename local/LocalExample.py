#!/usr/local/bin/python3 
# Filename: local.py 
# MiloCreek BP MiloCreek 
# Version 3.0 6/11/2014 
# Version 3.5 04.04.2016 IzK (Python3.4+)
# 
# Local Execute Objects for RasPiConnect.
# Uses a dispatcher class to register handlers for the the different objectServerID.
# To add Execute objects, modify this file as follows: 
# - Implement handler function for objectServerID based on the template FFF_func(list_par, bValidate)
# - Add the handler to the dispatcher in AssignObjectServerHandlers() 
#

# System imports
import sys
import subprocess
import os
import time
import collections
from math import exp

# RasPiConnectImports
import Config
import Validate
import BuildResponse 

import RPi.GPIO as GPIO ## Import GPIO library
GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(7, GPIO.OUT) ## Setup GPIO Pin 7 to OUT

# To put an LED on GPIO Pin 7 on your pi read this:
#		http://www.thirdeyevis.com/pi-page-2.php
#

# Local Debug
LocalDEBUG = True

# Information from XML
objectID = 		''
#objectType = 	''
objectName = 	''
objectFlags = 	''
objectAction = 	''

Handler = collections.namedtuple(
    typename='Handler_func',
    field_names=('callback', 'args'))
        
class RasPiDispatcher(object):
	"""
	Class that maps addresses (strings) to handlers (functions).
		Based on Dispatcher class implementation from python-osc 1.5 by attwad
		See: https://pypi.python.org/pypi/python-osc
	"""
	
	def __init__(self, exp_k, avg_lng):
		self.description = dict()

		self._map = collections.defaultdict(list)
		self._default_handler = None
		self._activity = dict()
		self.activity_metric = dict()
		self._prev_activity_metric = dict()
		
		self.exp_k = exp_k or 0.05
		self.avg_lng = avg_lng or 20

	def map(self, address, handler, address_description, *args):
		"""
		Map the given address to the given description of the address (string).
		Map the given address to the given handler (namedtuple).
		Initialize the activity deque for the given handler.
		Initialize the activity metric for the given handler.		
		"""
		
		self.description[address] = "{!s} (f{:d})".format(address_description, args[0])
		
		self._ext_args = list()
		self._ext_args.append( args[0] )
		self._ext_args.append( 'objName' )
		self._ext_args.append( 'objAction' )
		self._map[address].append(Handler(handler, list(self._ext_args)))
				
		self._activity[handler.__name__] = collections.deque([], self.avg_lng)
		self.activity_metric[handler.__name__] = 0
		self._prev_activity_metric[handler.__name__] = 0
		
	def listmap(self):
		"""
		List all registered handlers.
		The default handler is not returned!
		"""
		for addr, handlers in self._map.items():
			print(handlers)
		
	def handlers_for_address(self, address):
		"""
		Find handler(s) for a given address.
		The default handler is returned only if no registered handler(s) are found!		
		"""
	
		matched = False
		for addr, handlers in self._map.items():
			if (addr == address):
				yield from handlers
				matched = True

		if not matched and self._default_handler:
			yield Handler(self._default_handler, [])

	def activity_for_handler(self, handler_func):
		"""
		Update the activity monitor for the handler function.
		The default handler does not have an activity monitor!
		"""
		
		try:
			self._activity[handler_func.__name__].append(time.time())
			dn = (self._activity[handler_func.__name__][-1] - self._activity[handler_func.__name__][-2])
	
			# λ_last ← k + exp( -k*(t_new − t_last) ) * λ_last
			self._prev_activity_metric[handler_func.__name__] = self.exp_k + exp(-self.exp_k*dn) * self._prev_activity_metric[handler_func.__name__]
						
		except KeyError:
			pass

		except IndexError:
			pass
				
	def update_handlers_activity(self):
		"""
		Update/calculate the activity metric for all registered handlers.
		The default handler does not have an activity metric!		
		"""
	
		for addr, handlers in self._map.items():
			for handler in handlers:
				try:
					d0 = time.time() - self._activity[handler.callback.__name__][0]
					dt = time.time() - self._activity[handler.callback.__name__][-1]
					
					da = (self._activity[handler.callback.__name__][-1] - self._activity[handler.callback.__name__][0])/len(self._activity[handler.callback.__name__])/( 1 - exp(-self.exp_k*d0) )
					
					# Method for estimating the rate of occurrence of an event, by Ilmari Karonen
					# http://stackoverflow.com/questions/23615974/estimating-rate-of-occurrence-of-an-event-with-exponential-smoothing-and-irregul
					
					# Without averaging:
					# 	Init: λ_last = 0, t_last = t_0, k = 0.1
					#   At t_new:	λ_last ← k + exp( -k*(t_new − t_last) ) * λ_last
					#				t_last ← t_new
					# 	Estimate: 	λ(t) = exp( -k*(t − t_last) ) * λ_last / ( 1 − exp(-k*(t − t0)) )
					#
					self.activity_metric[handler.callback.__name__] = \
						da * exp(-self.exp_k*dt) * self._prev_activity_metric[handler.callback.__name__]
					
					# With averaging (exponentially decaying average of λ)
					#	Init: λ_last = 0, λ_avg_last = 0, t_last = t_0, k1 = 0.1, k2 = 0.2
					#	At t_new:	W(t_new − t_last) = k2 * ( exp( -k2*(t_new − t_last) ) − exp( -k1*(t_new − t_last) ) ) / (k1 − k2)
					#				λ_avg_last ← W(t_new − t_last) * λ_last + exp( -k2*(t_new − t_last) ) * λ_avg_last
        			#				λ_last ← k1 + exp( -k1*(t_new − t_last) ) * λ_last
        			# 				t_last ← t_new
					#				 
					#	Estimate:	λ(t) = ( W(t − t_last) * λ_last + exp( -k2*(t − t_last)  ) * λ_avg_last ) / (1 - S(t − t0))
					#				S(t − t0) = ( k1*exp( −k2*(t - t0) ) − k2*exp( −k1*(t - t0) ) ) / (k1 − k2) 
					#
									
				except IndexError:
					pass
					
	def get_all_handlers(self):
		"""
		Find all registered handlers.
		The default handler is returned only if no registered handlers are found!
		"""
	
		matched = False
		for addr, handlers in self._map.items():
			yield from handlers
			matched = True

		if not matched and self._default_handler:
			yield Handler(self._default_handler, [])
      
	def set_default_handler(self, handler):
		"""
		Sets the default handler.
		Must be a function with the same constraints as with the self.map method
		or None to unset the default handler.
		"""
		
		self._default_handler = handler
		
def AssignObjectServerHandlers():
	"""
	Builds the dispatcher map: ObjectServerHandlers. 
	Each entry maps an objectServerID (string) to:
		a handler (function), a description string and the handler arguments.
	"""
	
	ObjectServerHandlers.map('mAIL-1', AIL_func, 'Activity indicator LIVE', 1)
	ObjectServerHandlers.map('mWV-1', RWV_func, 'Server info', 1) 
	ObjectServerHandlers.map('mSB-1', SAB_func, 'Simple button', 1)
	
	# default handler for all not registered objectServerIDs
	ObjectServerHandlers.set_default_handler(Default_func)

def UserObjectsInfo():
	"""
	Generate the html view of the registered dispatcher map in ObjectServerHandlers
	"""
	
	responseData = buildHTML("./Templates/info.html")
	responseData += "<h3>Handled <i>objectServerIDs</i></h3>" 

	for objID in ObjectServerHandlers.description:
		responseData += "<p>{:<10}: {}</p>".format(objID, ObjectServerHandlers.description[objID])
		
	return responseData 

def ExecuteUserObjects(objectType, element):

	#
	# Fetch information from XML for use in user elements
	# objectServerID:	Control Code
	# objectType:		Interface constant (*_UITYPE)
	# objectName:		Display Name of Control
	# objectID:			???
	# objectFlags:		???
	# objectAction:		???
	objectServerID = element.find("./OBJECTSERVERID").text
	#objectType = element.find("./OBJECTTYPE").text
	objectName = element.find("./OBJECTNAME").text
	objectID = element.find("./OBJECTID").text
	objectFlags = element.find("./OBJECTFLAGS").text
	objectAction = element.find("./OBJECTACTION").text

	if LocalDEBUG:
		print("=====================================")
		print("objectServerID\t= %s" % objectServerID)
		print("objectType\t= %s" % objectType)
		print("objectName\t= %s" % objectName)
		print("objectID\t= %s" % objectID)
		print("objectFlags\t= %s" % objectFlags)
		print("objectAction\t= %s" % objectAction)

	#
	# Check if this is a Validate request
	#
	validate = Validate.checkForValidate(element)
	bValidate = False
	if (validate == "YES"):
		bValidate = True

	if LocalDEBUG:
		print("VALIDATE\t= %s" % validate)

	#
	# Run handler and get the response; update activity for the handler
	#
	responseData = ""
	handlers = ObjectServerHandlers.handlers_for_address(objectServerID)
	for handler in handlers:
		if len(handler.args) > 0:
			handler.args[1] = objectName
			handler.args[2] = objectAction
			responseData = handler.callback(handler.args, bValidate)
			ObjectServerHandlers.activity_for_handler(handler.callback)

	#
	# Update the activity metric for all handlers
	#
	ObjectServerHandlers.update_handlers_activity()
	
	if LocalDEBUG:
		print("-------------------------------------")
		for addr, handlers in ObjectServerHandlers._map.items():
			for handler in handlers:
				print("{:8s}()\t: {:4.2f}".format(handler.callback.__name__, ObjectServerHandlers.activity_metric[handler.callback.__name__]))

	# Return a zero length string when no match for the objectServerID was found	
	if len(responseData) == 0:
		return ""
	
	#	
	# Build the header
	#
	outgoingXMLData = BuildResponse.buildHeader(element)

	#
	# Build a valid response
	#			
	if responseData == "VALIDATED":
		# Build VALIDATED response 
		outgoingXMLData += Validate.buildValidateResponse("YES")
	
	else:	
		# Build respose 
		outgoingXMLData += BuildResponse.buildResponse(responseData)

	#
	# Build footer
	#	
	outgoingXMLData += BuildResponse.buildFooter()
	#if LocalDEBUG:
	#	print(outgoingXMLData)

	#
	# Return XML response
	#
	return outgoingXMLData


def AIL_func(list_par, bValidate):
	"""AIL Activity indicator LIVE"""
			
	if bValidate: 
		return "VALIDATED"
	
	sendOSC("/ail", 1)	
	return "YES"	
	
def RWV_func(list_par, bValidate):
	"""HTML page (from template)"""
	
	if bValidate: 
		return "VALIDATED"

	responseData = ""
	
	# Server info page
	if list_par[0] == 1:

		# check to see if i2c_demo is turned on
		if (Config.i2c_demo()):
			if (LocalDEBUG()):
				print("Config.i2c_demo passed as True")

			# Yes, it is on

			# Initialise the BMP085 and use STANDARD mode (default value)
			# bmp = BMP085(0x77, debug=True)
			# bmp = BMP085(0x77)

			# To specify a different operating mode, uncomment one of the following:
			# bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
			# bmp = BMP085(0x77, 1)  # STANDARD Mode
			# bmp = BMP085(0x77, 2)  # HIRES Mode
			bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode

			count = 0
			exceptionCount = 0
			exceptionCountBMP = 0
			blinkm = BlinkM(1,0xc)
			blinkm.reset()

			try:
				temp = bmp.readTemperature()
				pressure = bmp.readPressure()
				altitude = bmp.readAltitude()

				tempData = "%.2f C" % temp
				pressureData = "%.2f hPa" % (pressure / 100.0)

			except IOError as e:
				exceptionCountBMP = exceptionCountBMP + 1
				print("I/O error({0}): {1}".format(e.errno, e.strerror))
			except:
				exceptionCountBMP = exceptionCountBMP + 1
				print("Unexpected error:", sys.exc_info()[0])
				raise

		else:    # now set some values for display since we don't have i2C
			tempData = "xx.x C (no i2c enabled)"
			pressureData = "xxxx.x hPa (no i2c enabled)"

		# read latest data from ST-1 SendText control on RasPiConnect
		try:
			with open ("./local/ST-1.txt", "r") as myfile:
				sendTextData = myfile.read().replace('\n', '')
		except IOError:
			sendTextData = ""

		# check to see if i2c_demo is turned on
		if (Config.i2c_demo()):

			time.sleep(0.2)

			try:

				blinkm.go_to(255, 0, 0)
				time.sleep(0.2)
				blinkm.go_to(0, 255, 0)


			except IOError as e:
				#blinkm.reset()
				exceptionCount = exceptionCount + 1
				print("I/O error({0}): {1}".format(e.errno, e.strerror))
			except:
				blinkm.reset()
				exceptionCount = exceptionCount + 1
				print("Unexpected error:", sys.exc_info()[0])
				raise


		#
		# the html file with system info (from a template)
		#
		responseData = buildHTML("./Templates/W-1.html")

		# add temperature and pressure info
		#responseData = responseData.replace("EEE", tempData)
		#responseData = responseData.replace("FFF", pressureData)

		# more system info
		#responseData += subprocess.check_output(["cat", "/proc/cpuinfo"])
		#responseData += subprocess.check_output(["cat", "/proc/meminfo"])

		# data from ST-1 SendText control 
		responseData = responseData.replace("KKK", sendTextData)
		
	return responseData
	
def SAB_func(list_par, bValidate):
	"""Simple Action Button"""
	
	if bValidate: 
		return "VALIDATED"

	responseData = ""
	
	if list_par[0] == 1:
				
		responseData = "OK"
		
	return responseData			
	
def FFF_func(list_par, bValidate):
	"""Template function"""
	
	if bValidate: 
		return "VALIDATED"

	responseData = ""
	
	# ... #1
	if list_par[0] == 1:
		responseData = "OK"
		
	return responseData

def Default_func(list_par, bValidate):
	"""
	Default handler function.
	Do not change/delete this!
	"""
	return ""
		

	
def buildHTML(htmlfile):
	
	#htmlfile = html_file or "./Templates/info.html"
	
	# read the HTML template into a string
	try:
		with open (htmlfile, "r") as myfile:
			responseData = myfile.read().replace('\n', '')
			
	except IOError:
		return "<h3>Info not available</h3>"
		
	# replace the URL so it will point to static
	#responseData = responseData.replace("XXX", LOCALURL)

	# hostname
	responseData = responseData.replace("HOST", subprocess.check_output(["hostname", ""], shell=True).strip().decode('utf-8'))

	# now replace the AAA, BBB, etc with the right data
	responseData = responseData.replace("AAA", subprocess.check_output(["date", ""], shell=True).strip().decode('utf-8'))

	# split uptime at first blank, then at first ,
	uptimeString = subprocess.check_output(["uptime", ""]).strip().decode('utf-8')

	uptimeType = uptimeString.split(",")
	uptimeCount = len(uptimeType)

	if (uptimeCount == 6):
		# over 24 hours
		uptimeSplit = uptimeString.split(",")
		uptimeSplit = uptimeSplit[0]+uptimeSplit[1]
		uptimeSplit = uptimeSplit.split(" ", 1)
		uptimeData = uptimeSplit[1]
	else:
		# under 24 hours
		uptimeSplit = uptimeString.split(" ", 2)
		uptimeSplit = uptimeSplit[2].split(",", 1)
		uptimeData = uptimeSplit[0]

	responseData = responseData.replace("BBB", uptimeData)

	usersString = subprocess.check_output(["who", "-q"], shell=False, stderr=subprocess.STDOUT).strip().decode('utf-8')
	responseData = responseData.replace("CCC", usersString)

	freeString = subprocess.check_output(["free", "-mh"]).strip().decode('utf-8')
	freeSplit = freeString.split("cache: ", 1)
	freeSplit = freeSplit[1].split("       ", 2)
	freeSplit = freeSplit[2].split("\nSwap:", 1)
	freeData = freeSplit[0]

	responseData = responseData.replace("DDD", freeData)

	output = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"]).strip().decode('utf-8')
	cpuTemp = "%3.2f C" % (float(output)/1000.0)

	responseData = responseData.replace("GGG", cpuTemp)

	try:
		ifString = subprocess.check_output(["ifconfig", "eth0"]).strip().decode('utf-8')
		ifSplit = ifString.split("inet addr:", 1)
		if (len(ifSplit) > 1):
			ifSplit = ifSplit[1].split(" ", 1)
			ifData = ifSplit[0] + " (eth0)"

		else:
			ifData = "no eth0"
			raise

	except:

		ifString = subprocess.check_output(["ifconfig", "wlan0"]).strip().decode('utf-8')
		ifSplit = ifString.split("inet addr:", 1)
		if (len(ifSplit) > 1):
			ifSplit = ifSplit[1].split(" ", 1)
			ifData = ifSplit[0] + " (wlan0)"
		else:
			ifData = "no eth0 or wlan0"

	responseData = responseData.replace("HHH", ifData)

	responseData = responseData.replace("III", Config.localURL().decode('utf-8'))
	# responseData = responseData.replace("III", "'your external address here'")

	responseData = responseData.replace("JJJ", Config.version_number().decode('utf-8'))

	return responseData


# Set up the dispatcher for the RaspPiConnect ObjectServer messages
ObjectServerHandlers = RasPiDispatcher(0.05, 20)
AssignObjectServerHandlers()	