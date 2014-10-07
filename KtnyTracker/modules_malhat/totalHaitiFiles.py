Total Prog Files

from qgis.utils import iface
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QColor
import sys
sys.path.append('/Users/Alec_/pythonMods') #note:this will change on PC
sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/PyPDF2-1.22-py2.7.egg')
import malHat
from makePicture import exportMap
from datetime import date
from dateFunc import add_months
from PyPDF2 import PdfFileMerger, PdfFileReader
import pdb
import os


"""
this script displays the prevalence of malnutrition in different cities,
green cities have low prevalence and red cities have high prevalence.
malHat.py gathers data from iSante database query. city_dict is a dictionary
with key='city_name' and value=list of number of malnutrition patients in
the form of [mild,moderate,severe]. 
ex: {'Les Anglais':[0,0,0],'Port a Piment':[10,5,2]}
Note: qgis attributes in unicode
to set extent, go to makePicture module
when porting to windows, change open(PATH,'Utf-8') to open(PATH), and change
import Settings to true, change path of PYPDF2 file, path to spelList in spellingmod
5 pyscripts

"""
#note: make one script to do it for you, one for manual resizing
#if name of point layer changes, change NAMEOFPOINTLAYER
#note: make a timestamp
fileName='malnutMap' #.pdf gets added later
PATHTOPDF='/Users/Alec_/Documents/'
PATHTOQUERYDATA='/Users/Alec_/Downloads/'
QUERYFILENAME='shortquery1.txt'

NAMEOFPOINTLAYER='west_haiti_citiesv2'
NAMEOFPOLYLAYER='hti_boundaries_sections_communales_adm3_cnigs_polygon'
FIELD='total' #pick which field to display on map
CLASSES=3 #number of breaks, ie, colors displayed.
#^^ Make higher for higher color resolution
TRANSPARENCY=220 #zero is fully trans, 255 is fully opaque default:100
VISITDATEBETWEEN=['2013-01-01','2014-01-1'] #note: add this to legend
MONTHLY=False
QUARTERLY=False
EXPORTTOFILE=True
MAPRESOLUTION=400 #resolution of basemap in dpi, usually 300
importSettings=False
ruleBased=True

if MONTHLY and QUARTERLY:
        print ('pick monthly OR quarterly, not both')
#fourth number is transparency, 255=opaque, 0=clear 77=current
#'stops' makes the ramp pass through more colors, first number is at what %
RAMP=QgsVectorGradientColorRampV2.create({'color1':'64,180,0,'+str(TRANSPARENCY),
         'color2':'255,0,0,'+str(TRANSPARENCY),
        'stops':'0.75;255,244,0,'+str(TRANSPARENCY)})
#maybe here import settings 
if importSettings:
        setFile=open('C:\\Users\\Administrator.WIN-PNUQFF3GR15\\Desktop\\qgis_project\\Settings.txt')
        lines=setFile.read().splitlines()
        for line in lines:
                variable=line.split('=')[0]
                value=[]
                if len(line.split('='))>1:
                        value=line.split('=')[1]
                if variable=='QUERYFILENAME':
                        if '.txt' not in value:
                                value=value+'.txt'
        
                        QUERYFILENAME=value
                elif variable=='VISITDATEBETWEEN':
                        values=line.split('=')[1].split('and')
                        VISITDATEBETWEEN[0]=values[0]
                        VISITDATEBETWEEN[1]=values[1]
                elif variable=='MONTHLY':
                        if 'true' in value.lower():
                                MONTHLY=True
                        else:
                                MONTHLY=False
                elif variable=='YEARLY':
                        if 'true' in value.lower():
                                YEARLY=True
                        else:
                                YEARLY=False
                elif variable=='QUARTERLY':
                        if 'true' in value.lower():
                                QUARTERLY=True
                        else:
                                QUARTERLY=False
                elif variable=='MAPRESOLUTION':
                        MAPRESOLUTION=int(value)
                elif variable=='TRANSPARENCY':
                        TRANSPARENCY=int(value)
                elif variable=='PATHTOPDF':
                        PATHTOPDF=value
                elif variable=='PATHTOQUERYDATA':
                        PATHTOQUERYDATA=value
        setFile.close()
if QUERYFILENAME==NULL:
        print 'ERROR: specify query data name in settings'
else:
        print 'QueryData: '+QUERYFILENAME

PATHTOQUERYDATA=PATHTOQUERYDATA+QUERYFILENAME




[visitKey,cityKey,unMatchedList]=malHat.sortPatientData(PATHTOQUERYDATA)

