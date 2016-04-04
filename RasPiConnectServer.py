#!/usr/local/bin/python3
# Filename: RasPiConnectServer.py
# Version 2.9 9/07/13 RV MiloCreek
# Version 3.0 04.04.2016 IzK (Python3.4+ and CherryPy)

#set up sub directories

import sys
sys.path.append('./Adafruit')
sys.path.append('./ExecuteFiles')
sys.path.append('./RasPilib')
sys.path.append('./local')
sys.path.append('./config')

# configuration constants

import Config

# system imports

import hashlib
import cherrypy
from cherrypy import tools
from cherrypy import Tool

import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError

# RasPiConnectServer execute command routines

import ExecuteServerStatus
import ExecuteMeter
import ExecuteBarMeter
import ExecuteRemoteWebView
import ExecuteActionButton
import ExecuteSingleLED
import ExecuteFreqModLED
import ExecuteTextAndTitle
import ExecuteSendText
import ExecuteFileDirectory



# RasPiConnectServer interface constants

REMOTE_WEBVIEW_UITYPE = 1
ACTION_BUTTON_UITYPE = 16
FEEDBACK_ACTION_BUTTON_UITYPE = 17
SINGLE_LED_DISPLAY_UITYPE = 32
SPEEDOMETER_UITYPE = 64
VOLTMETER_UITYPE = 128
BARMETER_UITYPE = 129
SERVER_STATUS_UITYPE = 256
PICTURE_REMOTE_WEBVIEW_UITYPE = 512
LABEL_UITYPE = 1024
FM_BLINK_LED_UITYPE = 2048
TEXT_DISPLAY_UITYPE = 4096
TOGGLE_SWITCH_UITYPE = 33
SEND_TEXT_UITYPE = 34

FILE_DIRECTORY_CALL = 8192
FILE_READ_CALL = 16384
FILE_WRITE_CALL = 32768


# end interface constants

# Check for user imports
local_present = True
try:
	import Local
except ImportError:
	local_present = False
	import LocalExample
			
