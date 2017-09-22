import SocketServer
import random
import sys
import md5
import time
import threading
import os

SERVERHELLO = '''------------------------------------------------
|            Aero Auth Service                 |
------------------------------------------------
| version: 0.01 beta                           |
| dev by revker( opensource project )          |
------------------------------------------------
'''
SERVEREXIT    = "Connection close!\n"
AUTHREQLOGIN  = "Login:"
AUTHREQPASSWD = "Password:"
AUTHFALSE     = "Incorrect login or password!\n"
AUTHCORRECT   = "Auth success!\n"

LOGINSIZE     = 32
PASSWORDSIZE  = 32
COMMANDSIZE   = 1
FILENAMESIZE  = 10

Database = { 'veiwer':'VeIwEr', 'dev':'revker', 'admin':'admin', 'root':'toor' }

TextMenu = '''----------------------------------------------------------
Menu\n1. Read File\n2. Write File\n3. Give shell\n4. Exit\nSelect the number of option: '''

RoleList = { 'veiwer':3, 'admin':2, 'root':1, 'dev':0 }
OptionDict = { 1:'Read File', 2:'Write File', 3:'Give shell', 4:'Exit' }
AccessControl = { 'veiwer':[ 1, 4 ], 'admin':[ 1, 2, 4 ], 'root':[ 1, 2, 3, 4 ], 'dev':[ 1, 2, 3, 4 ] }


class TCPHandler( SocketServer.BaseRequestHandler ):

    def auth( self ):
        global Database

        self.request.sendall( SERVERHELLO )
        self.request.sendall( AUTHREQLOGIN )

        login = self.request.recv( LOGINSIZE ).strip()
        print "IP: %s\tlogin:%s" % ( self.client_address[ 0 ] , login )

        if login in Database.keys():
            self.request.sendall( AUTHREQPASSWD )
        else:
            return 0

        password = self.request.recv( PASSWORDSIZE ).strip()
        print "IP: %s\tpassword:%s" % ( self.client_address[ 0 ], password )

        if Database[ login ] == md5.new( password ).hexdigest():
            return 1, login
        else:
            return 0

    def ReadFile( self, fileName ):
        try:
            fd = open( fileName, 'rb' )
        except:
            self.request.sendall( 'File not opening!\nFile name is %s\n' % fileName )
            return 0
        buf = fd.read()
        self.request.sendall( buf )

    def handle( self ):
        global OptionDict
        global AccessControl

        authResult, Role = self.auth()

        if authResult == 1:
			self.request.sendall( AUTHCORRECT )
        else:
            self.request.sendall( AUTHFALSE )
            return 0

        while 1:
            self.request.sendall( TextMenu )
            InputCommand = int( self.request.recv( 2 ).strip() )

            if InputCommand in OptionDict.keys() and InputCommand in AccessControl[ Role ]:
                Option = OptionDict[ InputCommand ]
                self.request.sendall( "Option is setting correct it is %s\n" % Option)

                if Option == 'Exit':
                    self.request.sendall( "Exit....." )
                    break

                if Option == 'Read File':
                    self.request.sendall( 'wrtie filename to read: ' )
                    time.sleep(5)
                    fileName = self.request.recv( 1024 ).strip()

                    if "/" in fileName or ".." in fileName:
                        break
                    self.ReadFile( fileName )
                if Option == 'Give shell':
                    os.system( 'nc -lvvp 1337 -e "/bin/sh"' )
                    break
            else:
                self.request.sendall( "Option isn't setting( Access or number failed )!\n" )


class ThreadedTCPServer( SocketServer.ThreadingMixIn, SocketServer.TCPServer ):
    pass


def hashingDB( DB ): # tested - WORK!

	for key in DB.keys():
		DB[ key ] = md5.new( DB[ key ] ).hexdigest()

if __name__ == "__main__":

    hashingDB( Database )

    if len( sys.argv ) > 1:
        PORT = int( sys.argv[ 1 ] )
    else:
        print "terminate port!\n"
        sys.exit(0)

    HOST = '0.0.0.0'
    Server = ThreadedTCPServer( ( HOST, PORT ), TCPHandler )

    ServerThread = threading.Thread( target = Server.serve_forever )
    ServerThread.daemon = False
    ServerThread.start()

    while True:
        try:
            time.sleep(1)
        except:
            break

    Server.shutdown()
    Server.server_close()
