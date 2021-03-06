#!/usr/bin/env python
# Copyright 2012-2013 SAP Ltd
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
#


import imp,time,sys,os,EmulationManager
import datetime as dt
import sqlite3 as sqlite
import logging
import EMQproducer, Library
from EMQproducer import Producer
from Distribution import distribution
from Logger import singleLogger

import Pyro4
Pyro4.config.HMAC_KEY='pRivAt3Key'
#Pyro4.config.SERIALIZER='pickle'
#perhaps needs to be set somewhere else

distLoggerDM=None

global producer
producer = Producer()
# EMQproducer.StreamAndBroadcastHandler("Distribution Manager",producer,logging.INFO)

global HOMEPATH
HOMEPATH = Library.getHomepath()
   

def createDistribution(newEmulation):
    daemon=Library.getDaemon()
    
    global producer
    if producer is None:
        # print "In distributionManager, copying producer"
        producer = producer()

    # print "Who calls "+sys._getframe(0).f_code.co_name+": "+sys._getframe(1).f_code.co_name
#    distLoggerDM = ""
    
    # if distLoggerDM is None:
    #        distLoggerDM=Library.loggerSet("Distribution Manager",str(newEmulation.emulationID)+"-"+str(newEmulation.emulationName)+"-syslog"+"_"+str(newEmulation.startTimeEmu)+".csv")



    # connecting to the DB and storing parameters
    loggerJobReply = "No logger scheduled"
    try:

        conn = Library.dbconn()
        c = conn.cursor()
                
        # 1. Populate "emulation"
        c.execute('INSERT INTO emulation (emulationName,emulationType,resourceType,active,logging,logFrequency,logLevel,xmlData) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [newEmulation.emulationName, newEmulation.emulationType, newEmulation.resourceTypeEmulation, 1, newEmulation.emulationLog, newEmulation.emulationLogFrequency, newEmulation.emulationLogLevel, newEmulation.xmlData])
        newEmulation.setEmulationID(c.lastrowid)
        # start logger here once we know emulation ID
#        distLoggerDM = singleLogger("Distribution Manager", None, str(newEmulation.emulationID) + "-" + str(newEmulation.emulationName) + "-syslog" + "_" + str(newEmulation.startTimeEmu) + ".csv")
        
        c.execute('UPDATE emulation SET emulationName=? WHERE emulationID =?', (str(newEmulation.emulationID) + "-" + newEmulation.emulationName, newEmulation.emulationID))
        
        # 2. We populate "emulationLifetime" table  
        c.execute('INSERT INTO emulationLifetime (startTime,stopTime,emulationID) VALUES (?,?,?)', [newEmulation.startTimeEmu, newEmulation.stopTimeEmu, newEmulation.emulationID])
        emulationLifetimeID = c.lastrowid

        newEmulation.setEmulationLifetimeID(emulationLifetimeID)
        c.execute('UPDATE emulationLifetime SET stopTime=? WHERE emulationLifetimeID =?',(newEmulation.stopTimeEmu,emulationLifetimeID))
        c.execute('UPDATE emulation SET emulationLifetimeID=? WHERE emulationID=?',(emulationLifetimeID,newEmulation.emulationID))
        
        conn.commit()
        c.close()
        
        """
        # Here we create runs
        """

#        raise Exception ("newEmulation.emulationLog = " + str(newEmulation.emulationLog))
        if newEmulation.emulationLog == "1":
            
            # creating run for logger with probe interval of 2 seconds
            distLoggerDM = singleLogger("Distribution Manager", None, str(newEmulation.emulationID) + "-" + str(newEmulation.emulationName) + "-syslog" + "_" + str(newEmulation.startTimeEmu) + ".csv")
            interval = int(newEmulation.emulationLogFrequency)
            singleRunStartTime = Library.timeConv(newEmulation.startTimeEmu)
            loggerJobReply = daemon.createLoggerJob(singleRunStartTime, newEmulation.stopTimeEmu, interval, newEmulation.emulationID, newEmulation.emulationName, newEmulation.startTimeEmu)       
        
        createEndJob(daemon, newEmulation)
        
    except sqlite.Error, e:
        print e
        return "SQL error:", e
        sys.exit(1)
    
    createDistributionRuns(newEmulation)

def createEndJob (daemon, newEmulation):
    returnEmulationName = (str(newEmulation.emulationID) + "-" + newEmulation.emulationName)
    #Calcualte when the end job should be (start + duration +1) //+1 is to allow for delay in scheduler starting emulation 
    emulationEndTime = (Library.timeConv(newEmulation.startTimeEmu)) + dt.timedelta(0, (float(newEmulation.stopTimeEmu) + 1))
    emulationEndJobReply = daemon.createEmulationEndJob(emulationEndTime, returnEmulationName)

def createDistributionRuns(newEmulation):
    daemon=Library.getDaemon()
    daemon.setEmuObject(newEmulation)
    
    for distro in newEmulation.distroList:

        if distro.getDistributionID() != "none":
            #do nothing continue to next element, because this distribution was already scheduled.
            print "Already scheduled"

        else:
                        
            try:
                conn = Library.dbconn()
                c = conn.cursor()
                    
                # 1. We populate "distribution" table      
                c.execute('INSERT INTO distribution (distributionGranularity, distributionType,emulator,distributionName,startTime,duration,emulationID) VALUES (?, ?, ?, ?,?, ?,?)', [distro.granularity, distro.type, distro.emulatorName,distro.name,distro.startTime,distro.duration,newEmulation.emulationID])
                distro.setDistributionID(c.lastrowid)
                daemon.setEmuObject(newEmulation)
                '''
                {'startLoad': u'10', 'stopLoad': u'90'}
                '''
                #print "distributionArg:", distributionArg
                #print "emulatorArg:",emulatorArg
                
                #2. populate DistributionParameters, of table determined by distributionType name in our test it is "linearDistributionParameters"
                for d in distro.distroArgs :
                    c.execute('INSERT INTO DistributionParameters (paramName,value,distributionID) VALUES (?, ?, ?)',[d,distro.distroArgs[d],distro.ID])
                distributionParametersID=c.lastrowid
                
                
                c.execute('UPDATE distribution SET distributionParametersID=? WHERE distributionID =?',(distributionParametersID,distro.ID))
                
                
                for emu in distro.emulatorArg :
                    c.execute('INSERT INTO EmulatorParameters (paramName,value,resourceType,distributionID) VALUES (?, ?, ?,?)',[emu,distro.emulatorArg[emu],distro.resourceType,distro.ID])
                distributionParametersID=c.lastrowid
                
                conn.commit()
                c.close()
            except sqlite.Error, e:
                print "Error %s:" % e.args[0]
                print e
                sys.exit(1)                        
                   
            startTime= Library.timeConv(newEmulation.startTimeEmu)
            startTimesec=time.mktime(startTime.timetuple()) + float(distro.startTime)
            #making sure that the run after event has valid date for scheduling
            nowTime = Library.timeSinceEpoch(5)
            if startTimesec < nowTime:
                startTimesec = nowTime + float(distro.startTime)
                
            '''
            1. Load the module according to Distribution Type to create runs
            '''
    
            #1. Get required module loaded
            modhandleMy=Library.loadDistribution(distro.type)
            #Check if error returned
            if (type(modhandleMy) is str):
                raise Exception (modhandleMy)
             
            #2. Use this module for calculation and run creation   
            stressValues,runStartTime,runDurations,triggerType=modhandleMy(newEmulation.emulationID,newEmulation.emulationName,newEmulation.getEmulationLifetimeID(),startTimesec,distro.duration, int(distro.granularity),distro.distroArgs,distro.resourceType,HOMEPATH)

            if (distro.type != "event"): #event distributions don't require a minjobtime
                try:
                    if (distro.distroArgs.has_key("minjobtime")):
                        minJobTime = distro.distroArgs["minjobtime"]
                    else:
                        minJobTime = 2
                    (stressValues, runStartTime, runDurations) = Library.checkMinJobTime(distro.name, stressValues, runStartTime, runDurations, distro.distroArgs["minjobtime"])
                except Exception, e:
                    print "Could not enforce minimum job time. " + str(e)

            runStartTime = Library.staggerStartTimes(runStartTime)
            (stressValues, runStartTime, runDurations) = Library.removeZeroJobs(stressValues, runStartTime, runDurations) #Remove jobs with a stressValue of 0
            #event and time type disro's separation
            try :
                    n=0
                    for vals in stressValues:
                        #print "stressValues: ",vals
                        try:
                            #print "Things that are sent to daemon:\n",emulationID,emulationName,distributionName,emulationLifetimeID,runDurations[n],emulator,emulatorArg,resourceTypeDist,vals,runStartTime[n],str(n)
                            daemon.hello()
                            #Sending emulation name already including ID stamp
                            emulationNameID =str(newEmulation.emulationID)+"-"+str(newEmulation.emulationName)
                            
                            schedulerReply = str(daemon.createJob(newEmulation.emulationID,emulationNameID,distro.ID,distro.name,newEmulation.getEmulationLifetimeID(),runDurations[n],distro.emulatorName,distro.emulatorArg,distro.resourceType,vals,runStartTime[n],str(n),runDurations[n]))
                            distLoggerDM=singleLogger("Distribution Manager",None,str(newEmulation.emulationID)+"-"+str(newEmulation.emulationName)+"-syslog"+"_"+str(newEmulation.startTimeEmu)+".csv")
                            distLoggerDM.info("Job Created: "+schedulerReply)
            
                            
                            
                            #adding values to the table for recovery
                            try:
                                conn = Library.dbconn()
                                c = conn.cursor()
                                    
                                # 1. We populate "distribution" table :stressValue,runStartTime,runNo     
                                c.execute('INSERT INTO runLog (executed, stressValue, runStartTime,runNo,distributionID, runDuration) VALUES (?, ?, ?, ?, ?,?)', ["Pending", vals, runStartTime[n],str(n),distro.ID,runDurations[n]])
                           
                                conn.commit()
                                c.close()
                            except sqlite.Error, e:
                                print "Error %s:" % e.args[0]
                                print e
                                sys.exit(1)                         
                            
                            n= n+1
                            
                            
                            
                        except  Pyro4.errors.CommunicationError, e:
                            print e
                            print "\n---Check if SchedulerDaemon is started. Connection error cannot create jobs---"
                            
                
                    if triggerType=="time":
                        #schedule the next distro right after this will end 
                        pass#maybe break
                    else:
                        raise Exception("Found trigger type '%s' in distribution '%s'.Stopping job scheduling" % (triggerType,distro.name))    
        
            except Exception, e:
                #send copy of emulation object to daemon
                print "set emu exception:",e
                daemon.setEmuObject(newEmulation)            
                break
                #"do something with remaining distributions to transfer them to the end of event driven distro"    
                

if __name__ == "__main__":
    
    pass