def setxmlres(incomingXML):
	"""Build an XML response based on the XML request """
				
	# iterate through all the values and pull all the requests together
	# find the interface object type
	root = ET.fromstring(incomingXML)

	# start of building the XML responses sent back to the RasPiConnect App
	outgoingData="<XMLRESPONSES>"

	# Parse the XML

	# a message from the RasPiConnect App can consist of many individual control requests for refresh

	for element in root.findall('XMLCOMMAND'): # Get the items out.
	# Iterate through the list of items(They are in element objects)

		if (Config.debug()):
			print('XMLCOMMAND:') # Yey print stuff out!
			print('USERNAME:', element.find('USERNAME').text)
			print('PASSWORD:', element.find('PASSWORD').text)
			print('OBJECTNAME:', element.find('OBJECTNAME').text)
			print('OBJECTTYPE:', element.find('OBJECTTYPE').text)
			print('OBJECTSERVERID:', element.find('OBJECTSERVERID').text)
			print('OBJECTID:', element.find('OBJECTID').text)

		# authentication

		username = element.find('USERNAME').text
		password = element.find('PASSWORD').text

		m=hashlib.md5()
		m.update(Config.username())
		MD5username = m.hexdigest()
		MD5username = MD5username.upper()

		m=hashlib.md5()
		m.update(Config.password())
		MD5password = m.hexdigest()
		MD5password = MD5password.upper()

		if (Config.debug()):
			print(MD5username)
			print(MD5password)


		# gather the control object type
		objectType = element.find("./OBJECTTYPE").text
		objectType = int(objectType)

		# gather the RasPiConnect ID
		objectID = element.find("./OBJECTID").text
		objectID = int(objectID)




		if (Config.debug()):
			print(("objectType = %i" % objectType))


		# check for password and username.  If they don't match, then return an error and quit

		# password username error message
		if (username != MD5username) or (password != MD5password):
			if (Config.debug()):
				print(("objectType = %i" % objectType))

			outgoingData +="<XMLCOMMAND><OBJECTTYPE>%i" % objectType
			outgoingData +="</OBJECTTYPE>"
			outgoingData +="<OBJECTID>%i" % objectID
			outgoingData +="</OBJECTID>"
			outgoingData +='<ERROR>Username or Password Mismatch</ERROR></XMLCOMMAND>'

			outgoingData+="</XMLRESPONSES>"

			print(outgoingData)
			return outgoingData


		# call user routines 
		# by objectServerID
		if (local_present == True):
			returnData =  Local.ExecuteUserObjects(objectType, element)
		else:
			returnData =  LocalExample.ExecuteUserObjects(objectType, element)

		if (Config.debug()):
			print("Local user objects returns: %s" % returnData)

		if (len(returnData) != 0):
			outgoingData += returnData
			
		# if user objects not found (by zero length string), check for the predefined ones
		# by objectType
		if (len(returnData) == 0):

			# call web objects
			if (objectType == REMOTE_WEBVIEW_UITYPE):
				if (Config.debug()):
					print("REMOTE_WEBVIEW_UITYPE found")
				outgoingData += ExecuteRemoteWebView.Generate_Remote_WebView(element, Config.localURL())
			elif (objectType == PICTURE_REMOTE_WEBVIEW_UITYPE):
				if (Config.debug()):
					print("PICTURE_REMOTE_WEBVIEW_UITYPE found")
				outgoingData += ExecuteRemoteWebView.Generate_Remote_WebView(element, Config.localURL())

			# call button objects
			elif (objectType == ACTION_BUTTON_UITYPE):
				if (Config.debug()):
					print("ACTION_BUTTON_UITYPE found")
				outgoingData += ExecuteActionButton.Execute_Action_Button(element)

			# call button objects
			elif (objectType == FEEDBACK_ACTION_BUTTON_UITYPE):
				if (Config.debug()):
					print("FEEDBACK_ACTION_BUTTON_UITYPE found")
				outgoingData += ExecuteActionButton.Execute_Action_Button(element)

			# call send text objects
			elif (objectType == SEND_TEXT_UITYPE):
				if (Config.debug()):
					print("SEND_TEXT_UITYPE found")
				outgoingData += ExecuteSendText.Execute_Send_Text(element)

			# call text and display type
			elif (objectType == TEXT_DISPLAY_UITYPE):
				if (Config.debug()):
					print("TEXT_DISPLAY_UITYPE found")
				outgoingData += ExecuteTextAndTitle.Execute_Text_And_Title(element)

			# call Frequency Modulated LED
			elif (objectType == FM_BLINK_LED_UITYPE):
				if (Config.debug()):
					print("FM_BLINK_LED_UITYPE found")
				outgoingData += ExecuteFreqModLED.Execute_Freq_Mod_LED(element)

			# call single LED objects
			elif (objectType == SINGLE_LED_DISPLAY_UITYPE):
				if (Config.debug()):
					print("SINGLE_LED_DISPLAY_UITYPE found")
				outgoingData += ExecuteSingleLED.Execute_Single_LED(element)

			# call speedometer objects
			elif (objectType == SPEEDOMETER_UITYPE):
				if (Config.debug()):
					print("SPEEDOMETER_UITYPE found")
				outgoingData += ExecuteMeter.Execute_Meter(element)

			# call voltmeter objects
			elif (objectType == VOLTMETER_UITYPE):
				if (Config.debug()):
					print("VOLTMETER_UITYPE found")
				outgoingData += ExecuteMeter.Execute_Meter(element)

			# call barmeter objects
			elif (objectType == BARMETER_UITYPE):
				if (Config.debug()):
					print("BARMETER_UITYPE found")
				outgoingData += ExecuteBarMeter.Execute_BarMeter(element)

			# call server objects
			elif (objectType == SERVER_STATUS_UITYPE):
				if (Config.debug()):
					print("SERVER_STATUS_UITYPE found")
				outgoingData += ExecuteServerStatus.Execute_Server_Status(element)
			# call file directory object
			elif (objectType == FILE_DIRECTORY_CALL):
				if (Config.debug()):
					print("FILE_DIRECTORY_CALL found")
				outgoingData += ExecuteFileDirectory.Execute_File_Directory(element)

			# call file read object
			elif (objectType == FILE_READ_CALL):
				if (Config.debug()):
					print("FILE_READ_CALL found")
				outgoingData += ExecuteFileDirectory.Execute_File_Read(element)

			# call file write object
			elif (objectType == FILE_WRITE_CALL):
				if (Config.debug()):
					print("FILE_WRITE_CALL found")
				outgoingData += ExecuteFileDirectory.Execute_File_Write(element)

			else:

				# default error message
				if (Config.debug()):
					print(("objectType = %i" % objectType))

				outgoingData +="<XMLCOMMAND><OBJECTTYPE>%i" % objectType
				outgoingData +="</OBJECTTYPE>"
				outgoingData +="<OBJECTID>%i" % objectID
				outgoingData +="</OBJECTID>"
				outgoingData +='<ERROR>RasPi ObjectType Not Supported</ERROR></XMLCOMMAND>'

	# done with FOR loop
	outgoingData+="</XMLRESPONSES>"
	
	return outgoingData


