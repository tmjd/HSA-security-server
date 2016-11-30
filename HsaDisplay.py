#!/usr/bin/env python 

""" 
An echo server that uses select to handle multiple clients at a time. 
Entering any line of input at the terminal will exit the server. 
""" 
import config
from HsaProfile import HsaProfile
from HsaMsg import HsaStatusType
from time import strftime
from datetime import datetime

class DisplayLine:
    def __init__(self):
        self.line = ' '
        self.lastUpdate = datetime.today()
        self.devInfo = { 'name':' ', 'source':' ', 'type':' '}

    def UpdateLine(self, lineMsg):
        self.lastUpdate = datetime.today()
        self.line = lineMsg

    def UpdateDevLine(self, dev):
        self.devInfo = dev
        lineMsg = "{} {}".format(dev['name'], dev['state']).ljust(20, ' ')
        self.UpdateLine(lineMsg)

    def IsDevLine(self,dev):
        if self.devInfo['name'] == dev['name'] \
            and self.devInfo['source'] == dev['source'] \
            and self.devInfo['type'] == dev['type']:
            return True
        else:
            return False

class HsaDisplay:
    
    def __init__(self):
        self.lines = {}
        self.ChangeProfile(config.Standby)
        self.senders = []
        for i in range(1, 5):
            self.lines[i] = DisplayLine()

    def ChangeProfile(self, newProfile):
        self.profile = HsaProfile(newProfile.profileName, newProfile.profileCode)
        self.profile.CopyFrom(newProfile)
        self.status = HsaStatusType.STANDBY
        self.changed = []
        self.lines[2] = DisplayLine()
        self.lines[3] = DisplayLine()
        self.lines[4] = DisplayLine()

    def UpdateStatus(self, status):
        self.status = status

    def UpdateDeviceChange(self, dev):
        self.changed.append(dev)
            
    def AddOutputSender(self, sender):
        self.senders.append(sender)

    def SendLine(self, lineNum, line):
        print "{}:Ln{}:{}".format(datetime.today(),lineNum, line)
        for sndr in self.senders:
            sndr(lineNum, line)

    def SendDisplayUpdate(self):
        if self.status == HsaStatusType.ARMED:
            line1 = '{}'.format(self.profile.profileName).ljust(12,' ')
        else:
            line1 = '{}'.format(self.status).ljust(12, ' ')
        line1 += strftime("%I:%M%p")
        if line1 != self.lines[1].line:
            self.lines[1].line = line1
            self.SendLine(1,self.lines[1].line)

        while len(self.changed) > 0:
            chnDev = self.changed.pop(0)

            currentlyDisplayed = False
            for li in {2, 3, 4}:
                if self.lines[li].IsDevLine(chnDev):
                    self.lines[li].UpdateDevLine(chnDev)
                    currentlyDisplayed = True
                    self.SendLine(li, self.lines[li].line)

            if currentlyDisplayed == False:
                oldestIndex = 2
                for li in {3, 4}:
                    if self.lines[oldestIndex].lastUpdate > self.lines[li].lastUpdate:
                        oldestIndex = li

                self.lines[oldestIndex].UpdateDevLine(chnDev)
                self.SendLine(oldestIndex, self.lines[oldestIndex].line)
            

        
