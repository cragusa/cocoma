#!/usr/bin/env python
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



from bottle import route, run,response,request,re
from bottle import *
import sys,os, time, Pyro4, glob
from datetime import datetime as dt
import EmulationManager,ccmsh,DistributionManager,XmlParser
from json import dumps
from xml.etree import ElementTree
from xml.dom import minidom
import xml.etree.ElementTree as ET
import zipfile, Library
from twisted.persisted.aot import prettify

PORT_ADDR=0
IP_ADDR=0
INTERFACE=""
#Pyro4.config.HMAC_KEY='pRivAt3Key'



try:
    HOMEPATH= os.environ['COCOMA']
except:
    print "no $COCOMA environmental variable set"


def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, encoding="utf-8", method='xml')
    
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


'''
#######
COCOMA ROOT
#######
'''
@route('/', method ="GET")
def get_root():
    '''
    Shows list of resources available at root location
    '''
    #curl -k -i http://10.55.164.232:8050/
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD') 
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    
    root = ET.Element('root', { 'href':'/'})
    ver = ET.SubElement(root, 'version')
    ver.text = '0.1.1'
    ts = ET.SubElement(root, 'timestamp')
    ts.text = str(time.time())
    lk = ET.SubElement(root, 'link', {'rel':'emulations', 'href':'/emulations', 'type':'application/vnd.bonfire+xml'})
    lk = ET.SubElement(root, 'link', {'rel':'emulators', 'href':'/emulators', 'type':'application/vnd.bonfire+xml'})
    lk = ET.SubElement(root, 'link', {'rel':'distributions', 'href':'/distributions', 'type':'application/vnd.bonfire+xml'})
    lk = ET.SubElement(root, 'link', {'rel':'tests', 'href':'/tests', 'type':'application/vnd.bonfire+xml'})
    lk = ET.SubElement(root, 'link', {'rel':'results', 'href':'/results', 'type':'application/vnd.bonfire+xml'})
    lk = ET.SubElement(root, 'link', {'rel':'logs', 'href':'/logs', 'type':'application/vnd.bonfire+xml'})
    lk = ET.SubElement(root, 'link', {'rel':'jobs', 'href':'/jobs', 'type':'application/vnd.bonfire+xml'})

    return prettify(root)
    

'''
#######
GET emulation
#######
'''

#webpage host #ronan killough

@route('/<filename>')
def server_static(filename):
    
    return static_file(filename, root= HOMEPATH+'/bin/webcontent')
    
       



