#!/usr/bin/env python 

""" 
""" 

class HsaUser:

    def __init__(self, name, password):
        self.userName = name
        self.password = str(password)

    def ShowMe(self):
        print "User name: {} password: {}".format(self.userName, self.password)

