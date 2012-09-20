'''
Media type: application/json
we will try to return JSON object 
{
    "firstName": "John",
    "lastName": "Smith",
    "age": 25,
    "address": {
        "streetAddress": "21 2nd Street",
        "city": "New York",
        "state": "NY",
        "postalCode": "10021"
    },
    "phoneNumber": [
        {
            "type": "home",
            "number": "212 555-1234"
        },
        {
            "type": "fax",
            "number": "646 555-4567"
        }
    ]
}


'''


from bottle import route, run,response,request
import optparse,sys,Pyro4,itertools
#import argparse - new version of optparse
import EmulationManager,XmlParser,ccmsh
from json import dumps

@route('/hello/:id')
def hello(id):
    #return "Hello World!"
    return "MyID: "+id

@route('/ccmsh/list')
def get_emulation():
    emulationID = request.query.get('emulationID')
    if emulationID=="all":
        emulationSelect=EmulationManager.getEmulation("NULL","NULL",1,0)
    else:
        emulationSelect=EmulationManager.getEmulation("NULL",emulationID,0,0)
    
    
    
    if emulationSelect:
            
                
                response.content_type = 'application/json'
                return dumps(emulationSelect)

            
    else:
        
        return "emulation ID: \"",emulationID,"\" does not exists"
    
@route('/ccmsh/hello')
def api_status():
    return "Yes, Hello this is ccmshAPI."


@route('/ccmsh/create')
def create_emulation():
        '''
        #start alternative stuff
        paramList =[]
        
        paramList.append('emulationName')
        paramList.append(request.query.get('emulationName'))
        paramList.append('distributionType')
        paramList.append(request.query.get('distributionType'))
        paramList.append('resourceType')
        paramList.append(request.query.get('resourceType'))
        paramList.append('emulationType')
        paramList.append(request.query.get('emulationType'))
        paramList.append('startTime')
        paramList.append(request.query.get('startTime'))
        paramList.append('stopTime')
        paramList.append(request.query.get('stopTime'))
        paramList.append('distributionGranularity')
        paramList.append(request.query.get('distributionGranularity'))
        paramList.append('startLoad')
        paramList.append(request.query.get('startLoad'))
        paramList.append('stopLoad')
        paramList.append(request.query.get('stopLoad'))
                         
        
        d = dict(itertools.izip_longest(*[iter(paramList)] * 2, fillvalue=""))
        #stopalternative stuff
        '''
        
        #checking for daemon
        if ccmsh.daemonCheck()==0:
            return "Daemon is not running or cannot be located. Please check Scheduler configuration"
        else:
            d={}
            
                         
            emulationName = request.query.get('emulationName')
            distributionType = request.query.get('distributionType')
            resourceType = request.query.get('resourceType')
            emulationType = request.query.get('emulationType')
            startTime = request.query.get('startTime')
            stopTime = request.query.get('stopTime')
            distributionGranularity = request.query.get('distributionGranularity')
            startLoad = request.query.get('startLoad')
            stopLoad = request.query.get('stopLoad')
        
            EmulationManager.createEmulation(emulationName, distributionType, resourceType, emulationType, startTime, stopTime, distributionGranularity,startLoad, stopLoad)        
            d= {'emulationName':emulationName, 'distributionType':distributionType, 'resourceType':resourceType, 'emulationType':emulationType, 'startTime':startTime, 'stopTime':stopTime, 'distributionGranularity':distributionGranularity,'startLoad':startLoad, 'stopLoad':stopLoad}
        
            print d
            
            return d 
        

@route('/ccmsh/update')
def update_emulation():
        
        
        #checking for daemon
        if ccmsh.daemonCheck()==0:
            return "Daemon is not running or cannot be located. Please check Scheduler configuration"
        else:
            #setting all values to NULL
            
            emulationID = 'NULL'
            emulationName = 'NULL'
            distributionType = 'NULL'
            resourceType = 'NULL'
            emulationType = 'NULL'
            startTime = 'NULL'
            stopTime = 'NULL'
            distributionGranularity = 'NULL'
            startLoad = 'NULL'
            stopLoad = 'NULL'
            
            d={}
            
            
            
            if request.query.get('emulationID'):
                emulationID = request.query.get('emulationID')
                
                if request.query.get('emulationName'):
                    emulationName = request.query.get('emulationName')
                                
                if request.query.get('distributionType'):
                    distributionType = request.query.get('distributionType')
                
                if request.query.get('resourceType'):
                    resourceType = request.query.get('resourceType')
                
                if request.query.get('emulationType'):
                    emulationType = request.query.get('emulationType')
                    
                if request.query.get('startTime'):
                    startTime = request.query.get('startTime')
                
                if request.query.get('stopTime'):
                    stopTime = request.query.get('stopTime')
                    
                if request.query.get('distributionGranularity'):
                    distributionGranularity = request.query.get('distributionGranularity')
                    
                if request.query.get('startLoad'):
                    startLoad = request.query.get('startLoad')
                
                if request.query.get('stopLoad'):
                    stopLoad = request.query.get('stopLoad')
        
                EmulationManager.updateEmulation(emulationID,emulationName,distributionType,resourceType,emulationType,startTime,stopTime, distributionGranularity,startLoad, stopLoad)        
                d= {'emulationName':emulationName, 'distributionType':distributionType, 'resourceType':resourceType, 'emulationType':emulationType, 'startTime':startTime, 'stopTime':stopTime, 'distributionGranularity':distributionGranularity,'startLoad':startLoad, 'stopLoad':stopLoad}
                
                return d
            
            else:
                
                print "No emulation ID specified"
            
                return "Error: Provide Emulation ID" 
        


        
@route('/ccmsh/delete')
def emulationDelete():
    #checking for daemon
        if ccmsh.daemonCheck()==0:
            return "Daemon is not running or cannot be located. Please check Scheduler configuration"
        else:
            emulationID = request.query.get('emulationID')
            EmulationManager.deleteEmulation(emulationID)
            return "EmulationID: "+emulationID+" was deleted"

def startAPI():
    run(host='10.55.164.240', port=8050)
    
if __name__ == '__main__':
    startAPI()