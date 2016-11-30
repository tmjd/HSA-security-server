#!/usr/bin/env python 

import config
from HsaMsg import HsaStatusType
from googlevoice import Voice

""" 
Used to manage the alarm profiles.  Each profile consists of a name, id/code,
time to delay before checking mode, time delay before alarming after a disturbance,
devices of interest in the mode, and the possible profile codes to switch to and if
a password is required to switch to that mode.
""" 

class HsaTextNotifier:

    def __init__(self, email, password):
        self.voice = Voice()
        self.email = email
        self.password = password
        self.numbers = []
        self.interests = []
        self.profile = config.Standby
        self.status = HsaStatusType.STANDBY

    def StatusListener(self, status):
        for index in range(len(self.numbers)):
            if self.status != status \
               and  status in self.interests[index]:
                self.SendMsg(self.numbers[index], \
                    "Status changed to "+status+" in profile "+self.profile.profileName)
        self.status = status

    def ProfileListener(self, profile):
        for index in range(len(self.numbers)):
            if self.profile != profile \
               and profile.profileName in self.interests[index]:
                self.SendMsg(self.numbers[index], "Profile changed to "+profile.profileName)
        self.profile = profile

    def AddPhoneDest(self, number, changeOfInterest):
        self.numbers.append(number)
        self.interests.append(changeOfInterest)

    def SendMsg(self, number, msg):
        try:
            self.voice.login(self.email,self.password)

            self.voice.send_sms(number, msg)

            self.voice.logout()
        except:
            print "Error with text notification"
            

if __name__ == "__main__":
    gvInterface = HsaTextNotifier("googlevoiceaddress@gmail.com","passwordToLogin")
    gvInterface.AddPhoneDest("314xxxxxxx", [ "Alarmed", "Bedtime" ])
    gvInterface.ProfileListener(config.HomeGen)
    gvInterface.StatusListener("Armed")
    #gvInterface.StatusListener("Alarmed")
    gvInterface.ProfileListener(config.Standby)
    gvInterface.StatusListener("Armed")
    gvInterface.ProfileListener(config.HomeBed)
    
