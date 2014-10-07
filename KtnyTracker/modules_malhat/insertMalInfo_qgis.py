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



        
