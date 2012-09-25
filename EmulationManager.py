'''
Created on 3 Sep 2012

@author: i046533
'''

import sqlite3 as sqlite
import sys,re
import DistributionManager
import Pyro4


def getEmulation(emulationName,emulationID,all,active):
    print "Hello this is getEmulation"
    #creating Dictionary to return for JSON
    returnDict={}
    returnList=[]
    
        
    try:
        conn = sqlite.connect('cocoma.sqlite')
        c = conn.cursor()
        
        # 1. By name
        if emulationName !="NULL":
            #c.execute("SELECT * FROM emulation WHERE emulationName='"+str(emulationName)+"'")
            print "DB entries for emulation Name", emulationName
            
            c.execute("""SELECT emulation.emulationID, emulation.emulationName, emulation.emulationType, emulation.resourceType, emulation.active, 
                         distribution.distributionGranularity,distribution.distributionType,DistributionParameters.startLoad,DistributionParameters.stopLoad,
                         emulationLifetime.startTime,emulationLifetime.stopTime 
                         FROM emulation, distribution,emulationLifetime,DistributionParameters
                         WHERE emulation.emulationName=? and emulation.distributionID = distribution.distributionID and
                         emulationLifetime.emulationID = emulation.emulationID and 
                         DistributionParameters.distributionID=distribution.distributionID"""
                         ,[emulationName])
            print "DB entries for emulation Name", emulationName
        
        if emulationID !="NULL":
            #c.execute("SELECT * FROM emulation WHERE emulationID='"+str(emulationID)+"'")
            print "DB entries for emulation ID", emulationID
            c.execute("""SELECT emulation.emulationID,emulation.emulationName, emulation.emulationType, emulation.resourceType, emulation.active, 
                         distribution.distributionGranularity,distribution.distributionType,DistributionParameters.startLoad,DistributionParameters.stopLoad,
                         emulationLifetime.startTime,emulationLifetime.stopTime 
                         FROM emulation, distribution,emulationLifetime,DistributionParameters
                         WHERE emulation.emulationID=? and emulation.distributionID = distribution.distributionID and
                         emulationLifetime.emulationID = emulation.emulationID and 
                         DistributionParameters.distributionID=distribution.distributionID"""
                         ,[emulationID])
            
          
            
        if all==1:
            #c.execute("SELECT * FROM emulation")
            print "DB entries for all emulations"
            
            c.execute("""SELECT emulation.emulationID,emulation.emulationName, emulation.emulationType, emulation.resourceType, emulation.active, 
                         distribution.distributionGranularity,distribution.distributionType,DistributionParameters.startLoad,DistributionParameters.stopLoad,
                         emulationLifetime.startTime,emulationLifetime.stopTime 
                         FROM emulation, distribution,emulationLifetime,DistributionParameters
                         WHERE emulation.distributionID = distribution.distributionID and
                         emulationLifetime.emulationID = emulation.emulationID and 
                         DistributionParameters.distributionID=distribution.distributionID"""
                    )
            
            
        if active ==1:
            #c.execute('SELECT * FROM emulation WHERE active=?',("1"))
            print "DB entries for all active emulations"
            
            c.execute("""SELECT emulation.emulationID,emulation.emulationName, emulation.emulationType, emulation.resourceType, emulation.active, 
                         distribution.distributionGranularity,distribution.distributionType,DistributionParameters.startLoad,DistributionParameters.stopLoad,
                         emulationLifetime.startTime,emulationLifetime.stopTime 
                         FROM emulation, distribution,emulationLifetime,DistributionParameters
                         WHERE emulation.active=? and emulation.distributionID = distribution.distributionID and
                         emulationLifetime.emulationID = emulation.emulationID and 
                         DistributionParameters.distributionID=distribution.distributionID"""
                         ,["1"])
        
            
        
        
        emulationTable = c.fetchall()
        
        if emulationTable:
                      
        
            for row in emulationTable:
                
                print "------->\nemulation.emulationID",row[0],"\nemulation.emulationName",row[1], "\nemulation.emulationType",row[2], "\nemulation.resourceType",row[3],"\nemulation.active",row[4],"\ndistribution.distributionGranularity",row[5],"\ndistribution.distributionType",row[6],"\nDistributionParameters.startLoad",row[7],"\nDistributionParameters.stopLoad",row[8], "\nemulationLifetime.startTime",row[9],"\nemulationLifetime.stopTime",row[10]
                returnDict={"emulationID":row[0],"emulationName":row[1],"emulationType":row[2], "resourceType":row[3],"active":row[4],"distributionGranularity":row[5],"distributionType":row[6],"startLoad":row[7],"stopLoad":row[8], "startTime":row[9],"stopTime":row[10]}
                
                returnList.append(returnDict)
        else:
            print "emulation ID: \"",emulationID,"\" does not exists"
        
        
        
    except sqlite.Error, e:
        print "Error getting emulation list %s:" % e.args[0]
        print e
        sys.exit(1)
        
    c.close()
    return returnList



