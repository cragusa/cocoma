#!/usr/bin/env python
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



import optparse,sys,Pyro4,os,ConfigParser
import sqlite3 as sqlite
#import argparse - new version of optparse
import EmulationManager,XmlParser,DistributionManager,subprocess


Pyro4.config.HMAC_KEY='pRivAt3Key'


def main():
    
    uri ="PYRO:scheduler.daemon@localhost:51889"
    #perhaps needs to be setup somewhere else
    
    daemon=Pyro4.Proxy(uri)    

    #Trying to group things
    parser = optparse.OptionParser()
    
    listEmu = optparse.OptionGroup(parser, 'List existing emulations')
    listEmu.add_option('-l', '--list', action='store_true', default=False,dest='listAll',help='[emulationID] [all]  List of emulations by ID or all')
    listEmu.add_option('--list-name', action='store_true', default=False,dest='listName', help='[emulationName] List of emulations by name')
    listEmu.add_option('--list-active', action='store_true', default=False,dest='listActive', help='List of active emulations')
    listEmu.add_option('--list-inactive', action='store_true', default=False,dest='listInactive', help='List of inactive emulations')
    listEmu.add_option('--list-jobs', action='store_true', default=False,dest='listJobs', help='List of active Jobs running on Scheduler daemon')
        
    
    createEmu = optparse.OptionGroup(parser, 'Create new emulations')
    createEmu.add_option('-x', '--xml', action='store_true', dest='xml',default=False, help='[file.xml] enter name XML document')
    createEmu.add_option('-n', '--now', action='store_true', dest='emuNow',default=False, help='[-x filename -n minutes] enter duration only and emulation starts immediately')
    
    updateEmu = optparse.OptionGroup(parser, 'Update emulations')
    updateEmu.add_option('-u', '--update', action='store_true', dest='updateID',default=False, help='Update already created emulation. Usage: -u [emulationID] [emulationName] [distributionType] [resourceType] [emulationType] [startTime] [stopTime] [distributionGranularity] [startLoad] [stopLoad] . If no value needs to be changed enter NULL')
    
    
    deleteEmu = optparse.OptionGroup(parser, 'Delete emulations')
    deleteEmu.add_option('-d', '--delete', action='store_true',default=False, dest='deleteID', help='[emulationID] Deletes full emulation')
    deleteEmu.add_option('--purge', action='store_true',default=False, dest='purge_all', help='[all] clears everything. !!USE WITH CAUTION!!')
    
    listDistro = optparse.OptionGroup(parser, 'List available distributions')  
    listDistro.add_option('-i', '--dist', action='store_true', default=False,dest='listAllDistro',help='[all]  List of all available distributions')
    listDistro.add_option('--dist-help', action='store_true', default=False,dest='listDistroOptions',help='[name]  List of all available distribution arguments')
    
    serviceControl = optparse.OptionGroup(parser, 'Services Control')
    serviceControl.add_option('--start', action='store_true', default=False,dest='startServices',help='[scheduler][api] start services')
    serviceControl.add_option('--stop', action='store_true', default=False,dest='stopServices',help='[scheduler][api] stop services')
    serviceControl.add_option('--show', action='store_true', default=False,dest='showServices',help='[scheduler][api] show services')
    
    listEmulator = optparse.OptionGroup(parser, 'List available emulators')  
    listEmulator.add_option('-e', '--emu', action='store_true', default=False,dest='listAllEmulators',help='[all]  List of all available emulators')
    listEmulator.add_option('--emu-help', action='store_true', default=False,dest='listEmulatorOptions',help='[name]  List of all available emulator arguments')
    
    
    
        
    parser.add_option_group(listEmu)
    parser.add_option_group(listDistro)
    parser.add_option_group(listEmulator)
    parser.add_option_group(createEmu)
    parser.add_option_group(deleteEmu)
    parser.add_option_group(updateEmu)
    parser.add_option_group(serviceControl)
       

    options, arguments = parser.parse_args()
    #catch empty arguments
    if len(arguments)>0:
        
        '''
        ################################
        updateEmu
        ###############################
        '''
        
        if options.updateID and len(arguments) ==10:
              
            emulationID=arguments[0]
            emulationName=arguments[1]
            distributionType=arguments[2]
            resourceType=arguments[3]
            emulationType=arguments[4]
            startTime=arguments[5]
            stopTime=arguments[6]
            distributionGranularity=arguments[7]
            startLoad=arguments[8]
            stopLoad=arguments[9]
            print options
            print arguments
            EmulationManager.updateEmulation(emulationID,emulationName,distributionType,resourceType,emulationType,startTime,stopTime, distributionGranularity,startLoad, stopLoad)
        
        if options.updateID and len(arguments) !=10:
            parser.print_help()
        
        '''
        ################################
        serviceControl
        ###############################
        '''
        
        if options.startServices:
            if arguments[0] == "scheduler":
                print "Starting ",arguments[0]
                EmulationManager.services_control("scheduler","start"," ")
     
            if arguments[0] == "api":
                
                try:
                    print "Starting ",arguments[0],"on interface ",arguments[1]
                    EmulationManager.services_control("api","start",arguments[1])
                except:
                    print "Starting ",arguments[0],"on interface eth0"
                    EmulationManager.services_control("api","start","eth0")
 
                    
        if options.stopServices:
            if arguments[0] == "scheduler":
                EmulationManager.services_control("scheduler","stop"," ")
            
            if arguments[0] == "api":
                EmulationManager.services_control("api","stop"," ")
                
        if options.showServices:
            if arguments[0] == "scheduler":
                EmulationManager.services_control("scheduler","show"," ")
            
            if arguments[0] == "api":
                EmulationManager.services_control("api","show"," ")
                  
                
                    
                #2.check if pid is running
                #3.execute os.system("kill "+str(procAPI.pid))
                


                    
        '''
        ################################
        listEmu
        ###############################
        '''
                  
        if options.listActive:
            EmulationManager.getEmulation("NULL","NULL",1,1)
            sys.exit(1)
         
        if options.listInactive:
            EmulationManager.getEmulation("NULL","NULL",1,0)
            sys.exit(1)
        
       
        if options.listAll:
            if arguments[0]=="all":
                EmulationManager.getEmulation("NULL","NULL",1,"NULL")
            else:
                EmulationManager.getEmulation("NULL",arguments[0],0,"NULL")
                    
        if options.listJobs:
            connectionCheck=daemonCheck()
            if  connectionCheck !=1:
                sys.exit(1) 
                
            if arguments[0]=="all":
                try:
                    for job in daemon.listJobs():
                    
                        print job
                except :
                    print "\nNo jobs are scheduled\n"
                    
            else:
                
                for job in daemon.listJobs():
                    if job.name==arguments[0]:
                        print job
        
        if options.listName:
            EmulationManager.getEmulation(arguments[0],"NULL",0,"NULL")
                
        if options.listActive:
            if arguments[0]=="all":
                #TO-DO: List inactive values with 0 param
                print "Listing all active values"
                EmulationManager.getEmulation("NULL","NULL",0,1)



        '''
        ################################
        deleteEmu
        ###############################
        '''


                  
        if options.deleteID:
            #TO-DO: List inactive values with 0 param
            print "Deleting ID: ",arguments[0]
            EmulationManager.deleteEmulation(arguments[0])
        
        
        if options.purge_all:
            print "this is purge all ccmsh"
            if arguments[0]=="all":
                EmulationManager.purgeAll()
        


        '''
        ################################
        listDistro
        ###############################
        '''




        if options.listAllDistro:
            distroList=DistributionManager.listDistributions("all")
            print "\nThese are available distributions:"
            for distName in distroList:
                print distName
        
        if options.listDistroOptions:
            print "This is listDistroOptions"
            #1. check name
            EmulationManager.distributionTypeCheck(arguments[0])
            #2. Load module
            distroModHelp=DistributionManager.loadDistributionHelp(arguments[0])
            #3. Call distHelp()
            print "\n"
            distroModHelp()
            print "\n"
            


        '''
        ################################
        createEmu
        ###############################
        '''

        
              
        if options.xml and not options.emuNow:  
                #(emulationName, emulationType, resourceTypeEmulation, startTimeEmu, distroList) = XmlParser.xmlReader(arguments[0])
                #print "CCMSH:",emulationName, emulationType, distroList
                (emulationName,emulationType, resourceTypeEmulation, startTimeEmu, distroList) = XmlParser.xmlReader(arguments[0])
                if startTimeEmu.lower() =="now":
                    (startTimeEmu1, stopTime) = EmulationManager.emulationNow(1)
                    EmulationManager.createEmulation(emulationName, emulationType, resourceTypeEmulation, startTimeEmu1, distroList)
                else:
                    EmulationManager.createEmulation(emulationName, emulationType, resourceTypeEmulation, startTimeEmu, distroList)
                
                
                #EmulationManager.dataCheck(startTime,stopTime)
                #EmulationManager.distributionTypeCheck(distributionType)
                #EmulationManager.DistributionArgCheck(distributionType,arg)
                #EmulationManager.createEmulation(emulationName, distributionType, resourceType, emulationType, startTime, stopTime,emulator, distributionGranularity,arg)
        
        if options.emuNow and options.xml:
            print "Starting Now"
            #just giving random value at the moment
            arguments[1] = 1
            
            (emulationName,emulationType, resourceTypeEmulation, startTimeEmu, distroList) = XmlParser.xmlReader(arguments[0])
            (startTimeEmu, stopTime) = EmulationManager.emulationNow(arguments[1])
            EmulationManager.createEmulation(emulationName, emulationType, resourceTypeEmulation, startTimeEmu, distroList)
            #(emulationName, distributionType, resourceType, emulationType, startTime0, stopTime0,emulator, distributionGranularity,arg) = XmlParser.xmlReader(arguments[0])
            #EmulationManager.createEmulation(emulationName, distributionType, resourceType, emulationType, startTime, stopTime,emulator, distributionGranularity,arg)
            
        
    else:
        parser.print_help()

        
def daemonCheck():
    '''
    Checking if Scheduler Daemon is started
    '''
    uri ="PYRO:scheduler.daemon@localhost:51889"
    #perhaps needs to be setup somewhere else
    
    daemon=Pyro4.Proxy(uri)
    
    try:
        
        print daemon.hello()
        return(1)
    
    except  Pyro4.errors.CommunicationError, e:
        
        
        print e
        print "\n---Check if Scheduler Daemon is started. Connection error---"
        
        return (0)
        
    
    

if __name__ == '__main__':
    main()