def getxmlreq():
	"""Get the XML request """
		
	# Get the mime type of the entity sent by the user-agent
	ct = cherrypy.request.headers.get('Content-Type', None)
	
	# if it is not a mime type we can handle
	# then let's inform the user-agent
	if ct not in ['text/xml; charset=utf-8', 'application/xml; charset=utf-8']:
		raise cherrypy.HTTPError(415, 'Unsupported Media Type')

	# CherryPy will set the request.body with a file object
	# where to read the content from
	if hasattr(cherrypy.request.body, 'read'):
		incomingXML = cherrypy.request.body.read()
				
	# inject the parsed document instance into
	# the request parameters as if it had been
	# a regular URL encoded value
	##cherrypy.request.params['xmlreq'] = incomingXML

	return incomingXML
	
def printbody():

	print("\nReqH: %s" % cherrypy.request.headers)
	print("ReqM: %s" % cherrypy.request.method)
	print("ReqB: %s" % cherrypy.request.body.read())
	print("ReqPath: %s" % cherrypy.request.path_info)
	print("ReqParms: %s" % cherrypy.request.params)

	print("\nResH: %s" % cherrypy.response.headers)
	print("ResB: %s" % cherrypy.response.body)

tools.print_body = Tool('before_finalize', printbody)

def secureheaders():
	"""
	Make CherryPy pages more secure
	Rendering pages:
	Set HttpOnly cookies
	Set XFrame options
	Enable XSS Protection
	Set the Content Security Policy
	"""
	headers = cherrypy.response.headers
	headers['X-Frame-Options'] = 'DENY'
	headers['X-XSS-Protection'] = '1; mode=block'
	headers['Content-Security-Policy'] = "default-src='self'"
    
tools.secureheaders = Tool('before_finalize', secureheaders, priority=60)
			
