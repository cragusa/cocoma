'''
Created on 25 Sep 2012

@author: i046533
'''
import math


class distributionMod(object):
    
    
    def __init__(self,arg1, arg2, distributionGranularity,runNo):
        
        self.startLoad = arg1
        self.stopLoad = arg2
        self.distributionGranularity = distributionGranularity
        self.runNo = runNo
        
           
        self.linearStep=((int(self.startLoad)-int(self.stopLoad))/int(self.distributionGranularity))
        self.linearStep=math.fabs((int(self.linearStep)))
        print "LINEAR STEP SHOULD BE THE SAME"
        print self.linearStep
        self.linearStress= ((self.linearStep*int(self.runNo)))+int(self.startLoad)
        #make sure we return integer
        self.linearStress=int(self.linearStress)
        print "LINEAR STRESS SHOULD CHANGE"
        print self.linearStress
        #return self.linearStress
        
                  

    