totalPatients=len(visitKey)
#here start iterating through malHat and makePicture
#create actual date objects, easier to manipulate
dateMin=date(int(VISITDATEBETWEEN[0].split('-')[0]),int(VISITDATEBETWEEN[0].split('-')[1]),int(VISITDATEBETWEEN[0].split('-')[2]))
dateMax=date(int(VISITDATEBETWEEN[1].split('-')[0]),int(VISITDATEBETWEEN[1].split('-')[1]),int(VISITDATEBETWEEN[1].split('-')[2]))
#####
#####
#get appropriate city dict, iterate through visit ranges
fileNameIndex=0
rangeList=[] #if monthly, will be list of month to month ranges.
                #if not monthly, just one range in list
#creates a list of rangelists, where each rangelist is a one month span
if MONTHLY:
        while dateMin<dateMax:
                
                newDate=add_months(dateMin,1)
                rangeList.append([dateMin,newDate])
                dateMin=newDate
elif QUARTERLY:
        while dateMin<dateMax:
                newDate=add_months(dateMin,3)
                rangeList.append([dateMin,newDate])
                dateMin=newDate
else:
        rangeList.append([dateMin,dateMax])
#renderer=[]

#before chopping up, get ranges to fix

        
for dRange in rangeList:
        
        canvas = iface.mapCanvas()
        myLayer=NULL #note: take all this out of loop
        myPolyLayer=NULL
        #set current layer to the main malnutrition one, edit it
        for layer in canvas.layers():
                if NAMEOFPOINTLAYER.lower() in layer.name().lower():
                        myLayer=layer
                if NAMEOFPOLYLAYER.lower() in layer.name().lower():
                        myPolyLayer=layer
        if myLayer==NULL:
                print 'point layer name has changed'
        if myPolyLayer==NULL:
                print 'polygon layer has changed'
        iface.setActiveLayer(myLayer)
        layer=myLayer
        #dRange in form [min,max] of date objects
        [city_dict]=malHat.getCityDict(dRange,visitKey,cityKey,inQgis=True)
        #city dict in form {city:(mild,moderate,severe)}
        #now place malnut values into QGIS for map export
        layer.startEditing()



        if not ruleBased:   #renders all city points
                symbol= QgsSymbolV2.defaultSymbol(layer.geometryType()) #make the points all just green
                renderer = QgsSingleSymbolRendererV2(symbol)

                # create a new simple marker symbol layer, a green circle with a black border
                properties = {'color': 'green', 'color_border': 'black','scale_method':'Map unit','size':'2'}
                symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(properties)

                # assign the symbol layer to the symbol
               #sizeUnit1=mapUnits, sizeUnit0=pixels, always same size rel to canvas
                renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)
                renderer.symbols()[0].symbolLayer(0).setSizeUnit(1)
                renderer.symbols()[0].symbolLayer(0).setSize(300)
        
                # assign the renderer to the layer
                layer.setRendererV2(renderer)        



        
        for feature in layer.getFeatures():
                #get list of malnut values
                #feature attribute strings are unicode
                cityVals=city_dict[feature['city_name'].encode('Utf-8')]
                #place in fields
                feature['severe']=cityVals[2]
                feature['moderate']=cityVals[1]
                feature['mild']=cityVals[0]
                feature['maltot']=cityVals[2]+cityVals[1] #not including mild
                #feature['sevAndMod']=cityVals[2]+cityVals[1]
                layer.updateFeature(feature)
                #float(cityVals[0]+cityVals[1]*3+cityVals[2]*6)/3.333

        if ruleBased:

                #use rules to render only cities that have malnut values in them
                
                
                # define some rules: label, expression, color name, (min scale, max scale)
                cityRule = ('city', '"severe"+"moderate"+"mild">0  ', 'orange')
                    
                    
                

                # create a new rule-based renderer
                symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
                renderer = QgsRuleBasedRendererV2(symbol)

                # get the "root" rule
                root_rule = renderer.rootRule()

                
                    # create a clone (i.e. a copy) of the default rule
                rule = root_rule.children()[0].clone()
                    # set the label, expression and color
                rule.setLabel(cityRule[0])
                rule.setFilterExpression(cityRule[1])
                rule.symbol().setColor(QColor(cityRule[2]))
                    
                    
                    # append the rule to the list of rules
                root_rule.appendChild(rule)

                # delete the default rule
                root_rule.removeChildAt(0)

                
                renderer.symbols()[0].symbolLayer(0).setSizeUnit(1)
                renderer.symbols()[0].symbolLayer(0).setSize(320)
                # apply the renderer to the layer
                layer.setRendererV2(renderer)


                #############

                
        layer.commitChanges()
        myPolyLayer.startEditing()
        #maxTotal=0
        #note: maybe add a canvas refresh here
        for feature in myPolyLayer.getFeatures():
                feature[FIELD]=0  #initialize
                myPolyLayer.updateFeature(feature)
        for pointObject in layer.getFeatures():
                for poly in myPolyLayer.getFeatures():
                        if poly.geometry().contains(pointObject.geometry()): #means point is in polygon
                                poly[FIELD]=pointObject['maltot']+poly[FIELD]
                                myPolyLayer.updateFeature(poly)
                                #if poly[FIELD]>maxTotal:
                                       # maxTotal=poly[FIELD]



                
        #creates the coloring pattern for the layer
                #note: find setting for opacity
        if True:
                malNutRange = (
                    ('0 to 2', 0.0, 2, [0,150,0,TRANSPARENCY]),
                    ('2 to 10', 2, 10, [230,230,0,TRANSPARENCY]),
                    ('10 to 20', 10, 20, [230,90,0,TRANSPARENCY]),
                    ('>20', 20, 999, [222,0,0,TRANSPARENCY]))
                                                
        # maybe switch with: '20 to '+str(maxTotal)
        # create a category for each item 
                ranges = []
                for label, lower, upper, color in malNutRange:
                    symbol = QgsSymbolV2.defaultSymbol(myPolyLayer.geometryType())
                    symbol.setColor(QColor.fromRgb(color[0],color[1],color[2],color[3]))
                    rng = QgsRendererRangeV2(lower, upper, symbol, label)
                    ranges.append(rng)

                # create the renderer and assign it to a layer
                expression = FIELD # field name
                renderer = QgsGraduatedSymbolRendererV2(expression, ranges)
        else:
                renderer=QgsGraduatedSymbolRendererV2.createRenderer(myPolyLayer,'total',
                CLASSES,QgsGraduatedSymbolRendererV2.Jenks,
                QgsSymbolV2.defaultSymbol(myPolyLayer.geometryType()),RAMP)
        #set the border of the polygons
        for Symbol in renderer.symbols():
                Symbol.symbolLayer(0).setBorderColor(QColor.fromRgb(0,0,0,TRANSPARENCY))
        myPolyLayer.setRendererV2(renderer)
        myPolyLayer.commitChanges()
        iface.mapCanvas().refresh()

        if EXPORTTOFILE:
                exportMap(fileName+str(fileNameIndex)+'.pdf',PATHTOPDF,NAMEOFPOINTLAYER,NAMEOFPOLYLAYER,dRange,MAPRESOLUTION)
        fileNameIndex+=1 #so each exported pdf of different map canvas has dif name