class RasPiService(object):
	"""
	The RasPi server responding to POST requests
	Test with: curl -d "body"  --header "Content-Type:text/xml; charset=utf-8" http://192.168.87.110:9696/raspi
	"""
	exposed = True

	#def _cp_dispatch(self, vpath):
	#	req = vpath.pop(0)
	#	if req not in ['raspi', 'Raspi', 'RasPi']:
	#		raise cherrypy.HTTPError(405, 'Unsupported request path')
    		
	#@tools.print_body()
	def POST(self, reqpath):	
	
		# check request path
		if reqpath not in ['raspi', 'Raspi', 'RasPi']:
			raise cherrypy.HTTPError(405, 'Unsupported request path')

		#return 'TestMode'
	
		# get incoming XML
		incomingXML = getxmlreq()		
		cherrypy.session['xmlreq'] = incomingXML
		if (Config.debug()):
			print("Incoming request xml =%s" %incomingXML)

		# build the response XML
		outgoingXML = setxmlres(incomingXML)

		# build cherrypy POST response
		cherrypy.response.status = '201 Created'
		cherrypy.response.headers['Location'] = '/' + reqpath

		if (Config.debug()):
			print("Outgoing response xml =%s" % outgoingXML)
				
		return outgoingXML
		
class WebService(object):

	@cherrypy.expose(['Version','V','v'])
	@cherrypy.tools.accept(media='text/html')
	def version(self):
		cherrypy.response.headers['Content-Type'] = 'text/html'
		outGoingData = "<B>RasPiConnectServer Version %s</B><BR>" % Config.version_number()
				
		return outGoingData

	@cherrypy.expose(['Info','I','i'])
	@cherrypy.tools.accept(media='text/html')
	def info(self):	
		cherrypy.response.headers['Content-Type'] = 'text/html'
		
		responseData = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"><html>"
		responseData += "<head><meta content=\"text/html; charset=ISO-8859-1\" http-equiv=\"Content-Type\">"
		responseData += "<title>Info page</title><style>body,html,iframe{margin:5;padding:5;}</style></head>"
		responseData += "<body bgcolor=\"#cccccc\" link=\"#0000EE\" text=\"#000000\" vlink=\"#551A8B\" alink=\"#EE0000\">"

		responseData += "<h1>Info page</h1>"
		
		if (Config.debug()):
			print("Info page")

		# if Local.py is not found, import default LocalExample.py
		local_present = True
		# Check for user imports
		try:
			import Local
		except ImportError:
			local_present = False
			import LocalExample

		if (local_present == True):
			responseData += "<h2>Local.py</h2>"
			responseData += Local.UserObjectsInfo()
		else:
			responseData += "<h2>LocalExample.py</h2>"

		responseData += "</body></html>"
							
		# Return html page
		return responseData



if __name__ == '__main__':
	http_conf = {
		'global':{
			'server.socket_host': Config.hostAddr().decode('utf-8'),
			'server.socket_port': Config.web_server_port(),
			'environment': 'production',
			'log.screen': True,
			'log.error_file': 'error.log',
			'log.access_file': 'access.log'
		}
	}
	cherrypy.config.update(http_conf)
	web_conf =	{	
		'/': {
			'tools.secureheaders.on' : True,
			'tools.sessions.on': True,
			'tools.sessions.secure' : True,
			'tools.sessions.httponly' : True,
			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'text/html; charset=utf-8')],
			'tools.trailing_slash.on': False,
        }
	}        			
	rest_conf =	{
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
 			'tools.sessions.on': True,
 			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'text/xml; charset=utf-8')],
 			'tools.sessions.secure' : True,
 			'tools.sessions.httponly' : True,
 			'tools.trailing_slash.on': False,
        }			   
	}

	# Application is a pure CherryPy application, no WSGI:
	# switch to a HTTP server that by-passes the WSGI layer altogether. 
	# DOES NOT WORK!?
	#from cherrypy._cpnative_server import CPHTTPServer
	#cherrypy.server.httpserver = CPHTTPServer(cherrypy.server)	
	
	
	#pi_service = WebService()
	#pi_service.raspi = RasPiService()
	#cherrypy.quickstart(pi_service, '/', config = rest_conf)

	#cherrypy.quickstart(RasPiService(), '/', rest_conf)
	
	cherrypy.tree.mount(WebService(), '/w', config = web_conf)		
	cherrypy.tree.mount(RasPiService(), '/', config = rest_conf)	
	cherrypy.server.start()
	cherrypy.engine.start()
