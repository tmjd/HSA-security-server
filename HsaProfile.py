#!/usr/bin/env python 

""" 
Used to manage the alarm profiles.  Each profile consists of a name, id/code,
time to delay before checking mode, time delay before alarming after a disturbance,
devices of interest in the mode, and the possible profile codes to switch to and if
a password is required to switch to that mode.
""" 

class HsaProfile:

    def __init__(self, name, code):
        self.profileName = name
        self.profileCode = str(code)
        self.nextProfile = []
        self.devicesOfInterest = []
        self.delayStart = 0
        self.delayAlarm = 0

    def ShowMe(self):
        print "Profile: {} Code: {}".format(self.profileName, self.profileCode)
        print "   Start delay: {}".format(self.delayStart)
        print "   Alarm delay: {}".format(self.delayAlarm)
        print "   Exit Criteria:"
        for pf in self.nextProfile:
            print "       {} {}".format(pf['code'],pf['passwd'])
        print "   Devices Of Interest:"
        for di in self.devicesOfInterest:
            print "       {},{},{},{} - Match:{} Period:{}".format(di['source'], di['type'], di['name'], di['cmpState'], di['matching'], di['updatePeriod'])

    def AddNextProfile(self, profileCode, passwdRequired):
        self.nextProfile.append({'code':str(profileCode), 'passwd':bool(passwdRequired)})

    def AddDeviceOfInterest(self, sourceNode, devType, devName, state, matchState, updatePeriod):
        self.devicesOfInterest.append( {
                    'source':sourceNode, 'type':devType, 'name':devName,
                    'cmpState':state, 'matching':matchState, 'updatePeriod':updatePeriod } )

    def SetDelays(self, startDelay, alarmDelay):
        self.delayStart = startDelay
        self.delayAlarm = alarmDelay

    def CopyProfilesFrom(self, src):
        self.nextProfile = []
        for pf in src.nextProfile:
            self.AddNextProfile(pf['code'], pf['passwd'])

    def CopyDevsOfInterest(self, src):
        self.devicesOfInterest = []
        for di in src.devicesOfInterest:
            self.AddDeviceOfInterest(di['source'], di['type'], \
                    di['name'], di['cmpState'], di['matching'], di['updatePeriod'])

    def CopyFrom(self, src):
        self.SetDelays(src.delayStart, src.delayAlarm)
        self.CopyProfilesFrom(src)
        self.CopyDevsOfInterest(src)

