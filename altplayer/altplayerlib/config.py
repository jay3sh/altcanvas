
import os
import sys

from utils import XMLNode
    
class Config:
    map = None
    def __init__(self):
        self.CONFIG_FILE = None
        if sys.platform.find('win32') >= 0:
            self.CONFIG_FILE=os.getenv('USERPROFILE')+'\\.publishr'
        else:
            self.CONFIG_FILE=os.getenv('HOME')+'/.publishr'
        
        try:
            configf = open(self.CONFIG_FILE,'r')
        except IOError, ioe:
            self.map = None
            return
            
        xml = ''
        for line in configf:
            xml += line
        try:
            xmlresult = XMLNode.parseXML(xml)
        except:
            self.map = None
            return
        
        self.map = {}
        try:
            for param in xmlresult.param:
                key = param['name']
            	value = param.elementText
            	self.map[key] = value
        except AttributeError, ae:
            # when NO xml is present, the param attribute is absent,
            # leading to this error. Ignore it.
            pass
                
        configf.close()
                
    def get(self,key):
        if self.map and key in self.map.keys():
            return self.map[key]
        return None
    
    def set(self,key,value):
        if not self.map:
            self.map = {}
            
        if value:
            self.map[key] = value
        else:
            # if the new value of key is None, then remove the key from map
            # this can be used to delete some properties from config file 
            if key in self.map.keys():
                del self.map[key]
        
        self.flush()
        
    def flush(self):
        try:
            configf = open(self.CONFIG_FILE,'w')
        except IOError, ioe:
            return None
        
        configf.write('<config>\n')
        for key in self.map.keys():
            configf.write('<param name="%s">%s</param>\n'%(key,self.map[key]))
        configf.write('</config>\n')
            
        configf.close()
            
