#!/usr/bin/env python 

""" 
An echo server that uses select to handle multiple clients at a time. 
Entering any line of input at the terminal will exit the server. 
""" 

import string

class HsaError(Exception):
    originalStr = ' '
    def __init__(self, string):
        Exception.__init__(self)
        self.originalStr = string
    pass

class BadMsgError(HsaError):
    pass

class BadTypeError(HsaError):
    pass

class BadSourceError(HsaError):
    pass

class BadNameError(HsaError):
    pass

class NoInfoError(HsaError):
    pass

class HsaMsgType:
    INPUT = 0
    DOOR = 1
    MOTION = 2
    STATUS = 100
    LINE = 101
    INVALID = -1
    
    def fromStringToType(self, data):
        types = (self.INPUT, self.DOOR, self.MOTION, self.STATUS, self.LINE, self.INVALID );
        retType = self.INVALID
        for s in types:
            if str(s).lower() == data.lower():
                retType = s
        if retType == self.INVALID:
            raise BadTypeError(data)
        return retType

class HsaStatusType:
    STANDBY = 'Standby'
    ARMING = 'Arming'
    ARMED = 'Armed'
    DELAYED_ALARM = 'Delayed'
    ALARMED = 'Alarmed'


class HsaMsg:
    def __init__(self):
        self.maxSize = 200
        self.conSrc = ''
        self.msgSrc = -1
        self.msgType = HsaMsgType.INVALID
        self.msgName = ' '
        self.msgInfo = ' '
        self.msgExtra = ' '

    def SetConnSrc(self, source):
        self.conSrc = source

    def ParseMsg(self, dataString):
        splitElements = dataString.split(',');
        if len(dataString) < 6 or len(splitElements) < 4 \
            or len(splitElements[0]) < 1 or len(splitElements[1]) < 1 \
            or len(splitElements[2]) < 1 or len(splitElements[3]) < 1:
            raise BadMsgError(dataString)
        
        try:
            self.msgSrc = int(splitElements[0])
            self.msgType = HsaMsgType().fromStringToType(splitElements[1])
            self.msgName = string.strip(splitElements[2])
            self.msgInfo = string.strip(splitElements[3])
        except ValueError:
            raise BadMsgError(dataString)
        if len(splitElements) > 4:
            self.msgExtra = string.strip(splitElements[4])

        if self.msgType == HsaMsgType.INVALID:
            raise BadTypeError(dataString)

        if self.msgSrc < -1:
            raise BadSourceError(dataString)
        if self.msgSrc > 10:
            raise BadSourceError(dataString)
         
        if len(self.msgName) < 3:
            raise BadNameError(dataString)

        if len(self.msgInfo) < 3:
            raise NoInfoError(dataString)

    def ShowMe(self):
        print "Msg: ConSource {} NodeSrc {}".format(self.conSrc, self.msgSrc)
        print "     Type {} Name {} Info {}".format(self.msgType, self.msgName, self.msgInfo)
        if len(self.msgExtra) > 2:
            print "     ExtraInfo {}".format(self.msgExtra)
