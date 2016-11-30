#!/usr/bin/env python 

""" 
An echo server that uses select to handle multiple clients at a time. 
Entering any line of input at the terminal will exit the server. 
""" 
import config
from HsaProfile import HsaProfile
from HsaMsg import HsaMsgType
from HsaMsg import HsaStatusType
from datetime import datetime

class HsaMonitor:
    
    def __init__(self):
        self.ChangeProfile(config.Standby)
        self.changeListener = []
        self.statusListener = []
        self.lastUpdate = datetime.today()

    def ChangeProfile(self, newProfile):
        self.profile = HsaProfile(newProfile.profileName, newProfile.profileCode)
        self.profile.CopyFrom(newProfile)
        #Set "last update" time for all devices of interest
        for di in self.profile.devicesOfInterest:
            di['lastUpdate'] = datetime.today()
        self.disturbed = []
        self.status = HsaStatusType.STANDBY
        self.startTime = datetime.today()
        self.alarmedTime = False
        #print "Monitor updated with profile {}".format(self.profile.profileName)

    def ReceiveMsg(self, msg):
        if msg.msgType == HsaMsgType.DOOR or msg.msgType == HsaMsgType.MOTION:
            #Don't exit because the message will be used
            pass
        else:
            #message is not of interest so ignore and exit
            return

        devForUpdate = False
        for dev in self.profile.devicesOfInterest:
            if dev['source'] == msg.msgSrc and dev['type'] == msg.msgType \
                                           and dev['name'] == msg.msgName:
                #print "Matched device"
                devForUpdate = dev

        if devForUpdate == False:
            devForUpdate = { 'source':msg.msgSrc, 'type':msg.msgType, \
                             'name':msg.msgName }
            self.profile.devicesOfInterest.append(devForUpdate)

        self.UpdateState(devForUpdate, msg.msgInfo, msg.msgExtra)

    def UpdateState(self, devToUpdate, state, extraInfo):
        devToUpdate['lastUpdate'] = datetime.today()
        if not 'state' in devToUpdate or devToUpdate['state'] != state:
            devToUpdate['state'] = state
            self.NotifyDevChange(devToUpdate)
            self.CheckState(devToUpdate)
            
    def AddDevChangeListener(self, listener):
        self.changeListener.append(listener)

    def NotifyDevChange(self, devChanged):
        for lsnr in self.changeListener:
            lsnr(devChanged)

    def AddStatusChangeListener(self, listener):
        self.statusListener.append(listener)

    def NotifyStatusChange(self):
        for lsnr in self.statusListener:
            lsnr(self.status)

    def CheckState(self, dev):
        timeSinceStart = abs(datetime.today()-self.startTime)
        devDisturbed = False
        if timeSinceStart.total_seconds() > self.profile.delayStart:
            if 'matching' in dev and 'cmpState' in dev and 'state' in dev:
                if dev['matching'] == True:
                    if dev['cmpState'] != dev['state']:
                        devDisturbed = True
                else:
                    if dev['cmpState'] == dev['state']:
                        devDisturbed = True
        if devDisturbed:
            inList = False
            for d in self.disturbed:
                if dev['source'] == d['source'] and dev['type'] == d['type'] \
                                                and dev['name'] == d['name']:
                    inList = True
            #Only if the disturbed is not already in the list will it be added
            if inList == False:
                self.disturbed.append(dev)
                print "Disturbed {}".format(dev['name'])

    def UpdateStatus(self):
        curStatus = self.status
        timeSinceStart = abs(datetime.today()-self.startTime)
        if len(self.disturbed) > 0 and self.alarmedTime == False:
            #only if the alarm time is not set do we set it, this causes
            # the first disturbance to set the alarmed time
            self.alarmedTime = datetime.today()

        if self.profile.profileName == 'Standby':
            self.status = HsaStatusType.STANDBY
        elif timeSinceStart.total_seconds() < self.profile.delayStart:
            self.status = HsaStatusType.ARMING
        elif self.alarmedTime == False:
            self.status = HsaStatusType.ARMED
            rightNow = datetime.today()
            for di in self.profile.devicesOfInterest:
                if 'updatePeriod' in di and 'lastUpdate' in di:
                    timeSinceUpdate = abs(rightNow - di['lastUpdate'])
                    if timeSinceUpdate.total_seconds() > di['updatePeriod']:
                        self.alarmedTime = datetime.today()
        else:
            timeSinceAlarm = abs(datetime.today() - self.alarmedTime)
            #Alarmed time has been set
            if timeSinceAlarm.total_seconds() < self.profile.delayAlarm:
                self.status = HsaStatusType.DELAYED_ALARM
            else:
                self.status = HsaStatusType.ALARMED

        timeSinceLastUpdate = abs(datetime.today()-self.lastUpdate)
        if curStatus != self.status or timeSinceLastUpdate .total_seconds() > 5:
            self.NotifyStatusChange()
            self.lastUpdate = datetime.today()

    def GetStatus(self):
        return self.status

