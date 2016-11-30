#!/usr/bin/env python 

""" 
An echo server that uses select to handle multiple clients at a time. 
Entering any line of input at the terminal will exit the server. 
""" 

import select 
import socket 
import sys
import threading
import syslog
import string
import re
from HsaMsg import HsaMsg
from HsaMsg import HsaError
import logging

#logger = logging.getLogger("mine")
#hdlr = logging.FileHandler('Hsa.log')
#FORMAT=logging.Formatter('%(asctime)-15s %(message)s')
#hdlr.setFormatter(FORMAT)
#logger.addHandler(hdlr)
#logger.setLevel(logging.INFO)


class HsaSocketServer(threading.Thread):
    # data saved from successive reads on the incoming sockets
    incomingData = []
    # addresses of connections in inputs
    connections = []
    # sockets that have been connected
    inputs = []
    # bind'ed sockets that are listening for new connections
    servers = []
    # tuple of (host,port) that matches in index with the servers
    #  used for if there is an error on a server the server can be 
    #  closed and reopened
    listeners = []
    running = False
    backlog = 5 
    size = 1024 
    dataObserver = []
    
    def __init__(self):
        threading.Thread.__init__(self)
        running = False

    def addListen(self,host,port):
        newServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This doesn't seem quite right but when close down the start
        # back up this should stop from erroring out because of 
        # "Address already in use"
        newServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        newServer.bind((host,port))
        newServer.listen(self.backlog)
        self.listeners.append((host,port))
        self.servers.append(newServer)

    def addDataObserver(self,callback):
        self.dataObserver.append(callback)

    def stop(self):
        self.running = False
        print "Shutting down {0}".format(self.__class__.__name__)

    def refreshListener(self,sock):
        i =  self.servers.index(sock)
        sock.close()
        self.servers.pop(i)
        pair = self.listeners.pop(i)
        newServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        newServer.bind(pair)
        newServer.listen(self.backlog)
        self.listeners.append(pair)
        self.servers.append(newServer)

    def receiveData(self, connection, src, data):
        msg = HsaMsg()
        try:
            msg.ParseMsg(data)
        except HsaError as e:
            errMsg = "Error {}: {}".format(e.__class__.__name__, e.originalStr)
            print errMsg
            #syslog.syslog(repr(errMsg))
        else:
            msg.SetConnSrc(src)
            for c in self.dataObserver:
                c(msg)

    def sendToAll(self, data):
        for c in self.inputs:
            try:
                c.send(data)
            except:
                pass
    
    def run(self):
        self.running = True 
        while self.running: 
            socks = []
            socks.extend(self.servers)
            socks.extend(self.inputs)
            # Can be a large timeout because it is not expected to add
            #  any new listeners after the loop has started anyway. (1 second)
            iready,oready,eready = select.select(socks,[],[],1)

            # I read something at one point that if one of the sockets
            #  dies a horrible deat it may be necessary to loop through
            #  each socket doing a select(sock[i],[],[],0) to find the bad one

            for s in iready: 

                if s in self.servers: 
                    # handle if the socket is a listener
                    try:
                        client, address = s.accept()
                    except socket.error:
                        print "Error accepting new connection"
                        refreshListener(sock)
                    else:
                        self.inputs.append(client)
                        self.connections.append(address)
                        self.incomingData.append("")

                else: 
                    # handle all other sockets 
                    i = self.inputs.index(s)
                    try:
                        data = s.recv(self.size)
                    except socket.error as msg:
                        print "Remove socket "+str(s)
                        self.connections.pop(i)
                        s.close() 
                        self.inputs.remove(s)
                        continue
                    if data: 
                        self.incomingData[i] += data
                        if string.count(self.incomingData[i], "\n") > 0:
                            [ singleMsg, restOf ] = re.split('[\n\r]', self.incomingData[i], 1)
                            self.incomingData[i] = restOf
                            if len(singleMsg) > 0 :
                                self.receiveData(s,self.connections[i],singleMsg)
                        #for c in self.dataObserver:
                        #    c(s,self.connections[i],data)
                    else:
                        self.connections.pop(i)
                        s.close() 
                        self.inputs.remove(s)


        for s in socks:
            s.close()
        