@route('/emulations/', method ='GET')
@route('/emulations', method ='GET')
def get_emulations():
    '''
    Displays list of emulations that were created/scheduled
    '''
    
    
    response.set_header('Allow', 'GET, HEAD, POST')
    response.set_header('Accept', '*/*')
    emuList=Library.getEmulationList("all")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    
    '''
    XML namespaces are used for providing uniquely named elements and attributes in an XML document.
    '''
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    
    #building the XML we will return
    emulations = ET.Element('collection', { 'xmlns':'http://127.0.0.1/cocoma','href':'/emulations'})
    #<items offset="0" total="2">
    items =ET.SubElement(emulations,'items', { 'offset':'0','total':str(len(emuList))})
    
    #<emulator href="/emulations/1" name="Emu1"/>
    
    for elem in emuList :
        emulation = ET.SubElement(items,'emulation', { 'href':'/emulations/'+str(elem["Name"]),'id':str(elem["ID"]),'name':str(elem["Name"]),'state':str(elem["State"])})
        
    
    #<link href="/" rel="parent" type="application/vnd.cocoma+xml"/>
    lk = ET.SubElement(emulations, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
    
    

    return prettify(emulations)

@route('/emulations/<name>/', method='GET')
@route('/emulations/<name>', method='GET')
def get_emulation_details(name=""):
    '''
    Display specific emulation details by name
    '''
    #curl -k -i http:///10.55.164.232:8050/emulations/1
    
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD') 
    
    try:
        (emulationID,emulationName,emulationType, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData,logging,logFrequency,logLevel,enabled,vhost,exchange,user,password,host,topic)=EmulationManager.getEmulation(name)
    
    except Exception,e:
            
        response.status = 404
        return "<error>Emulation Name: "+name+" not found. Error:"+str(e)+"</error>"
        
    print "Creating Response xml"
    #[{'emulatorName': u'lookbusy', 'distroArgs': {u'startload': u'10', u'stopload': u'95'}, 
    #'distrType': u'linear', 'resourceTypeDist': u'cpu', 'distributionsID': 1, 'startTimeDistro': u'0',
    # 'distributionsName': u'CPU_distro', 'durationDistro': u'10',
    # 'emulatorArg': {u'ncpus': u'0'}, 'granularity': 1}]
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    
    #building the XML we will return
    emulation = ET.Element('emulation', { 'xmlns':'http://127.0.0.1/cocoma','href':'/emulations/'+str(name)})
    #<id>1</id>
    idXml =ET.SubElement(emulation,'id')
    idXml.text = str(emulationID)
    #<emulationName>myMixEmu</emulationName>
    emulationNameXml =ET.SubElement(emulation,'emulationName')
    emulationNameXml.text = str(emulationName)
    
    #<emulationType>Mix</emulationType>
    emulationTypeXml =ET.SubElement(emulation,'emulationType')
    emulationTypeXml.text = str(emulationType)
    
    #<resourceType>Mix</resourceType>
    resourceTypeXml =ET.SubElement(emulation,'resourceType')
    resourceTypeXml.text = str(resourceTypeEmulation)
    
    #<startTime>now</startTime>
    startTimeEmuXml =ET.SubElement(emulation,'emuStartTime')
    startTimeEmuXml.text = str(startTimeEmu)    
    
    #<stopTime>now+180</stopTime>
    stopTimeEmuXml =ET.SubElement(emulation,'emuStopTime')
    stopTimeEmuXml.text = str(stopTimeEmu)
    
    scheduledJobsXml = ET.SubElement(emulation,'scheduledJobs')
    uri ="PYRO:scheduler.daemon@"+str(Library.readIfaceIP("schedinterface"))+":"+str(Library.readLogLevel("schedport"))
    daemon=Pyro4.Proxy(uri)    
    
    #create active jobs list
    try:
        n=1
        for job in daemon.listJobs():    
            #6-6-0-CPU-stable-lookbusy-CPU
            if job[len(str(emulationID))-1]==str(emulationID):
                jobXml = ET.SubElement(scheduledJobsXml,"job"+str(n))
                print 
                jobXml.text=str(job)
                n+=1
        if n==1:
            jobXml = ET.SubElement(scheduledJobsXml,"jobsempty")
            jobXml.text="No jobs are scheduled"
    
    except Exception,e :
            jobXml = ET.SubElement(scheduledJobsXml,"jobsempty")
            jobXml.text="Scheduler error/Or scheduler is off-line"
            jobXml = ET.SubElement(scheduledJobsXml,"error")
            jobXml.text=str(e)
    
    try:
        #create distributions list
        for distro in distroList:
            #<distributions ID="1" name="myMixEmu-dis-1" >
            distributionsXml = ET.SubElement(emulation,'distributions', { 'ID':str(distro['distributionsID']),'name':distro['distributionsName']})
            
            startTimeDistroXml=ET.SubElement(distributionsXml,'startTime')
            startTimeDistroXml.text = str(distro['startTimeDistro'])
            
            startTimeDistroXml=ET.SubElement(distributionsXml,'granularity')
            startTimeDistroXml.text = str(distro['granularity'])
            
            #distroNameXml = ET.SubElement(distributionsXml,'distribution', { 'href':'/emulators/'+ str(distro['distributionName']),'name':str(distro['distributionName'])})
            #<distribution href="/distributions/geometric" name="geometric" />
            
            distributionXml = ET.SubElement(distributionsXml,'distribution', { 'href':'/distributions/'+ str(distro['distrType']),'name':str(distro['distrType'])})
            
            durationDistroXml=ET.SubElement(distributionsXml,'duration')
            durationDistroXml.text = str(distro['durationDistro'])
            
            distroArgs = distro['distroArgs']
            for distroArg in distroArgs:
                distroArgXml =ET.SubElement(distributionsXml,distroArg) 
                distroArgXml.text = str(distroArgs[distroArg])
        
            #<emulator href="/emulators/wireshark" name="wireshark" />
            emulatorXml = ET.SubElement(distributionsXml,'emulator', { 'href':'/emulators/'+ str(distro['emulatorName']),'name':str(distro['emulatorName'])})
            
            
            emulatorParamsXml = ET.SubElement(distributionsXml,'emulator-params')
            
            resourceTypeXml=ET.SubElement(emulatorParamsXml,'resourceType')
            resourceTypeXml.text = str(distro['resourceTypeDist'])
        
        
            emulatorArg = distro['emulatorArg']
            for emuArg in emulatorArg:
                emuArgXml =ET.SubElement(emulatorParamsXml,emuArg) 
                emuArgXml.text = str(emulatorArg[emuArg])
            
            
    except Exception,e:
        print "Distro list errorr",e
        


        
    logXML = ET.SubElement(emulation,'log')
    
    
    enableXML= ET.SubElement(logXML,'enable')
    enableXML.text=str(logging)
    
    frequencyXML=ET.SubElement(logXML,'frequency')
    frequencyXML.text=str(logFrequency)
    
    logLevelXML= ET.SubElement(logXML,'logLevel')
    logLevelXML.text=str(logLevel)        

    mqXML = ET.SubElement(emulation,'mq')
    
    
    enabledXML= ET.SubElement(mqXML,'enabled')
    enabledXML.text=str(enabled)
    
    vhostXML=ET.SubElement(mqXML,'vhost')
    vhostXML.text=str(vhost)
    
    exchangeXML= ET.SubElement(mqXML,'exchange')
    exchangeXML.text=str(exchange)             
    
    userXML= ET.SubElement(mqXML,'user')
    userXML.text=str(user)   

    passwordXML= ET.SubElement(mqXML,'password')
    passwordXML.text=str(password)  

    hostXML= ET.SubElement(mqXML,'host')
    hostXML.text=str(host)  

    topicXML= ET.SubElement(mqXML,'topic')
    topicXML.text=str(topic)  


    #<xmlData>xml body content</xmlData>
    #xmlDataXml =ET.SubElement(emulation,'xmlData')
    #xmlDataXml.text = str(xmlData)

    #<link href="/" rel="parent" type="application/vnd.cocoma+xml"/>
    lk0 = ET.SubElement(emulation, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
    #<link href="/emulations" rel="parent" type="application/vnd.cocoma+xml"/>
    lk0 = ET.SubElement(emulation, 'link', {'rel':'parent', 'href':'/emulations', 'type':'application/vnd.bonfire+xml'})
    
    return prettify(emulation)    

@route('/emulators/', method='GET')
@route('/emulators', method='GET')
def get_emulators():
    '''
    Display list of emulators
    '''
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD')     
    
    emuList=Library.listEmulators("all")
    #print "emulist",emuList
    '''
    XML namespaces are used for providing uniquely named elements and attributes in an XML document.
    '''
     
    #building the XML we will return
    emulators = ET.Element('collection', { 'xmlns':'http://127.0.0.1/cocoma','href':'/emulators'})
    #<items offset="0" total="2">
    items =ET.SubElement(emulators,'items', { 'offset':'0','total':str(len(emuList))})
    
    #<emulator href="/emulations/1" name="Emu1"/>
    
    for elem in emuList :
        emulator = ET.SubElement(items,'emulator', { 'href':'/emulators/'+str(elem),'name':str(elem)})
        
    #<link href="/" rel="parent" type="application/vnd.cocoma+xml"/>
    lk = ET.SubElement(emulators, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
    
  
    return prettify(emulators)




@route('/emulators/<name>/', method='GET')
@route('/emulators/<name>', method='GET')
def get_emulator(name=""):
    '''
    Display emulator by name
    '''
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD')
        
        
             
        
        
    try:
        helpMod=Library.loadEmulatorHelp(name)
        argMod=Library.loadEmulatorArgNames(name)
    
        emulatorXml = ET.Element('emulator', { 'xmlns':'http://127.0.0.1/cocoma','href':'/emulators/'+str(name)})
    
        emulatorInfoXml=ET.SubElement(emulatorXml,'info')
        emulatorHelpXml=ET.SubElement(emulatorInfoXml,'help')
        emulatorHelpXml.text = str(helpMod())
        
        emulatorResourcesListXml=ET.SubElement(emulatorInfoXml,'resources')
        
        #get list of resources
        resList=argMod()
        
        #get arguments for every resource { "mem":[startLoad,stopLoad,malloc]}, "io":[...]}
        for resource in resList:
            argNames=argMod(resource)
            
            #<mem>
            emulatorResourceXml=ET.SubElement(emulatorResourcesListXml,resource)
            #<startLoad>
            #{"startload":{"upperBound":100,"lowerBound":0},"stopload":{"upperBound":100,"lowerBound":0}}
            for args in argNames:
                emulatorArgsXml=ET.SubElement(emulatorResourceXml,args)
                
                #<upperBound>
                emulatorUpperBound=ET.SubElement(emulatorArgsXml,"upperBound")
                
                emulatorUpperBound.text = str(argNames[args]["upperBound"])
                
                emulatorLowerBound=ET.SubElement(emulatorArgsXml,"lowerBound")
                emulatorLowerBound.text = str(argNames[args]["lowerBound"])
                
                if not (argNames[args].has_key("argHelp")):
                    argNames[args]["argHelp"] = "No help Available"
                emuArgHelp=ET.SubElement(emulatorArgsXml,"argHelp")
                emuArgHelp.text = str(argNames[args]["argHelp"])
    

        lk0 = ET.SubElement(emulatorXml, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
        #<link href="/emulations" rel="parent" type="application/vnd.cocoma+xml"/>
        lk0 = ET.SubElement(emulatorXml, 'link', {'rel':'parent', 'href':'/emulators', 'type':'application/vnd.bonfire+xml'})
    
    
        return prettify(emulatorXml)
    
    except Exception, e:
        response.status = 404
        return "<error>"+str(e)+"</error>"    
    
    
    #curl -k -i http://10.55.164.211:8050/emulations/1/emulators/stressapptest
 
@route('/distributions/', method='GET')
@route('/distributions', method='GET')
def get_distributions():
    '''
    List all available distributions
    '''
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD')     
    
    distroList=Library.listDistributions("all")
    #print "distroList",distroList
    '''
    XML namespaces are used for providing uniquely named elements and attributes in an XML document.
    '''
    
    
    
    #building the XML we will return
    distributions = ET.Element('collection', { 'xmlns':'http://127.0.0.1/cocoma','href':'/distributions'})
    #<items offset="0" total="2">
    items =ET.SubElement(distributions,'items', { 'offset':'0','total':str(len(distroList))})
    
    #<distribution href="/emulations/1" name="Emu1"/>
    
    for elem in distroList :
        distribution = ET.SubElement(items,'distribution', { 'href':'/distributions/'+str(elem),'name':str(elem)})
        
        
    
    #<link href="/" rel="parent" type="application/vnd.cocoma+xml"/>
    lk = ET.SubElement(distributions, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
    
    

    return prettify(distributions)

@route('/distributions/<name>/', method='GET')
@route('/distributions/<name>', method='GET')
def get_distribution(name=""):
    '''
    Display distribution by name
    
    
    #example return
    <info>
        <help>Linear distribution takes in start and stop load parameters and gradually increasing resource workload. Can be used with CPU,MEM,IO,NET resource types.</help>
        <resources>
            <mem>
                <startLoad>
                    <upperBound>1</upperBound>
                    <lowerBound>2</lowerBound>
                </startLoad>
                
                <stopLoad>
                    <upperBound>1</upperBound>
                    <lowerBound>2</lowerBound>
                </stopLoad>                
            </mem>
            <io>
            ...
            </io>
        </resources>
    </info>
    '''
    
    #curl -k -i http://10.55.164.232:8050/distributions/linear
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD') 
    
    try:
        helpMod=Library.loadDistributionHelp(name)
        argMod=Library.loadDistributionArgNames(name)
    
        distributionXml = ET.Element('distribution', { 'xmlns':'http://127.0.0.1/cocoma','href':'/distributions/'+str(name)})
    
        distroInfoXml=ET.SubElement(distributionXml,'info')
        distroHelpXml=ET.SubElement(distroInfoXml,'help')
        distroHelpXml.text = str(helpMod())
        
        distroResourcesListXml=ET.SubElement(distroInfoXml,'resources')
        
        #get list of resources
        resList=argMod()
        
        #get arguments for every resource { "mem":[startLoad,stopLoad,malloc]}, "io":[...]}
        for resource in resList:
            argNames=argMod(resource)
            
            #<mem>
            distroResourceXml=ET.SubElement(distroResourcesListXml,resource)
            #<startLoad>
            #{"startload":{"upperBound":100,"lowerBound":0},"stopload":{"upperBound":100,"lowerBound":0}}
            for args in argNames:
                distroArgsXml=ET.SubElement(distroResourceXml,args)
                
                #<upperBound>
                distroUpperBound=ET.SubElement(distroArgsXml,"upperBound")
                
                distroUpperBound.text = str(argNames[args]["upperBound"])
                
                distroLowerBound=ET.SubElement(distroArgsXml,"lowerBound")
                distroLowerBound.text = str(argNames[args]["lowerBound"])
                
                if not (argNames[args].has_key("argHelp")):
                    argNames[args]["argHelp"] = "No help Available :'("
                distroArgHelp=ET.SubElement(distroArgsXml,"argHelp")
                distroArgHelp.text = str(argNames[args]["argHelp"])
                
#                if (argNames[args].has_key("argHelp")):
#                    distroArgHelp.text = str(argNames[args]["argHelp"])
#                else:
#                    distroArgHelp.text = str("No help Available :(")
    
        lk0 = ET.SubElement(distributionXml, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
        lk0 = ET.SubElement(distributionXml, 'link', {'rel':'parent', 'href':'/distributions', 'type':'application/vnd.bonfire+xml'})
    
    
        return prettify(distributionXml)
    
    except Exception, e:
        response.status = 404
        return "<error>"+str(e)+"</error>"
''' 
#############################
tests repository
#############################
'''

@route('/tests/', method='GET')
@route('/tests', method='GET')
def get_tests():
    '''
    List all available tests in the "/tests" folder
    '''
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD, POST')     
    
    testsList=Library.listTests("all")
    #print "testsList",testsList
    '''
    XML namespaces are used for providing uniquely named elements and attributes in an XML document.
    '''

    #building the XML we will return
    tests = ET.Element('collection', { 'xmlns':'http://127.0.0.1/cocoma','href':'/tests'})
    #<items offset="0" total="2">
    items =ET.SubElement(tests,'items', { 'offset':'0','total':str(len(testsList))})
    
    #<distribution href="/emulations/1" name="Emu1"/>
    
    for elem in testsList :
        test = ET.SubElement(items,'test', { 'href':'/tests/'+str(elem),'name':str(elem)})
        
        
    
    #<link href="/" rel="parent" type="application/vnd.cocoma+xml"/>
    lk = ET.SubElement(tests, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
    
    
    

    return prettify(tests)

@route('/tests/<name>/', method='GET')
@route('/tests/<name>', method='GET')
def show_test(name=""):
    '''
    List particular test by name in the "/tests" folder
    '''
    #curl -k -i http://10.55.164.232:8050/distributions/linear
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD') 
    
    try:
        filename=open(HOMEPATH+"/tests/"+name,'r')
        #print "filename to show: ",filename
        xmlFileContent = filename.read()
        filename.close()
        #xmlFileContent=XmlParser.xmlReader(filename)
        
        #DistributionManager.listTests(name)
        
        testXml = ET.Element('test', { 'xmlns':'http://127.0.0.1/cocoma','href':'/tests/'+str(name)})
        
        #xmlContent=ET.SubElement(testXml,)
        
    
        lk0 = ET.SubElement(testXml, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
        #<link href="/emulations" rel="parent" type="application/vnd.cocoma+xml"/>
        lk0 = ET.SubElement(testXml, 'link', {'rel':'parent', 'href':'/distributions', 'type':'application/vnd.bonfire+xml'})
    
    
        return prettify(ET.fromstring(xmlFileContent))
    
    except Exception, e:
        response.status = 404
        return "<error>"+str(e)+"</error>"
 




@route('/tests', method='POST')
@route('/tests/', method='POST')
def start_test():
    '''
    Execute an existing emulation XML from "/tests" folder
    '''
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD, POST') 
    
    
    
    emulationID=""
    
    fileName_stream =request.files.data
    fileName_stream_body =request.body.read()
    
    
    
    
    if fileName_stream:
        try:
            filename=HOMEPATH+"/tests/"+str(fileName_stream_body)
            #check if file exists maybe?
        except Exception,e:
            print e
            response.status = 400
            return "<error>"+str(e)+"</error>"
        
        #print "File data detected:\n",fileName_stream
        #return fileName_stream
        try:
             
            (emulationName,emulationType,emulationLog,emulationLogFrequency,emulationLogLevel, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData, MQproducerValues) = XmlParser.xmlFileParser(filename, True)
            if startTimeEmu.lower() =="now":
                startTimeEmu = Library.emulationNow(2)
                emulationID=EmulationManager.createEmulation(emulationName,emulationType,emulationLog,emulationLogFrequency,emulationLogLevel, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData, MQproducerValues)
            else:
                
                emulationID=EmulationManager.createEmulation(emulationName,emulationType,emulationLog,emulationLogFrequency,emulationLogLevel, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData, MQproducerValues)
        
        except Exception,e:
            print e
            response.status = 400
            return "<error>Cannot parse:"+str(e)+"</error>"
    else:
        #print "xml_stream_body:\n",fileName_stream_body
        
        try:   
            filename=HOMEPATH+"/tests/"+str(fileName_stream_body)
            #check if file exists maybe?
        except Exception,e:
            print e
            response.status = 400
            return "<error>Cannot parse body:"+str(e)+"</error>"        
        
        #print "Body data detected:\n", filename
        try:

            (emulationName,emulationType,emulationLog,emulationLogFrequency,emulationLogLevel, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData, MQproducerValues) = XmlParser.xmlFileParser(filename, True)
            if startTimeEmu.lower() =="now":
                startTimeEmu = Library.emulationNow(2)
                emulationID=EmulationManager.createEmulation(emulationName,emulationType,emulationLog,emulationLogFrequency,emulationLogLevel, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData, MQproducerValues)
            else:
                emulationID=EmulationManager.createEmulation(emulationName,emulationType,emulationLog,emulationLogFrequency,emulationLogLevel, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData, MQproducerValues)
    
        except Exception,e:
            print e
            response.status = 400
            return "<error>"+str(e)+"</error>"
        
        #Location: http://10.55.164.154:8050/results/2-CPU-dis-1
        paramsArray=re.split(r"-",str(emulationID))
        if isStr(paramsArray[0]):
            
            response.status = 400
            return "Unable to create emulation please check data.\n"+str(emulationID)
        
        response.set_header('Location', 'http://'+str(IP_ADDR)+':'+str(PORT_ADDR)+'/results/'+str(emulationID))
        response.status = 201
        
        
        resultsEmulation = ET.Element('test', { 'xmlns':'http://127.0.0.1/cocoma','href':'/tests/'+str(emulationID)})
            
        emuName= ET.SubElement(resultsEmulation,'emulationName')
        emuName.text = str(emulationID)
        emuStart=ET.SubElement(resultsEmulation,'startTime')
        emuStart.text=str(startTimeEmu)
        
        emuDate=ET.SubElement(resultsEmulation,'durationSec')
        emuDate.text=str(stopTimeEmu)
        
        
        
        return prettify(resultsEmulation)
        


'''
#############################
'''    
@route('/results', method='GET')
@route('/results/', method='GET')
def show_all_results():
    '''
    Show summary of emulations results
    '''
    #curl -k -i http://10.55.164.232:8050/distributions/linear
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD') 
    emuList=Library.getEmulationList("all")
    
    #root element
    resultsCollection = ET.Element('collection', { 'xmlns':'http://127.0.0.1/cocoma','href':'/results'})
    items =ET.SubElement(resultsCollection,'items', { 'offset':'0','total':str(len(emuList))})
        
        
    for elem in emuList :
        failedRunsInfo=elem["failedRunsInfo"]
        
        
        #print "---->\nID: "+str(elem["ID"])+"\nName: "+str(elem["Name"])+"\nState: "+str(elem["State"])+"\nTotal Runs: "+str(elem["runsTotal"])+"\nExecuted Runs: "+str(elem["runsExecuted"])+"\nFailed Runs: "+str(len(failedRunsInfo))
        
        emuResults = ET.SubElement(items,'results', { 'href':'/results/'+str(elem["Name"]),'failedRuns':str(len(failedRunsInfo)),'name':str(elem["Name"]),'state':str(elem["State"])})


        
    
    #<link href="/" rel="parent" type="application/vnd.cocoma+xml"/>
    lk = ET.SubElement(resultsCollection, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
    
    

    return prettify(resultsCollection)   


@route('/results/<name>/', method='GET')
@route('/results/<name>', method='GET')
def show_results(name=""):
    '''
    Show emulation results. The amount of total runs and the amount of failed runs.
    '''
    
    #curl -k -i http://10.55.164.232:8050/distributions/linear
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD') 
    
    
    try:    
        emuList=Library.getEmulationList(name)
        
        
        for elem in emuList :
            failedRunsInfo=elem["failedRunsInfo"]
            
            resultsEmulation = ET.Element('results', { 'xmlns':'http://127.0.0.1/cocoma','href':'/results/'+str(elem["Name"])})
            
            emuName= ET.SubElement(resultsEmulation,'emulationName')
            emuName.text = str(elem["Name"])
            
            totalRuns= ET.SubElement(resultsEmulation,'totalRuns')
            totalRuns.text=str(elem["runsTotal"])
            
            executedRuns=ET.SubElement(resultsEmulation,'executedRuns')
            executedRuns.text=str(elem["runsExecuted"])
            
            failedRuns=ET.SubElement(resultsEmulation,'failedRuns')
            
            #checking if emulation was already executed
            if str(elem["State"]) == "inactive":
                totalFailedRuns = int(elem["runsTotal"])-int(elem["runsExecuted"])
                failedRuns.text=str(totalFailedRuns)
            else:
                failedRuns.text=str(len(failedRunsInfo))
            
            
            
            emuState= ET.SubElement(resultsEmulation,'emuState')
            emuState.text=str(elem["State"])
            
            if failedRunsInfo:
            
                failedRunsDetails= ET.SubElement(resultsEmulation,'failedRunsDetails')
            
                #print "###Failed Runs Info###"
                for Runs in failedRunsInfo:
                    runNo= ET.SubElement(failedRunsDetails,'runNo',{'runNo':str(Runs["runNo"])})
                    #runNo.text=str(Runs["runNo"])
                    
                    distributionID= ET.SubElement(runNo,'distributionID')
                    distributionID.text=str(Runs["distributionID"])
                                   
                    distributionName= ET.SubElement(runNo,'distributionName')
                    distributionName.text=str(Runs["distributionName"])
                    
                    stressValue= ET.SubElement(runNo,'stressValue')
                    stressValue.text=str(Runs["stressValue"])
                    
                    message= ET.SubElement(runNo,'message')
                    message.text=str(Runs["message"])
                    
                    #print "#\nRun No: ", Runs["runNo"]
                    #print "Distribution ID: ",Runs["distributionID"]
                    #print "Distribution Name: ",Runs["distributionName"]
                    
                    #print "Stress Value: ", Runs["stressValue"]
                    #print "Error Message: ", Runs["message"]
        
            return prettify(resultsEmulation)
        
            
    except Exception,e:
        response.status = 400
        print "\nEmulation ID:"+str(name)+" not found.\nError:"+str(e)
        return "<error>Emulation ID:"+str(name)+" not found.\nError:"+str(e)+"</error>"


    
    
@route('/hello', method='OPTIONS')
@route('/hello', method='GET')
def api_status():
    '''
    Simpliest API responce to check if it is online
    '''
    response.status = 200
    #response.headers['status'] = response.status#str(response.status_code())
    response.content_type = "application/vnd.cocoma+xml"
    
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD, OPTIONS')
    return "Yes, Hello this is ccmshAPI." 

def isStr(s):
    '''
    Checking if the variable is a string
    '''
    try: 
        int(s)
        return False
    except ValueError:
        return True

'''
#######
Creating emulation
#######
'''
@route('/emulations', method='POST')
@route('/emulations/', method='POST')
def create_emu():
    '''
    Create emulation by POSTing xml with required parameters
    '''
    
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD, POST')
    
    #http://10.55.164.232:8050/emulations
    
    xml_stream =request.files.data
    xml_stream_body =request.body.read()
    xml_stream_body=urllib.unquote(xml_stream_body).decode('utf8')
    xml_stream_body = xml_stream_body.replace(unicode("+"), unicode(" "))
    searchString = "&runifOverloaded="
    searchIndex = xml_stream_body.rfind(searchString)
    runIfOverloaded = False
    if (searchIndex > 0):
        runIfOverloadedChar = xml_stream_body[searchIndex+len(searchString)]
        xml_stream_body = xml_stream_body [4:searchIndex]
        if (runIfOverloadedChar.upper() == "Y"):
            runIfOverloaded = True

    if xml_stream:
        #print "File data detected:\n",xml_stream
        return xml_stream
        try:
            (emulationName,emulationType,emulationLog,emulationLogFrequency, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData, MQproducerValues) = XmlParser.xmlFileParser(xml_stream, runIfOverloaded)
            if ("Re-send with force (-f)" in distroList[0]):
                response.status = 500
                ET.register_namespace("test", "http://127.0.0.1/cocoma")
                emuError = ET.Element('Force-Errors')
                emuError = ET.Element('Force-Errors', { 'xmlns':'http://127.0.0.1/cocoma','href':'/emulations/'})
                for forceError in distroList:
                    forceErrorXML = ET.SubElement(emuError, "error")
                    forceErrorXML.text = str(forceError)
                return prettify(emuError)
        except Exception,e:
            print e
            if str(e).find("no attribute 'getElementsByTagName'") > 0: #Return if supplied XML is bad
                e = "Supplied xml is malformed, check thoroughly for errors"
            response.status = 500
            emuError=ET.Element('error')
            emuError.text = str(e)
            return prettify(emuError)
            
    else:    
        try:
            (emulationName,emulationType,emulationLog,emulationLogFrequency,emulationLogLevel, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData, MQproducerValues) = XmlParser.xmlReader(xml_stream_body, runIfOverloaded)
            if ("Re-send with force (-f)" in distroList[0]):
                response.status = 500
                ET.register_namespace("test", "http://127.0.0.1/cocoma")
                emuError = ET.Element('Force-Errors', { 'xmlns':'http://127.0.0.1/cocoma','href':'/emulations/'})
                for forceError in distroList:
                    forceErrorXML = ET.SubElement(emuError, "error")
                    forceErrorXML.text = str(forceError)
                return prettify(emuError)
        except Exception,e:
            print e
            if str(e).find("no attribute 'getElementsByTagName'") > 0: #Return if supplied XML is bad
                e = "Supplied xml is malformed, check thoroughly for errors"
            response.status = 500
            #proper way to return web API error
            emuError=ET.Element('error')
#            emuError.text = str(XmlParser.xmlReader(xml_stream_body, runIfOverloaded))
            emuError.text = str(e)
            return prettify(emuError)
            
    #create emulation
    
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    try:
        emulationID=EmulationManager.createEmulation(emulationName,emulationType,emulationLog,emulationLogFrequency,emulationLogLevel, resourceTypeEmulation, startTimeEmu,stopTimeEmu, distroList,xmlData, MQproducerValues)
        paramsArray=re.split(r"-",str(emulationID))
        #print "paramsArray[0]",paramsArray[0]
        if isStr(paramsArray[0]):
            
            response.status = 400
            return "Unable to create emulation please check data.\n"+str(emulationID)
        #return new resource ID
        print str(emulationID)
        

        
        response.set_header('Location', 'http://'+str(IP_ADDR)+':'+str(PORT_ADDR)+'/emulations/'+str(emulationID))
        
        emulationXml = ET.Element('emulation', { 'xmlns':'http://127.0.0.1/cocoma','href':'/emulations/'+str(emulationID)})
        
        emulationIDXml=ET.SubElement(emulationXml,'ID')
        emulationIDXml.text = str(emulationID)
        #note about values change if out of bounds
        emulationEmuNotesXml=ET.SubElement(emulationXml,'EmuNotes')
        emulationDistroNotesXml=ET.SubElement(emulationXml,'DistroNotes')
        
        distroNotesStr=""
        emuNotesStr=""

        for items in distroList:
            for enotes in items['emulatorArgNotes']:
                    emuNotesStr+=str(enotes)
                
            for dnotes in items['distroArgsNotes']:
                    distroNotesStr+=str(dnotes)
                    
        emulationEmuNotesXml.text = emuNotesStr
        emulationDistroNotesXml.text= distroNotesStr
        

        
        lk0 = ET.SubElement(emulationXml, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
        #<link href="/emulations" rel="parent" type="application/vnd.cocoma+xml"/>
        lk0 = ET.SubElement(emulationXml, 'link', {'rel':'parent', 'href':'/emulations', 'type':'application/vnd.bonfire+xml'})
        
        response.status = 201
        return prettify(emulationXml)
        
    except Exception, e:
        response.status = 400
        print "Unable to create emulation please check data\n",e
        #print e
        #return error
        return "Unable to create emulation please check data\n"+str(e)


@route('/emulations/<ID>/', method='DELETE')
@route('/emulations/<ID>', method='DELETE')
def emulationDelete(ID=""):
    
    '''
    Deleting specific emulation by ID number
     
    
    
    DELETE /experiments/{{experiment_id}} HTTP/1.1
    Host: api.bonfire-project.eu
    Accept: */*
    
    =>
    
    HTTP/1.1 202 Accepted
    Content-Length: 0
    Location: https://api.bonfire-project.eu/experiments/{{experiment_id}}
    '''
    #delete_header=request.get_header("DELETE")
    #print "header info:",delete_header
    #delete_header =request.header.read()
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    try:
        
        deleteAction=EmulationManager.deleteEmulation(ID)
        if deleteAction == "success":
            #set confirmation headers
            response.status = 202
            response.set_header('Location', 'http://'+str(IP_ADDR)+':'+str(PORT_ADDR)+'/emulations/'+str(ID))
        else:
            response.status = 400
            return "Unable to delete emulation. Error:\n"+str(deleteAction)
    except Exception.message, e:
        response.status = 400
        print "Unable to create emulation please check data\n",e
        #print e
        #return error
        return "Unable to delete emulation please check data\n"+str(e)


'''
#######
Creating logging system
#######
'''
@route('/logs/', method='GET')
@route('/logs', method='GET')
def get_logs_list():
    """
    Show "emulation" and "system"
    """    
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD') 
    ET.register_namespace("test", "http://127.0.0.1/cocoma")
    
    logs = ET.Element('logs', { 'href':'/logs'})
    lk = ET.SubElement(logs, 'link', {'rel':'emulations', 'href':'/logs/emulations', 'type':'application/vnd.bonfire+xml'})
    lk = ET.SubElement(logs, 'link', {'rel':'system', 'href':'/logs/system', 'type':'application/vnd.bonfire+xml'})
    #lk = ET.SubElement(logs, 'link', {'rel':'system', 'href':'/', 'type':'application/vnd.bonfire+xml'})

    

    return prettify(logs)



@route('/logs/emulations/', method='GET')
@route('/logs/emulations', method='GET')
def get_emu_logs_list():
 
    ET.register_namespace("emulationLog", "http://127.0.0.1/cocoma")
    response.set_header('Content-Type', 'application/vnd.bonfire+xml')
    response.set_header('Accept', '*/*')
    response.set_header('Allow', 'GET, HEAD')     
    
    os.chdir(HOMEPATH+"/logs/")
    fileLogList = glob.glob("*-res_*-*-*:*:*.csv")
    '''
    XML namespaces are used for providing uniquely named elements and attributes in an XML document. 
    '''

    #building the XML we will return
    emulationLog = ET.Element('collection', { 'xmlns':'http://127.0.0.1/cocoma','href':'/logs/emulations'})
    #<items offset="0" total="2">
    items =ET.SubElement(emulationLog,'items', { 'offset':'0','total':str(len(fileLogList))})
    
    #<distribution href="/emulations/1" name="Emu1"/>
    print fileLogList
    for elem in fileLogList :
        test = ET.SubElement(items,'emulationLog', { 'href':'/logs/emulations/'+str(elem)[:-28],'name':str(elem)[:-28]})
        
        
    
    #<link href="/" rel="parent" type="application/vnd.cocoma+xml"/>
    lk = ET.SubElement(emulationLog, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
    lk = ET.SubElement(emulationLog, 'link', {'rel':'parent', 'href':'/logs', 'type':'application/vnd.bonfire+xml'})
    
    
    

    return prettify(emulationLog)



@route('/logs/emulations/<logName>/', method='GET')
@route('/logs/emulations/<logName>', method='GET')
def get_emu_logs(logName=''):
    """
    Retrieve Zipped logs by emulation name
    """
    response.set_header('Allow', 'GET, HEAD')
    response.set_header('Accept', '*/*')
    response.set_header('Content-Type', 'application/zip')
    response.set_header('Cache-Control', 'no-cache')
    
    return zip_files(logName)


@route('/logs/system/', method='GET')
@route('/logs/system', method='GET')
def get_system_logs():
    """
    Retrieve Zipped system logs by emulation name
    """
    response.set_header('Allow', 'GET, HEAD')
    response.set_header('Accept', '*/*')
    response.set_header('Content-Type', 'application/zip')
    response.set_header('Cache-Control', 'no-cache')
    
    return zip_files("COCOMAlogfile")

def zip_files(fileName_wo_zip):
    zipFilename="log-"+str(fileName_wo_zip)+".zip"
    dirPath=HOMEPATH+"/logs/"
    zfilename=dirPath+zipFilename    
    os.chdir(dirPath)
    fileZipList = glob.glob(str(fileName_wo_zip)+"*")

    if fileZipList:
        zf = zipfile.ZipFile(zfilename, 'w')
        for f in fileZipList:
            zf.write(dirPath + f, f)
        zf.close()
    else:
        response.status = 400
        return "<error>Emulation Log: "+str(zipFilename)+" not found.</error>"

    return static_file(zipFilename, root=dirPath, download=zipFilename)

@route('/jobs', method='GET')
@route('/jobs/', method='GET')
def get_Jobs():
    jobList = Library.getJobList()
    jobListLength = len(jobList)
    listSplitIndex = -1
    currentJobList = []
    
    for index, job in enumerate(jobList):
        if job.find("Currently running jobs") >= 0:
            listSplitIndex = index
    if listSplitIndex != -1:    #Splits into two lists, if there are jobs currently running
        currentJobList = jobList[listSplitIndex+1:jobListLength]
        jobList = jobList[0:listSplitIndex]
        jobListLength = len(jobList) + len(currentJobList)
        
    def jobsToXML (jobList, currentJobList, totalJobs): #Converts job lists to xml foramt
        ET.register_namespace("jobs", "http://127.0.0.1/cocoma")
        response.set_header('Content-Type', 'application/vnd.bonfire+xml')
        response.set_header('Accept', '*/*')
        response.set_header('Allow', 'GET')
        
        jobXmlRoot = ET.Element('collection', { 'xmlns':'http://127.0.0.1/cocoma','href':'/jobs'})
        jobCollection = ET.SubElement(jobXmlRoot, 'items', {'offset':'0','total':str(totalJobs)})
        for job in jobList:
            jobXML = ET.SubElement(jobCollection, "Job")
            jobXML.text = job
        if len(currentJobList) > 0:
            for currentJob in currentJobList:
                currentJobXML = ET.SubElement(jobCollection, "currentlyRunningJob")
                currentJobXML.text = str(currentJob)
        lk = ET.SubElement(jobXmlRoot, 'link', {'rel':'parent', 'href':'/', 'type':'application/vnd.bonfire+xml'})
        return prettify(jobXmlRoot)
    
#    jobXML = jobsToXML(jobList, currentJobList, jobListLength)
#    response.status = 200
#    return jobXML
    
    try:
        jobXML = jobsToXML(jobList, currentJobList, jobListLength)
        response.status = 200
        return jobXML
    except Exception, e:
        response.status = 400
        return "<ERROR>Unable to get job list: " + e + " </ERROR>"

def startAPI(IP_ADDR,PORT_ADDR):

    if Library.daemonCheck() ==0:
            print "\n---Check if Scheduler Daemon is started. Connection error---"
            sys.exit(0)
  
    print"API IP address:",IP_ADDR

    API_HOST=run(host=IP_ADDR, port=PORT_ADDR)
    return IP_ADDR

if __name__ == '__main__':
    PORT_ADDR = 5050
    try: 
        if sys.argv[1] == "-h":
            print "Use ccmshAPI -i <name of network interface> -p <port number>. Default network interface is eth0, port 5050."
        else:
            try:
                INTERFACE = sys.argv[1]
                print "Interface: ",INTERFACE
                IP_ADDR=Library.getifip(INTERFACE)
                try:
                    PORT_ADDR = int(sys.argv[2])
                except Exception, e:
                    print "No port specified using 5050 as default"
            except Exception, e:
                INTERFACE = "eth0"
                IP_ADDR=Library.getifip(INTERFACE)
                print "No port specified using eth0 as default"

            #writing config to db
            Library.writeInterfaceData(INTERFACE,"apiinterface")
            #starting API module
            startAPI(IP_ADDR,PORT_ADDR)
     
    except Exception, e:
        INTERFACE ="eth0"
        IP_ADDR=Library.getifip("eth0")
        Library.writeInterfaceData("eth0","apiinterface")
        startAPI(IP_ADDR,PORT_ADDR)