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
#

from xml.dom.minidom import parseString, Node
import xml.dom.minidom
import DistributionManager,sys,EmulationManager
import logging


def xmlReader(filename):
    
    logging.debug("This is XML Parser: xmlReader(filename)")
    
    
    
    #open the xml file for reading:
    file = open(filename,'r')
    #convert to string:
    data = file.read()
    #close file because we dont need it anymore:
    file.close()
    #parse the xml you got from the file
    (emulationName,emulationType,emulationLog,emulationLogFrequency, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList)=xmlParser(data)
    return emulationName,emulationType,emulationLog,emulationLogFrequency, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList

def xmlParser(xmlData):
    logging.debug("This is XML Parser: xmlParser(xmlData)")
    emulationLogFrequency = "3"
    emulationLog="0"
    
    ##new##
    #normal values
    dom1 = parseString(xmlData)
    #lower case values
    dom2 = parseString(xmlData.lower())
    domNode=dom2.documentElement
    
    distroList = []


    distributionsXml=dom2.getElementsByTagName('distributions')
    #emulationName=dom2.getElementsByTagName('emulation')[0].getElementsByTagName('emulationName')[0].firstChild.data
    emulationName=dom1.getElementsByTagName('emulation')[0].getElementsByTagName('emuname')[0].firstChild.data
    
    #if <log> block is written in XML file we will find it and read it, if not we will just set default values 
    try:
        emulationLog=dom2.getElementsByTagName('emulation')[0].getElementsByTagName('log')[0].getElementsByTagName('enable')[0].firstChild.data
        
        try:
        
            emulationLogFrequency=dom2.getElementsByTagName('emulation')[0].getElementsByTagName('log')[0].getElementsByTagName('frequency')[0].firstChild.data
        except Exception, e:
            logging.debug("Setting emulationLogFrequency to default value of 3sec")
            
    
    except Exception, e:
        logging.debug("XML Logging is Off")
    
    emulationType=dom2.getElementsByTagName('emulation')[0].getElementsByTagName('emutype')[0].firstChild.data
    startTimeEmu=dom2.getElementsByTagName('emulation')[0].getElementsByTagName('emustarttime')[0].firstChild.data
    resourceTypeEmulation=dom2.getElementsByTagName('emulation')[0].getElementsByTagName('emuresourcetype')[0].firstChild.data
    stopTimeEmu=dom2.getElementsByTagName('emulation')[0].getElementsByTagName('emustoptime')[0].firstChild.data
     
    
    
    logging.debug( "##########################")
    logging.debug("emulation name: "+str(emulationName))
    logging.debug("emulation type: "+str(emulationType))
    logging.debug("resource type: "+str(resourceTypeEmulation))
    logging.debug("start time: "+str(startTimeEmu))
    logging.debug("stop time: "+str(stopTimeEmu))
    logging.debug("##########################")
    
    n=0
    for node in distributionsXml:
        logging.debug("n: "+str(n))
        #Loading distribution type by module (linear, parabola, etc.)
        
        distribution = dom2.getElementsByTagName('distribution')[n]
        distrType = distribution.attributes["name"].value
        
        #getting resource type of distribution CPU,IO,MEM or NET
        resourceTypeDist = dom2.getElementsByTagName('emulator-params')[n].getElementsByTagName('resourcetype')[0].firstChild.data
            
                
        try:
            moduleMethod=DistributionManager.loadDistributionArgNames(distrType)
            
            distroArgsLimitsDict=moduleMethod(resourceTypeDist)
            moduleArgs=distroArgsLimitsDict.keys()
            
            
            logging.debug("moduleArgs:"+str(moduleArgs))
        except IOError, e:
            print "Unable to load module name \"",distrType,"\" error:"
            print e
            sys.exit(0) 
        '''
        loading emulator args
        '''
        #emulator = dom2.getElementsByTagName('emulator')[n]
        #emulatorName = emulator.attributes["name"].value
    
        emulator = dom2.getElementsByTagName('emulator')[n]
        emulatorType = emulator.attributes["name"].value
            
        try:
            logging.debug("trying to load emulatorType:"+str(emulatorType))
            EmulatorModuleMethod=DistributionManager.loadEmulatorArgNames(emulatorType)
            #argNames={"fileQty":{"upperBound":10,"lowerBound":0}}
            emulatorArgsLimitsDict=EmulatorModuleMethod(resourceTypeDist)
            emulatorArgs=emulatorArgsLimitsDict.keys()
            logging.debug("emulatorArgs:"+str(emulatorArgs))
        except IOError, e:
            print "Unable to load module name \"",emulatorType,"\" error:"
            print e
            sys.exit(0)    
        
        
        #get things inside "distributions"
        startTimeDistro = dom2.getElementsByTagName('distributions')[n].getElementsByTagName('starttime')[0].firstChild.data
        durationDistro = dom2.getElementsByTagName('duration')[n].firstChild.data
        granularity= dom2.getElementsByTagName('granularity')[n].firstChild.data
         
        distroArgs={}
        a=0
        #for things in moduleArgs:
        '''
        Getting all the arguments for distribution
        ''' 
        distroArgsNotes=[]
        logging.debug("moduleArgs"+str(moduleArgs))
        
        for args in moduleArgs:
            logging.debug("Inside distribution moduleArgs loop!")
            try:
               
                
                arg0 = dom2.getElementsByTagName('distributions')[n].getElementsByTagName(moduleArgs[a].lower())[0].firstChild.data
                #print "Distro Arg",a," arg Name: ", moduleArgs[a].lower()," arg Value: ",arg0
                
                distributionsLimitsDictValues = distroArgsLimitsDict[moduleArgs[a].lower()]
                #print "boundsCompare(arg0,distributionsLimitsDictValues):",boundsCompare(arg0,distributionsLimitsDictValues)


                checked_distroArgs,checkDistroNote = boundsCompare(arg0,distributionsLimitsDictValues)         
                #print "checked_distroArgs,checkDistroNote",checked_distroArgs,checkDistroNote       
                distroArgsNotes.append(checkDistroNote)
                distroArgs.update({moduleArgs[a].lower():checked_distroArgs})                
                
                
                #distroArgs.update({moduleArgs[a]:arg0})
                a+=1
                #print a, moduleArgs[a]
            except Exception,e:
                    logging.exception("error getting distribution arguments")
                    sys.exit(0)
                    #print e, "setting value to NULL"
                    #arg0="NULL"
                    #print arg0
                    #arg.append(arg0)
                
                
                
                    arg0="NULL"
                    #arg.append(arg0)
                    a= a+1
        '''
        getting all the arguments for emulator
        '''
        emulatorArg={}
        emulatorArgNotes=[]
        a=0
        #for things in moduleArgs:
        logging.debug("emulatorArgs"+str(emulatorArgs))
        for args in emulatorArgs:
            try:
                #print "emulatorArgs[a]",emulatorArgs[a].lower()
                arg0 = dom2.getElementsByTagName('distributions')[n].getElementsByTagName(emulatorArgs[a].lower())[0].firstChild.data
                #print "Emulator Arg",a," arg Name: ", emulatorArgs[a].lower()," arg Value: ",arg0
                #emulatorArgDict={emulatorArgs[a]:arg0}
                
                emulatorLimitsDictValues = emulatorArgsLimitsDict[emulatorArgs[a].lower()]
                #print "boundsCompare(arg0,emulatorLimitsDictValues):",boundsCompare(arg0,emulatorLimitsDictValues,emulatorArgs[a].lower())
                checked_emuargs,check_note = boundsCompare(arg0,emulatorLimitsDictValues,emulatorArgs[a].lower())                
                emulatorArg.update({emulatorArgs[a].lower():checked_emuargs})
                emulatorArgNotes.append(check_note)
                
                #append(emulatorArgs[a]:arg0)
                a+=1
                #print a, moduleArgs[a]
            except Exception, e:
                print e
                logging.exception("Not all emulator arguments are in use, setting Value of "+str(emulatorArgs[a].lower())+" to NULL")
                    #arg0="NULL"
                    #print arg0
                    #arg.append(arg0)
                arg0="NULL"
                emulatorArg.append(arg0)
                a= a+1
        
        logging.debug("emulatorArg:"+str(emulatorArg))
                    #a=a+1
        
        resourceTypeDist = dom2.getElementsByTagName('emulator-params')[n].getElementsByTagName('resourcetype')[0].firstChild.data 
        #dom2.getElementsByTagName('resourceType')[n].firstChild.data
        ##############
        
        #get attributes

        #distributions= dom2.getElementsByTagName('distributions')[n]
        #distributionsName = distributions.attributes["name"].value
        distributionsName=dom1.getElementsByTagName('distributions')[n].getElementsByTagName('name')[0].firstChild.data
        
        emulator = dom1.getElementsByTagName('emulator')[n]
        emulatorName = emulator.attributes["name"].value
        
        ##############
        
        
        #add every emulation in the dictionary
        distroDict={"distributionsName":distributionsName,"startTimeDistro":startTimeDistro,"durationDistro":durationDistro,"granularity":granularity,"distrType":distrType,"distroArgs":distroArgs,"emulatorName":emulatorName,"emulatorArg":emulatorArg,"resourceTypeDist":resourceTypeDist,"emulatorArgNotes":emulatorArgNotes,"distroArgsNotes":distroArgsNotes}
        
       
        
        #print "---->",distributionsName
        #print "start time: ",startTimeDistro
        #print "duration: ",durationDistro
        #print "granularity: ", granularity
        #print "distribution type: ",distrType
                
        distroList.append(distroDict)
        n=n+1
        
        #    CPU-dis-1        Mix          1              3                        Mix               now         180       [{'distroArgs': {'startLoad': u'10', 'stopLoad': u'90'}, 'emulatorName': u'lookbusy', 'distrType': u'linear', 'resourceTypeDist': u'CPU', 'startTimeDistro': u'5', 'distributionsName': u'CPU-dis-1', 'durationDistro': u'170', 'emulatorArg': {'ncpus': u'0'}, 'granularity': u'10'}] 
                                                                                                                                            
    logging.debug("XML Extracted Values:"+str(emulationName)+str(emulationType)+str(emulationLog)+str(emulationLogFrequency)+str(resourceTypeEmulation)+str(startTimeEmu)+str(stopTimeEmu)+str(distroList))
    
    return emulationName,emulationType,emulationLog,emulationLogFrequency, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList


def boundsCompare(xmlValue,LimitsDictValues,variableName = None):
    '''
    Comparing XML variables with emulator or distribution set bounds.
    NOTE: in future might be better moved to the wrapper modules
    '''
    
    if  variableName == "serverip" or variableName == "clientip" or variableName == "packettype":
        return_note ="\nOK"
        return xmlValue,return_note
    
    upperBound=int(LimitsDictValues["upperBound"])
    lowerBound=int(LimitsDictValues["lowerBound"])
    xmlValue=int(xmlValue)
    
    if xmlValue >= lowerBound:
        if xmlValue <= upperBound:
            logging.debug( "1- All OK")#,xmlValue,upperBound,lowerBound
            return_note ="\nOK"
            return xmlValue, return_note
            
        else:
            logging.debug("2- Higher than upperBound taking maximum value")#,xmlValue,upperBound,lowerBound
            return_note ="\nThe scpecified value "+str(xmlValue)+" was higher than the maximum limit "+str(upperBound)+" changing to the maximum limit"
            return upperBound , return_note 
    else:
        logging.debug("3- Lower than lowerBound taking minimum value")#,xmlValue,upperBound,lowerBound
        return_note ="\nThe scpecified value "+str(xmlValue)+" was lower than the minimum limit "+str(lowerBound)+" changing to the maximum limit"
        return lowerBound, return_note

