#malnutrition project
import csv
import codecs
import spellingMod
from datetime import date
#from PyQt4.QtGui import QMessageBox
#import pdb
#from PyQt4.QtCore import pyqtRemoveInputHook


def getCityDict(visitRange,pvKey,patCityKey,TrackerObj):
        
        """
        getCityDict()->[city_dict]
        creates a dictionary of city to tally of malnutrition for patients whos
        visit date is within list_visitRange [minDate,maxDate]
        patCityKey is list of all patients matched to their city
        """
        
        #designate file with patient info in csv

	
        #list of all cities in catchment area of clinic
        #corresponds 1:1 with feature.attribute_cityname on QGIS map
        
	
        patientList=[] #will hold every patient that has a primary visitDate in visitRange
        #TrackerObj.cityList
        sortedPatVisitKey={}
        #initiate city dictionary in the form 'city':(mild,moderate,severe)
        city_dict={}
        visitMin=visitRange[0]
        visitMax=visitRange[1]

        
        
        layer=TrackerObj.iface.activeLayer()
                
        for city in TrackerObj.cityList:
             city_dict[city]=[0,0,0]
        
        
	#first go trhough patient visit key and pull out just those
             #who are in the range of visitRange, place in sortedKey
             #then do if malnut in linelower add to dict
             #patVisitKey='name':[(date,condition),(date,condition),(date,condition)]
        
        for [patName,patList] in pvKey.iteritems():
                for [vDate,condit] in patList:
                        
                        if vDate<=visitMax and vDate>=visitMin:
                                sortedPatVisitKey[patName]=(vDate,condit)
                                break
                        
                
	#sortedPatVisitKey only has patients within the range of visit Dates
        #but sortedPatVisitKey has even patients who are unmatched
        #get a list of the names that are in both these lists
        patientNames=[]
        for key in sortedPatVisitKey.keys():
                if key in patCityKey.keys():
                        patientNames.append(key)
                        

        for patName in patientNames:
                condition=sortedPatVisitKey[patName][1] #the tuple was (date,condition)
                city=patCityKey[patName]
                if 'malnutritionsevere' in condition:
                            
                            city_dict[city][2]+=1
                elif 'malnutritionmoderate' in condition:
                            city_dict[city][1]+=1
                elif 'malnutritionmild' in condition:
                            city_dict[city][0]+=1

            
          
            
       
                    #note: later, prompt user to look for missspellings in unmatched
                    #spellingMod compares leftover patients to a list a common misspellings
            #[city_dict,unMatchedList]=spellingMod.catchSpellings(city_dict,unMatchedList,totalPatients)
			
	return 	[city_dict]


def sortPatientData(TrackerObj):
        from PyQt4.QtGui import QMessageBox
        #note: comment in spelling mod clause
        """takes in cvs and outputs a dict of patients the form
        {'name':[(visitdate,condition),(visitdate,condition)]}
        and a dict of patients paired to their city {'name':city,'name2':city}"""
        
        #designate file with patient info in csv
        #tracker obj contains all relevant variables from the GUI
        path_and_file=TrackerObj.queryFile
        cityList=[]
        unMatchedList=[]
        patientVisitKey={}
        patientCityKey={}
        previousName=''
        NAMEOFPOINTLAYER=TrackerObj.NAMEOFPOINTLAYER #note: make universal
        layer=''
        #only exists if qgis is running
        for getlayer in TrackerObj.iface.mapCanvas().layers():
                if NAMEOFPOINTLAYER.lower() in getlayer.name().lower():
                        layer=getlayer
                
        if layer=='':
                QMessageBox.information( TrackerObj.iface.mainWindow(),"Info", 'incorrect layer specified, check your settings' )
                return # throw more errors
                #note: throw an error
        TrackerObj.iface.setActiveLayer(layer)
        
        for feature in layer.getFeatures(): #incase the cities double dip
                if feature['city_name'].encode('Utf-8') not in cityList:
                        cityList.append(feature['city_name'].encode('Utf-8'))
        #now all cities from QGIS are in a list in cityList
                #in alsoSections, order from smallest to largest
        alsoSections=['Port a Piment','Barbois','Arniquet','Roche a Bateau','Les Cayes','Les Anglais','Coteaux','Port Salut']
        #add port salut later
        #reorder, put cities that are also sections at the end
        for section in alsoSections:
                cityList.remove(section)
                cityList.append(section) #kicks to the end
        TrackerObj.cityList=cityList
                
	with open(path_and_file) as f:
	    #for each patient, sort into correct city and malnutrition info
            f.readline()  #skip header
            lineList=f.readlines()
            #contains multiple lines for patients with multiple visit dates
            for line in lineList:
                    linesplit=line.split(',') #lname,fname,visitDate,location
                    cityString=','.join(linesplit[2:]) #cut name from string to look for city
                    predate=linesplit[2].split('/')
                    visitDate=date(int(predate[2]),int(predate[0]),int(predate[1]))
                    name=linesplit[1]+' '+linesplit[0] #'john doe'
                    condition=getCondition(line)
                    if name!=previousName:
                            #initialize key if key doesn't exist yet
                            patientVisitKey[name]=[(visitDate,condition)]
                    else:
                            patientVisitKey[name].append((visitDate,condition))
                    
                    if name!=previousName:
                            #new name, so new person to look for city
                        successfullyMatched=False
                        for city in cityList:
                                if city.lower() in cityString.lower(): #or spellingMod.containsCity(city,cityString)  #match patient to city
                                        successfullyMatched=True
                                        patientCityKey[name]=city
                                        break #so no double dipping if 2 cities per patient
                        
                           

                        if not successfullyMatched:    
                            unMatchedList.append(line)
                    #note: later, prompt user to look for missspellings in unmatched
                    #spellingMod compares leftover patients to a list a common misspellings
                    #[city_dict,unMatchedList]=spellingMod.catchSpellings(city_dict,unMatchedList,totalPatients)
                    previousName=name
        return (patientVisitKey,patientCityKey,unMatchedList)



def getCondition(line):
        #return mild,moderate,or severe from string
        condition=''
        if 'malnutritionsevere' in line.lower():
                condition='malnutritionsevere'
                            
                            
        elif 'malnutritionmoderate' in line.lower():
                condition='malnutritionmoderate'
                           
        elif 'malnutritionmild' in line.lower():
                condition='malnutritionmild'
                          
        else:
                print 'something is wrong!' #note: throw an error, bad query
        return condition