#now combine exported files into one using PDFmerger, if MONTHLY is true
print 'processing complete'
print '%.0f%% of patients unmatched' %(float(len(unMatchedList))/totalPatients*100)
print 'total number of patients: '+str(totalPatients)
filetag=''
if QUARTERLY:
       filetag='_quarterly'
if MONTHLY:
        filetag='_monthly'
if (MONTHLY or QUARTERLY) and EXPORTTOFILE:
        listToTrash=[]
        merger=PdfFileMerger()
        for index in range(fileNameIndex): #catch all maps and combine
                currentPdf=PATHTOPDF+fileName+str(index)+'.pdf'
                merger.append(PdfFileReader(file(currentPdf,'rb')))
                listToTrash.append(currentPdf)
        finalFileName=PATHTOPDF+fileName+filetag+'.pdf'
        nameAddon=1
        #make sure the final file to output doesnt already exist. if it does,
        #change the name
        while os.access(finalFileName,os.F_OK):
                finalFileName=PATHTOPDF+fileName+filetag+'_'+str(nameAddon)+'.pdf'
                nameAddon+=1  
        merger.write(finalFileName)
        for File in listToTrash:
                os.remove(File) #cleans up after combine

elif EXPORTTOFILE and not (MONTHLY or QUARTERLY):
       #mapname=fileName+0. change to something legit
        filenameToChange=PATHTOPDF+fileName+'0'+'.pdf'
        addon=1
        newFileName=PATHTOPDF+fileName+'_yearly.pdf'
        while os.access(newFileName,os.F_OK):
                newFileName=PATHTOPDF+fileName+'_yearly'+str(addon)+'.pdf'
                addon+=1  
        os.rename(filenameToChange,newFileName)
else:
        print 'did not export to file. change EXPORTTOFILE in settings if desired'

#note: handle and print errors



        
#################

