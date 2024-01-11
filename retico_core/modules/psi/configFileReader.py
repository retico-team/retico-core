"""A module for reading xml/json config file and prepare retico to receive psi outputs"""

#xml
import xml.etree.ElementTree as ET
import xmltodict
import os

# retico
from retico_core.interop.zeromq.io import ZeroMQReader
from retico_core.debug import DebugModule

class configFileReader():
    """A module reads a config file and prepares to read psi outputs"""

    @staticmethod
    def name():
        return "config file reader module"

    @staticmethod
    def description():
        return "A module that reads a config file and prepares to read outputs from psi"

    def __init__(self):
        print("Enter config file name:\n")
        self.fileName = input()    

    def read_config(self, fileName):
        print("Reading Config File: " + str(fileName))
        
        if fileName.endswith('.xml') or fileName.endswith('.json'):
            print("Valid File Format")
        else:
            print("Invalid File Format")
            return None
        
        if not os.path.isfile(fileName):
            print("File not found")
            return None
        
        if fileName.endswith('.xml'):
            root = ET.parse(fileName).getroot()
            
            allZeroMqInfo = []
            for IUComponentCollection in root:
                for IUComponent in IUComponentCollection:
                    if IUComponent.findtext('componentOwner') == "psi":
                        if IUComponent.findtext('componentType') == "component":
                            if IUComponent.findtext('interopStatus') == "True":
                                allZeroMqInfo.append(IUComponent.findtext('interopTopic') + ";" + IUComponent.findtext('interopAddress'))
                                
        return allZeroMqInfo
    
    def createComponents(self, allZeroMqInfo):
        print("Creating zeromq components...")
        allZeroMqModules = []
        allDebugModules = []
        for i in range(0, len(allZeroMqInfo)):
            #e.g. someTopic;tcp://localhost:12345
            splittedData = allZeroMqInfo[i].split(';')
            ipAddress = splittedData[1].split('//')[1].split(':')[0]
            psiPort = splittedData[1].split('//')[1].split(':')[1]
            
            print("creating zeromq module with address: " + ipAddress + ", and port: " + psiPort)
            psiZeroMqReader = ZeroMQReader(topic=splittedData[0], ip=ipAddress, port=psiPort)
            debug = DebugModule()
            
            psiZeroMqReader.subscribe(debug)
                
            allZeroMqModules.append(psiZeroMqReader)
            allDebugModules.append(debug)
        
        return allZeroMqModules, allDebugModules
    
    def startExecution(self, allZeroMqModules, allDebugModules):
        #running the modules
        print("running modules")
        for i in range(0, len(allZeroMqModules)):
            allZeroMqModules[i].run()
            allDebugModules[i].run()
        
        #waiting for user interrupt
        input()
        
    def stopExecution(self, allZeroMqModules, allDebugModules):
        #stopping the modules
        print("stopping modules")
        for i in range(0, len(allZeroMqModules)):
            allZeroMqModules[i].stop()
            allDebugModules[i].stop()