def deleteEmulation(emulationID):
    print "Hello this is deleteEmulation"
     
    
    try:
        conn = sqlite.connect('cocoma.sqlite')
        c = conn.cursor()
        c.execute('SELECT distributionID, emulationName FROM emulation WHERE emulationID=?',[str(emulationID)])
                
        distributionIDfetch = c.fetchall()
        
        if distributionIDfetch:
            for row in distributionIDfetch:
                print row
                distributionID= row[0]
                emulationName = row[1]
                
        else:
            print "Emulation ID: "+str(emulationID)+" does not exists" 
            sys.exit(1)
        
        print "distro ID: ",distributionID
        
        c.execute('SELECT distributionType FROM distribution WHERE distributionID=?',[str(distributionID)]) 
        
        distributionTypeFetch = c.fetchall()
        
        if distributionTypeFetch:
            for row in distributionTypeFetch:
                distributionType= row[0]
        print "distro Type: ",distributionType
        
        
        c.execute('SELECT emulationLifetimeID FROM emulationLifetime WHERE emulationID=?',[str(emulationID)])
                
        emulationLifetimeIDfetch = c.fetchall()
        
        if emulationLifetimeIDfetch:
            for row in emulationLifetimeIDfetch:
                emulationLifetimeID= row[0]
        
        
        
        c.execute('DELETE FROM distribution WHERE distributionID=?',[str(distributionID)])
        c.execute('DELETE FROM emulationLifetime WHERE emulationID=?',[str(emulationID)])
        c.execute('DELETE FROM runLog WHERE emulationLifetimeID=?',[str(emulationLifetimeID)])
        c.execute('DELETE FROM DistributionParameters WHERE distributionID=?',[str(distributionID)])
        c.execute('DELETE FROM emulation WHERE emulationID=?',[str(emulationID)])
        
        conn.commit()
    except sqlite.Error, e:
        print "Could not delete emulationID: ",emulationID
        print "Error %s:" % e.args[0]
        print e
        sys.exit(1)
        
    c.close()
    print "Emulation ID: ", emulationID," was deleted"
    
    #Now here we need to remove the emulation from the scheduler
    uri ="PYRO:scheduler.daemon@localhost:51889"
    daemon=Pyro4.Proxy(uri)
    daemon.deleteJobs(emulationID, emulationName)
    
def purgeAll():
    print "Hello this is purgeAll"
     
    
    try:
        conn = sqlite.connect('cocoma.sqlite')
        c = conn.cursor()
        c.execute('DELETE FROM distribution')
        c.execute('DELETE FROM emulationLifetime ')
        c.execute('DELETE FROM runLog')
        c.execute('DELETE FROM DistributionParameters')
        c.execute('DELETE FROM emulation')
        #reset the counter
        c.execute('UPDATE sqlite_sequence SET seq=0 WHERE name="DistributionParameters"')
        c.execute('UPDATE sqlite_sequence SET seq=0 WHERE name="distribution"')
        c.execute('UPDATE sqlite_sequence SET seq=0 WHERE name="emulation"')
        c.execute('UPDATE sqlite_sequence SET seq=0 WHERE name="emulationLifetime"')
        c.execute('UPDATE sqlite_sequence SET seq=0 WHERE name="runLog"')
        
        
        
        conn.commit()
    except sqlite.Error, e:
        print "Could not delete everything "
        print "Error %s:" % e.args[0]
        print e
        sys.exit(1)
        
    c.close()
    print "Everything was deleted in DBl"
    
    #Now here we need to remove the emulation from the scheduler
    #uri ="PYRO:scheduler.daemon@localhost:51889"
    #daemon=Pyro4.Proxy(uri)
    # we need to remove jobs somehow too
    