#malnutrition project
import csv
import codecs
import spellingMod
from datetime import date
#import pdb
#from PyQt4.QtCore import pyqtRemoveInputHook


def getCityDict(visitRange,pvKey,patCityKey,inQgis=False):
        
        """
        getCityDict()->[city_dict]
        creates a dictionary of city to tally of malnutrition for patients whos
        visit date is within list_visitRange [minDate,maxDate]
        patCityKey is list of all patients matched to their city
        """
        #note: change input to filepath instead of ()
        #designate file with patient info in csv
	#path_and_file='/Users/Alec_/Downloads/xlsOutputNoSection.txt'
	#query should leave out patient.section
	#'/Users/Alec_/Downloads/patients200-1.txt'
	#'/Users/Alec_/pythonMods/xlsoutput2.csv'
        #'/Users/Alec_/Downloads/shortquery1.txt'
	
        #list of all cities in catchment area of clinic
        #corresponds 1:1 with feature.attribute_cityname on QGIS map
        
	if not inQgis:
	
                cityList=['Arniquet', 'Port a Piment', 'Roche a Bateau', 'Marcabe',
                           'Chardoni\xc3\xa8re', 'Les Anglais', 'Jabouin', 'Coteaux',
                          'Morass', 'Blondin', 'Debauche', 'Nan Camp\xc3\xa9che']
	
        
        patientList=[] #will hold every patient that has a primary visitDate in visitRange
        cityList=[]
        sortedPatVisitKey={}
        #initiate city dictionary in the form 'city':(mild,moderate,severe)
        city_dict={}
        visitMin=visitRange[0]
        visitMax=visitRange[1]

        if inQgis:
                from qgis.utils import iface  #only exists if qgis is running
                layer=iface.activeLayer()
                for feature in layer.getFeatures():
                        cityList.append(feature['city_name'].encode('Utf-8'))
        #now all cities from QGIS are in a list in cityList
                        #in alsoSections, order from smallest to largest
        alsoSections=['Port a Piment','Barbois','Arniquet','Roche a Bateau','Les Cayes','Les Anglais','Coteaux','Port Salut']
        #reorder, put cities that are also sections at the end, so matched as last resort
        for section in alsoSections:
                cityList.remove(section)
                cityList.append(section) #kicks to the end
                
        for city in cityList:
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


def sortPatientData(path_and_file):

        """takes in cvs and outputs a dict of patients the form
        {'name':[(visitdate,condition),(visitdate,condition)]}
        and a dict of patients paired to their city {'name':city,'name2':city}"""
        #note: change input to filepath instead of ()
        #designate file with patient info in csv
	#path_and_file='/Users/Alec_/Downloads/xlsOutputNoSection.txt'
	#query should leave out patient.section
	#'/Users/Alec_/Downloads/patients200-1.txt'
	#'/Users/Alec_/pythonMods/xlsoutput2.csv'
        #'/Users/Alec_/Downloads/shortquery1.txt'
        cityList=[]
        unMatchedList=[]
        patientVisitKey={}
        patientCityKey={}
        previousName=''
        NAMEOFPOINTLAYER='hti_location_populatedplaces_cnigs_points' #note: make universal
        layer=''
        from qgis.utils import iface  #only exists if qgis is running
        for getlayer in iface.mapCanvas().layers():
                if NAMEOFPOINTLAYER.lower() in getlayer.name().lower():
                        layer=getlayer
                
        if layer=='':
                print 'point layer name has changed'
                #note: throw an error
        iface.setActiveLayer(layer)
        
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
                                if city.lower() in cityString.lower() or spellingMod.containsCity(city,cityString):  #match patient to city
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

################################

from qgis.utils import iface
from qgis.core import *
from PyQt4.QtCore import * #QVariant
from PyQt4.QtGui import QColor
from PyQt4.QtGui import *
import sys
sys.path.append('/Users/Alec_/pythonMods') #note:this will change on PC

