#Copyright 2012 SAP Ltd
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

import math
import Pyro4,imp,time,sys
import sqlite3 as sqlite
import datetime as dt
#perhaps needs to be set somewhere else
Pyro4.config.HMAC_KEY='pRivAt3Key'


class distributionMod(object):
    
    
    def __init__(self,emulationID,emulationName,emulationLifetimeID,startTimesec,duration, distributionGranularity,distributionArg,HOMEPATH):
        
        self.startLoad = distributionArg["startLoad"]
        self.stopLoad = distributionArg["stopLoad"]
        
        distributionGranularity_count=distributionGranularity
        #startTimesec = startTimesec
        duration = float(duration)
        
        runNo=int(0)
        
        print "Hello this is dist_linear"
        print "emulationID,emulationName,emulationLifetimeID,startTimesec,duration, distributionGranularity,arg,HOMEPATH",emulationID,emulationName,emulationLifetimeID,startTimesec,duration, distributionGranularity,distributionArg,HOMEPATH
        

def functionCount(emulationID,emulationName,emulationLifetimeID,startTimesec,duration, distributionGranularity,distributionArg,HOMEPATH):
    
    startLoad = distributionArg["startLoad"]
    stopLoad = distributionArg["stopLoad"]
    
    distributionGranularity_count=distributionGranularity
    #startTimesec = startTimesec
    duration = float(duration)
    
    runNo=int(0)
    
    
    stressValues = []        
    runStartTimeList=[]      
                
    while(distributionGranularity_count>=0):
    
            print "Run No: "
            print runNo
            print "self.startTimesec",startTimesec
            runStartTime=startTimesec+(duration*runNo)
            
            
            runStartTimeList.append(runStartTime)
            print "This run start time: "
            print runStartTime
            print "This is time passed to scheduler:"
            print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(runStartTime))
        
            '''
            1. Distribution formula goes here
            '''
                            
            linearStep=((int(startLoad)-int(stopLoad))/int(distributionGranularity))
            linearStep=math.fabs((int(linearStep)))
            print "LINEAR STEP SHOULD BE THE SAME"
            print linearStep
            linearStress= ((linearStep*int(runNo)))+int(startLoad)
            #make sure we return integer
            linearStress=int(linearStress)
            print "LINEAR STRESS SHOULD CHANGE"
            print linearStress
            
            
            
            
            stressValues.append(linearStress)
            print "This run stress Value: "
            print stressValues
            
            print "runStartTimeList",runStartTimeList
             
            #increasing to next run            
            runNo=int(runNo)+1
            
        
            print "distributionGranularity_count:"
            distributionGranularity_count= int(distributionGranularity_count)-1
            print distributionGranularity_count
        
    return stressValues, runStartTimeList
    
    
def distHelp():
    
    print "Linear Distribution How-To:"
    print "Enter arg0 for first point and arg1 for 2nd point"
    
    print "Have fun"
    
'''
here we specify how many arguments distribution instance require to run properly
'''
def argNames():
    
    argNames=["startLoad","stopLoad"]
    print "Use Arg's: ",argNames
    return argNames

