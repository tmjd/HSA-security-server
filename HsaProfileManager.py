#!/usr/bin/env python 

""" 
An echo server that uses select to handle multiple clients at a time. 
Entering any line of input at the terminal will exit the server. 
""" 
import config
from HsaProfile import HsaProfile
from HsaUser import HsaUser
from HsaMsg import HsaMsgType

class HsaProfileManager:
    
    def __init__(self):
        self.profile = config.Standby
        self.profileListeners = []

    def AddProfileListener(self, listener):
        self.profileListeners.append(listener)

    def ChangeProfile(self, newProfile):
        self.profile = newProfile
        for lsnr in self.profileListeners:
            lsnr(self.profile)

    def ReceiveMsg(self, msg):
        if msg.msgType != HsaMsgType.INPUT or msg.msgName != "Input":
            #message is not of interest so ignore and exit
            return

        #Use message
        code, passwd = self.SplitInput(msg.msgInfo)

        switchProfile = False
        for pf in self.profile.nextProfile:
            if pf['code'] == code:
                switchProfile = self.PasswordIsGood(pf['passwd'], passwd)
            
        if switchProfile != False:
            self.ChangeProfile(self.GetProfile(code))
            if isinstance(switchProfile, HsaUser):
                print "Change to Profile {} by user {}".format(self.profile.profileName, switchProfile.userName)
            else:
                print "Change to Profile {} password not needed".format(self.profile.profileName)

    def SplitInput(self, inputString):
        if len(inputString) < 3:
            return [0, 0]
        code = inputString[0:3].strip()
        passwd = inputString[3:].strip()
        return [code, passwd]

    def PasswordIsGood(self, required, password):
        if required == True:
            for usr in config.UserList:
                if password == usr.password:
                    return usr
            return False
        else:
            return True

    def GetProfile(self, code):
        for pf in config.ProfileList:
            if pf.profileCode == code:
                return pf
        #If a profile was not found to match then just return the same
        # profile the class is in.
        return self.profile