def parse_tests(filename):

    "test"


if __name__ == '__main__':
    
    #filename = "xmldoc.xml"
    #xmlFileReader(filename)
    xmlData='''
<emulation>
  <emuname>NET_emu</emuname>
  <emuType>Mix</emuType>
  <emuresourceType>NET</emuresourceType>
  <emustartTime>now</emustartTime>
  <!--duration in seconds -->
  <emustopTime>15</emustopTime>
  
  <distributions> 
   <name>NET_distro</name>
     <startTime>0</startTime>
     <!--duration in seconds -->
     <duration>10</duration>
     <granularity>1</granularity>
     <distribution href="/distributions/linear" name="linear" />
    <!--cpu utilization distribution range-->
      <startLoad>10</startLoad>
      <stopLoad>10</stopLoad>
      <emulator href="/emulators/iperf" name="iperf" />
    <emulator-params>
        <!--Server/Client-->
        <resourceType>NET</resourceType>
        <serverip>10.55.168.166</serverip>
    <!--Leave "0" for default 5001 port -->
    <serverport>5001</serverport>
        <clientip>10.55.168.167</clientip>
    <!--Leave "0" for default 5001 port -->
    <clientport>5001</clientport>
        <packettype>UDP</packettype>
    </emulator-params>
  </distributions>

  <log>
      <!-- Use value "1" to enable logging(by default logging is off)  -->
      <enable>0</enable>
      <!-- Use seconds for setting probe intervals(if logging is enabled default is 3sec)  -->
      <frequency>3</frequency>
  </log>
  
</emulation>
    
    
    '''
    
    logging.basicConfig(level=logging.DEBUG)
    xmlParser(xmlData)
    
    
    pass