#TO-DO: logic needs to be updated 
def updateEmulation(emulationID,newEmulationName,newDistributionType,newResourceType,newEmulationType,newStartTime,newStopTime, newDistributionGranularity,newStartLoad, newStopLoad):
    print "Hello this is updateEmulation"
    
    uri ="PYRO:scheduler.daemon@localhost:51889"
    daemon=Pyro4.Proxy(uri)
    
    #1. Get all the values from the existing table
    try:
        conn = sqlite.connect('cocoma.sqlite')
        c = conn.cursor()
        
        if emulationID !="NULL":
            #c.execute("SELECT * FROM emulation WHERE emulationID='"+str(emulationID)+"'")
            print "DB entries for emulation ID", emulationID
            c.execute("""SELECT emulation.emulationID,emulation.emulationName, emulation.emulationType, emulation.resourceType, emulation.active, 
                         distribution.distributionGranularity,distribution.distributionType,DistributionParameters.startLoad,DistributionParameters.stopLoad,
                         emulationLifetime.startTime,emulationLifetime.stopTime,emulationLifetime.emulationLifetimeID,distribution.distributionID 
                         FROM emulation, distribution,emulationLifetime,DistributionParameters
                         WHERE emulation.emulationID=? and emulation.distributionID = distribution.distributionID and
                         emulationLifetime.emulationID = emulation.emulationID and 
                         DistributionParameters.distributionID=distribution.distributionID"""
                         ,[emulationID])
            
            emulationTable = c.fetchall()
        
        if emulationTable:
                      
        
            for row in emulationTable:
                
                print "------->\nemulation.emulationID",row[0],"\nemulation.emulationName",row[1], "\nemulation.emulationType",row[2], "\nemulation.resourceType",row[3],"\nemulation.active",row[4],"\ndistribution.distributionGranularity",row[5],"\ndistribution.distributionType",row[6],"\nDistributionParameters.startLoad",row[7],"\nDistributionParameters.stopLoad",row[8], "\nemulationLifetime.startTime",row[9],"\nemulationLifetime.stopTime",row[10]
                
                emulationID=row[0]
                emulationName=row[1]
                emulationType=row[2]
                resourceType=row[3]
                active=row[4]
                distributionGranularity=row[5]
                distributionType=row[6]
                startLoad=row[7]
                stopLoad=row[8]
                startTime=row[9]
                stopTime=row[10]
                emulationLifetimeID =row[11]
                distributionID= row[12]
                
                #Deleting existing jobs at scheduler
                daemon.deleteJobs(emulationID, emulationName)
                
                #2. Check and assign which changes were made
                if newEmulationName != "NULL":
                    
                
                    emulationName = newEmulationName
                    c.execute('UPDATE emulation SET emulationName=? WHERE emulationID =?',(emulationName,emulationID))
                    conn.commit()
                    
                if newEmulationType != "NULL":
                    emulationType = newEmulationType
                    c.execute('UPDATE emulation SET emulationType=? WHERE emulationID =?',(emulationType,emulationID))
                    conn.commit()
                    
                if newResourceType != "NULL":
                    resourceType = newResourceType
                    c.execute('UPDATE emulation SET resourceType=? WHERE emulationID =?',(resourceType,emulationID))
                    conn.commit()
                    
                if newDistributionType != "NULL":
                    distributionType = newDistributionType
                    c.execute('UPDATE distribution SET distributionType=? WHERE distributionID =?',(distributionType,distributionID))
                    conn.commit()
                    
                if newStartTime != "NULL":
                    startTime = newStartTime
                    c.execute('UPDATE emulationLifetime SET startTime=? WHERE emulationLifetimeID =?',(startTime,emulationLifetimeID))
                    conn.commit()
                    
                if newStopTime != "NULL":
                    stopTime = newStopTime
                    c.execute('UPDATE emulationLifetime SET stopTime=? WHERE emulationLifetimeID =?',(stopTime,emulationLifetimeID))
                
                if newDistributionGranularity != "NULL":
                    distributionGranularity = newDistributionGranularity
                    c.execute('UPDATE distribution SET distributionGranularity=? WHERE distributionID =?',(distributionGranularity,distributionID))
                    conn.commit()
                    
                if newStartLoad != "NULL":
                    startLoad = newStartLoad
                    c.execute('UPDATE DistributionParameters SET startLoad=? WHERE distributionID =?',(startLoad,distributionID))
                    conn.commit()
                    
                if newStopLoad != "NULL":
                    stopLoad = newStopLoad
                    c.execute('UPDATE DistributionParameters SET stopLoad=? WHERE distributionID =?',(stopLoad,distributionID))
            
            
                #3. Deleting existing runLog
                c.execute('DELETE FROM runLog WHERE emulationLifetimeID=?',[str(emulationLifetimeID)])
                
                dataCheck(startTime,stopTime)
                conn.commit()
                                                
                #4. Create new runLog
                newEmulation =1
                daemon.schedulerControl(emulationID,emulationLifetimeID,emulationName,startTime,stopTime, distributionGranularity,startLoad, stopLoad,newEmulation)   
                
                
                
        else:
            print "emulation ID: \"",emulationID,"\" does not exists"
        
        
        conn.commit()
    except sqlite.Error, e:
        print "Error getting emulation list %s:" % e.args[0]
        print e
        sys.exit(1)
        
    c.close()
    

    
    

