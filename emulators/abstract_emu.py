#Copyright 2012-2013 SAP Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# This is part of the COCOMA framework
#
# COCOMA is a framework for COntrolled COntentious and MAlicious patterns

import sqlite3 as sqlite
import psutil
import sys
from Library import getPIDList
import abc
from abc import ABCMeta

import os
try:
    HOMEPATH= os.environ['COCOMA']
except:
    print "no $COCOMA environmental variable set"

class abstract_emu(object):
    
    __metaclass__ = ABCMeta

@abc.abstractmethod
def emulatorHelp():
    raise NotImplementedError ("'emulatorHelp' method not Implemented in Emulator Class")

@abc.abstractmethod
def emulatorArgNames(Rtype=None):
    raise NotImplementedError ("'emulatorArgNames' method not Implemented in Emulator Class")

def pidFinder(PROCNAME):
    for proc in psutil.process_iter():
        if proc.name == PROCNAME:
            p = proc.pid
#            print "Process found on PID: ",p
            return p

def dbWriter(distributionID,runNo,message,executed):
        #connecting to the DB and storing parameters
        try:
            if HOMEPATH:
                conn = sqlite.connect(HOMEPATH+'/data/cocoma.sqlite')
            else:
                conn = sqlite.connect('./data/cocoma.sqlite')
                
            c = conn.cursor()
                    
            # 1. Populate "emulation"
            c.execute('UPDATE runLog SET executed=? ,message=? WHERE distributionID =? and runNo=?',(executed,message,distributionID,runNo))
            
            conn.commit()
            c.close()
        except sqlite.Error, e:
            print "Error %s:" % e.args[0]
            print e
            sys.exit(1)             

def zombieBuster(PID_ID, processName):
    try:
        wrtiePIDtable(PID_ID, processName)
    except Exception:
        print "unable to write PIDs to DB"
    #catching failed runs
    p = psutil.Process(PID_ID)
    #print "Process name: ",p.name,"\nProcess status: ",p.status
    if str(p.status) =="zombie":
        return True
    else:
        return False
    
def wrtiePIDtable (PID, processName):
    processDict = {"PID": str(PID), "processName": str(processName)}
    if processDict not in getPIDList():
        try:
            if HOMEPATH:
                conn = sqlite.connect(HOMEPATH+'/data/cocoma.sqlite')
            else:
                conn = sqlite.connect('./data/cocoma.sqlite')
            c = conn.cursor()
            sqlCommand = 'INSERT INTO jobPIDs VALUES ("' + str(PID) + '","' + str(processName) + '")' 
            c.execute(sqlCommand)
            conn.commit()
            c.close()
        except sqlite.Error, e:
            print "Error %s:" % e.args[0]
            print e