def exportMap(fileName,path,POINTLAYER,POLYLAYER,dateRange,resolution=300):

    #note, QgsRectangle=malnutrition_prevLayer.extent()
    """mainLayer=[]
    for layer in iface.mapCanvas().layers():
        if layer.name()==POLYLAYER:
            mainLayer=layer
    rect=mainLayer.extent() #so composer grabs extent from poly layer      
           #keep for later    """
    xmin=-8276492
    ymin=2036988
    xmax=-8181087
    ymax=2084520
    rect=QgsRectangle(xmin,ymin,xmax,ymax)

    #assume picture is ready to be exported
    mapRenderer = iface.mapCanvas().mapRenderer()
    mapRenderer.setExtent(rect) 
    c = QgsComposition(mapRenderer)
    c.setPlotStyle(QgsComposition.Print)
    #stretch map over whole composer paper
    x, y = 0, 0
    w, h = c.paperWidth(), c.paperHeight()
    composerMap = QgsComposerMap(c, x,y,w,h)
    c.addItem(composerMap)
    titleString='Malnutrition Prevalence from '+dateRange[0].strftime('%B %d, %Y')+' to '+dateRange[1].strftime('%B %d, %Y')
    #add labels
    composerLabel = QgsComposerLabel(c)
    composerLabel.setText(titleString)
    composerLabel.adjustSizeToText()
    c.addItem(composerLabel)
    #set legend
    legend = QgsComposerLegend(c)
    index=0
    layerindex=[]
    #grab the polygon layer from layerset, only it goes in legend
    #note: below is sloppy
    for layer in mapRenderer.layerSet():
        if POLYLAYER.lower().split(' ')[0] in layer.lower():
            layerindex=index
        index+=1    
    legend.model().setLayerSet([mapRenderer.layerSet()[layerindex]]) 
    
                                         
    c.addItem(legend) 
    # set both label's position and size (width 10cm, height 3cm)
    composerLabel.setItemPosition(100,10)
    #composerLabel.setFrameEnabled(False)
    #c.setPaperSize(width, height) in milimeteres
    c.setPrintResolution(resolution)

    #output to pdf
    printer = QPrinter()
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(path+fileName)
    printer.setPaperSize(QSizeF(c.paperWidth(), c.paperHeight()), QPrinter.Millimeter)
    printer.setFullPage(True)
    printer.setColorMode(QPrinter.Color)
    printer.setResolution(c.printResolution())

    pdfPainter = QPainter(printer)
    paperRectMM = printer.pageRect(QPrinter.Millimeter)
    paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
    c.render(pdfPainter, paperRectPixel, paperRectMM)
    pdfPainter.end()
    print 'rendered a map'
#######################

import ast
"""
takes list of patients who could not be matched to a city, probably
because the city was misspelled. compares to a growing list of common
misspellings to find a match

"""

def catchSpellings(city_dict,unMatchedList,totalPatients):
    #note: consolidate paths
    dictOfSpellings={}
    newUnMatchedList=[]
    file=open('/Users/Alec_/pythonMods/altSpellingListv2.txt')
    #make dict of misspellings from lines in file=dictOfSpellings
    for line in file.read().splitlines():
        key=ast.literal_eval(line.split(':')[0]) 
        listS=ast.literal_eval(line.split(':')[1])
        dictOfSpellings[key]=listS
    file.close()
    
    
    #go through unmatched list searching for match in list of common mispels
    while len(unMatchedList)>0:
        currentPatient=unMatchedList.pop()
        foundMatch=False
        for [cityName,mispelList] in dictOfSpellings.iteritems():
            #cycle through each city and its spellings to find match
            for spelling in mispelList:
                if spelling.lower() in currentPatient.lower():
                    #print 'found a match!'
                    foundMatch=True
                    #add patient to malnutrition data structure
                    if 'malnutritionsevere' in currentPatient.lower():
                            
                            city_dict[cityName][2]+=1
                    elif 'malnutritionmoderate' in currentPatient.lower():
                            city_dict[cityName][1]+=1
                    elif 'malnutritionmild' in currentPatient.lower():
                            city_dict[cityName][0]+=1
                    else:
                            pass #note: throw an error, bad query
                if foundMatch:
                    break #out of misSpelList for loop
            if foundMatch:
                break #out of city search for this patient
            
        if not foundMatch:
            #catches patients still unmatched
            newUnMatchedList.append(currentPatient) 

    print '%.0f%% of patients unmatched' %(float(len(newUnMatchedList))/totalPatients*100)
    return [city_dict,newUnMatchedList]
    

def containsCity(cityName,patientInfo):
    #note: consolidate paths
    dictOfSpellings={}
    
    file=open('/Users/Alec_/pythonMods/altSpellingListv2.txt')
    #make dict of misspellings from lines in file=dictOfSpellings
    for line in file.read().splitlines():
        key=ast.literal_eval(line.split(':')[0]) 
        listS=ast.literal_eval(line.split(':')[1])
        dictOfSpellings[key]=listS
    file.close()
    isaMatch=False
    if dictOfSpellings.has_key(cityName):
        
        spellingList=dictOfSpellings[cityName]
    else:
        return False
    for city in spellingList:
        if city.lower() in patientInfo.lower():
            isaMatch=True

    return isaMatch
    
    
                        
        