def createEmulation(emulationName,distributionType,resourceType,emulationType,startTime,stopTime, distributionGranularity,startLoad, stopLoad):
                    
    print "Hello this is createEmulation"
    
    #TO-DO: we need to check here if there is another emulation scheduled for the same time and if the date is in the future
    #dateCheck(startTime,stopTime)

    #connecting to the DB and storing parameters
    try:
        conn = sqlite.connect('cocoma.sqlite')
        c = conn.cursor()
    
        # 1. populate DistributionParameters, of table determined by distributionType name in our test it is "linearDistributionParameters"
        c.execute('INSERT INTO DistributionParameters (startLoad,stopLoad) VALUES (?, ?)', [startLoad,stopLoad])

        distributionParametersID=c.lastrowid
                
        # 2. We populate "distribution" table  
        c.execute('INSERT INTO distribution (distributionGranularity, distributionType, distributionParametersID) VALUES (?, ?, ?)', [distributionGranularity, distributionType, distributionParametersID])
    
        distributionID=c.lastrowid
        
                
        # 3. Populate "emulation"
        c.execute('INSERT INTO emulation (emulationName,emulationType,resourceType,distributionID,active) VALUES (?, ?, ?, ?, ?)', [emulationName,emulationType,resourceType,distributionID,1])
        emulationID = c.lastrowid
        
        # 4. Adding missing distribution ID
        c.execute('UPDATE DistributionParameters SET distributionID=? WHERE distributionParametersID =?',(distributionID,distributionParametersID))
        
        # 5. We populate "emulationLifetime" table  
        c.execute('INSERT INTO emulationLifetime (startTime,stopTime,emulationID) VALUES (?, ?, ?)', [startTime,stopTime,emulationID,])
        emulationLifetimeID = c.lastrowid
        
        #6. Update emulation with LifetimeID
        
        c.execute('UPDATE emulation SET emulationLifetimeID=? WHERE emulationID =?',(emulationLifetimeID,emulationID))
        
        
                
        
        
        c.execute("SELECT * FROM emulation WHERE emulationID='"+str(emulationID)+"'")
        print "Entry created with emulation ID", emulationID
        
        emulationEntry= c.fetchall()
        for row in emulationEntry: 
            print "emulationID:",row[0],"emulationName:", row[1],"emulationType:", row[2],"resourceType:", row[3], "distributionID:",row[4],"emulationLifetimeID:",row[5] ,"active:",row[6]
        
        dataCheck(startTime,stopTime)
        conn.commit()
        
        DistributionManager.distributionManager(emulationID,emulationLifetimeID,emulationName,distributionType,resourceType,emulationType,startTime,stopTime, distributionGranularity,startLoad, stopLoad)
        
    except sqlite.Error, e:
        print "Error %s:" % e.args[0]
        print e
        sys.exit(1)
    
    c.close()





def dataCheck(startTime,stopTime):
    print "Hello this is dataCheck"
    time_re = re.compile('\d{4}[-]\d{2}[-]\d{2}[T]\d{2}[:]\d{2}[:]\d{2}')
    granularity_re=re.compile('/d')
    
    if time_re.match(startTime) and time_re.match(stopTime) :
        print "date is correct"
    else:
        print "Date incorrect use YYYY-MM-DDTHH:MM:SS format "
        sys.exit(0)
    '''    
    if granularity_re(distributionGranularity) and granularity_re(startLoad):
        print "Granularity is correct"
    else:
        print "Granularity format is wrong"
    '''    

if __name__ == '__main__':
    
    
    emulationName = "mytest"
    emulationType = "Malicious"
    resourceType = "CPU"
    startTime = "2012-10-30T20:03:04"
    
    stopTime= "2012-10-30T20:10:03"
    distributionGranularity = 10
    distributionType = "linear"
    startLoad = 20
    stopLoad = 100
       
    pass