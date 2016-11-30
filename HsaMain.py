#!/usr/bin/env python 

""" 
An echo server that uses select to handle multiple clients at a time. 
Entering any line of input at the terminal will exit the server. 
""" 

from HsaSocketServer import HsaSocketServer
from HsaProfileManager import HsaProfileManager
from HsaMonitor import HsaMonitor
from HsaMsg import HsaStatusType
from HsaDisplay import HsaDisplay
from HsaTextNotifier import HsaTextNotifier
import config
import sys 
import signal
import time
import threading
import logging


def signal_handler():
    print ' '
    print 'Caught Ctrl+c, exiting'
    srvr.stop()
    srvr.join(10)



logger = logging.getLogger("mine")
hdlr = logging.FileHandler('Hsa.log')
FORMAT=logging.Formatter('%(asctime)-15s %(message)s')
hdlr.setFormatter(FORMAT)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def dumps(hsaMsg):
    #print "Source {0}: {1}-{2}-{3}-{4}".format(hsaMsg.conSrc, hsaMsg.msgSrc, hsaMsg.msgType, hsaMsg.msgName, hsaMsg.msgInfo)
    pass

def logInput(hsaMsg):
    msgToLog = "{},{},{},{},{}".format(hsaMsg.msgSrc,hsaMsg.msgType,hsaMsg.msgName,hsaMsg.msgInfo,hsaMsg.msgExtra)
    #logger.info(msgToLog)


srvr = HsaSocketServer()
pM = HsaProfileManager()
mon = HsaMonitor()
dis = HsaDisplay()
srvr.addListen('',50002)
srvr.addListen('',50001)
srvr.addDataObserver(dumps)
srvr.addDataObserver(pM.ReceiveMsg)
srvr.addDataObserver(mon.ReceiveMsg)
#srvr.addDataObserver(logInput)
pM.AddProfileListener(mon.ChangeProfile)
pM.AddProfileListener(dis.ChangeProfile)
mon.AddDevChangeListener(dis.UpdateDeviceChange)
mon.AddStatusChangeListener(dis.UpdateStatus)

def send_line(lineNum, lineText):
    message = "0,101,Line{},{}\n".format(lineNum, lineText)
    srvr.sendToAll(message)

dis.AddOutputSender(send_line)

if 5 < len(config.gvUser) and 1 < len(config.gvPassword):
    tn = HsaTextNotifier(config.gvUser, config.gvPassword)
    pM.AddProfileListener(tn.ProfileListener)
    mon.AddStatusChangeListener(tn.StatusListener)
    for interest in config.textNotifierDestination:
        tn.AddPhoneDest(interest[0], interest[1])

try:
    srvr.start()
    curStatus = HsaStatusType.STANDBY
    while True:
        mon.UpdateStatus()
        srvr.sendToAll("0,100,Status,{}\n".format(mon.GetStatus()))
        dis.SendDisplayUpdate()
        time.sleep(1)
except KeyboardInterrupt:
    signal_handler()
    pass
