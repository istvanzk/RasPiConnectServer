RasPiConnectServer, V3.0
==================

Server for RasPiConnect App on the Apple Appstore.

See www.milocreek.com for complete documentation.

This is a fork from milocreek/RasPiConnectServer, 04.04.2016, modified to work with Pyhton3.4+.

Main changes compared to the original milocreek/RasPiConnectServer are:

1. The web module was replaced by the cherrypy module to provide additional functionalities.

2. Updated all python files in config, local, RasPilib and ExecuteFiles to work with Pyhton3.4+. The Adafruit files have not been updated yet.

3. The local/Local.py uses a dispatcher class to register handlers for the the different objectServerID.

4. The rpiconn.sh script was added to run the RasPiConnectServer as a service via init.d



