#!/usr/bin/env python 

""" 
An echo server that uses select to handle multiple clients at a time. 
Entering any line of input at the terminal will exit the server. 
""" 

import sys 
import signal
import time
from HsaProfile import HsaProfile
from HsaUser import HsaUser
from HsaMsg import HsaStatusType

ProfileList = []
UserList = []


user1 = HsaUser("Fred", 1111)
UserList.append(user1)
user2 = HsaUser("Janice", 2222)
UserList.append(user2)
user3 = HsaUser("Steven", 3333)
UserList.append(user3)

HomeGen = HsaProfile("Home", 711)
HomeGen.SetDelays(15, 15)
HomeGen.AddNextProfile(711, True)
HomeGen.AddNextProfile(713, True)
HomeGen.AddNextProfile(111, True)
HomeGen.AddNextProfile(811, True)
#The 911 profile (alarm ASAP) does not need a password to enter
HomeGen.AddNextProfile(911, False)
HomeGen.AddDeviceOfInterest(1,1,'Front Door','clr',True,10)
HomeGen.AddDeviceOfInterest(1,1,'Back Door','clr',True,10)
HomeGen.AddDeviceOfInterest(1,1,'Garage Door','clr',True,10)
ProfileList.append(HomeGen)

HomeBed = HsaProfile("Bedtime", 713)
HomeBed.CopyFrom(HomeGen)
HomeBed.AddDeviceOfInterest(1,2,'Main Floor Mtn','clr',True,10)
HomeBed.AddDeviceOfInterest(1,2,'Basement Mtn','clr',True,10)
HomeBed.AddDeviceOfInterest(3,2,'Main Panel Mtn', 'clr', True, 10)
ProfileList.append(HomeBed)

Away = HsaProfile("Away", 811)
Away.CopyProfilesFrom(HomeGen)
# Delay for 30 seconds before start and wait 30 seconds before alarming so
# we can put in the code to disarm.
Away.SetDelays(30, 30)
Away.AddDeviceOfInterest(1,1,'Front Door','clr',True,10)
Away.AddDeviceOfInterest(1,1,'Back Door','clr',True,10)
Away.AddDeviceOfInterest(1,1,'Garage Door','clr',True,10)
Away.AddDeviceOfInterest(1,2,'Basement Mtn','clr',True,10)
Away.AddDeviceOfInterest(2,2,'Upstairs Mtn','clr',True,10)
#The away profile cannot have the motion sensors active because
# the dog trips them
#Away.AddDeviceOfInterest(1,2,'Main Floor Mtn','clr',True,10)
#Away.AddDeviceOfInterest(3,2,'Main Panel Mtn', 'clr', True, 10)
ProfileList.append(Away)

NineOneOne = HsaProfile("911", 911)
NineOneOne.SetDelays(0, 0)
NineOneOne.AddNextProfile(711, True)
NineOneOne.AddNextProfile(713, True)
NineOneOne.AddNextProfile(111, True)
NineOneOne.AddNextProfile(811, True)
NineOneOne.AddNextProfile(911, False)
#Add one device to trip the alarm off of
NineOneOne.AddDeviceOfInterest(1,1,'Front Door','nothing',False,10)
ProfileList.append(NineOneOne)

Standby = HsaProfile("Standby", 111)
#From Standby any profile can be entered without a password
Standby.AddNextProfile(711, False)
Standby.AddNextProfile(713, False)
Standby.AddNextProfile(111, False)
Standby.AddNextProfile(811, False)
Standby.AddNextProfile(911, False)
ProfileList.append(Standby)

gvUser = "google.voice@real.address.net"
gvPassword = "PasswordForTheAbove"
# Phone numbers to notify and the statuses and profiles to notify them about
textNotifierDestination = [ [ "1234567890", [ HsaStatusType.ALARMED, Away.profileName, \
                                              NineOneOne.profileName, HomeGen.profileName,\
                                              HomeBed.profileName, Standby.profileName] ],\
                            [ "2345678901", [ HsaStatusType.ALARMED ] ] \
                            ]

if __name__ == "__main__":
    print "---- Users ----"
    for usr in UserList:
        usr.ShowMe()
    print "---- Profiles ----"
    for pf in ProfileList:
        pf.ShowMe()
