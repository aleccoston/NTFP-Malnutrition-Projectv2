# -*- coding: utf-8 -*-
"""
/***************************************************************************
 KtnyTracker
                                 A QGIS plugin
 geographically tracks patient info from EMR query data
                              -------------------
        begin                : 2014-07-21
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Alec Coston
        email                : alec.coston@utsouthwestern.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import * #import QSettings, QTranslator, qVersion, QCoreApplication, QVariant, QObject
from PyQt4.QtGui import * #import QAction, QIcon, QColor, QFileDialog
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from KTNY_tracker_dialog import KtnyTrackerDialog

import sys
import os
sys.path.append(os.path.dirname(__file__)+"/modules_malhat")
sys.path.append(os.path.dirname(__file__)+"/modules_malhat/PyPDF2-1.22-py2.7.egg")
#sys.path.append('/Users/Alec_/pythonMods') #note:this will change on PC
#sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/PyPDF2-1.22-py2.7.egg')
import malHat
from makePicture import exportMap
from datetime import date
from dateFunc import add_months
from PyPDF2 import PdfFileMerger, PdfFileReader
import pdb



class KtnyTracker:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'KtnyTracker_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = KtnyTrackerDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&KTNY tracker')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'KtnyTracker')
        self.toolbar.setObjectName(u'KtnyTracker')
        self.exit=False
       

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('KtnyTracker', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/KtnyTracker/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'plots patient info to map'),
            callback=self.run,
            parent=self.iface.mainWindow())
        QObject.connect(self.dlg.loadQuery,SIGNAL("clicked()"),self.loadFile)
        QObject.connect(self.dlg.exportToFile,SIGNAL("clicked()"),self.exportPDF)
        QObject.connect(self.dlg.closeButton, SIGNAL("clicked()"), self.dlg.accept)
        QObject.connect(self.dlg.mapButton, SIGNAL("clicked()"), self.sendToMap)
        QObject.connect(self.dlg.refreshButton, SIGNAL("clicked()"), self.refreshMap)
        QObject.connect(self.dlg.citySaveButton, SIGNAL("clicked()"), self.connectPointLayer)
        QObject.connect(self.dlg.polySaveButton, SIGNAL("clicked()"), self.connectPolyLayer)
        QObject.connect(self.dlg.haltButton, SIGNAL("clicked()"), self.halt)


    def halt(self):
        self.exit=True

    def loadFile(self):
        self.queryFile=QFileDialog.getOpenFileName(None,("Open File"),"~/")
        spliced=self.queryFile.split('/')
        #just displays the name of the file, not the whole path
        self.dlg.queryLabel.setText(spliced[len(spliced)-1])

    def refreshMap(self):
##        self.exit=False
##        for x in range(1000000):
##            if self.exit:
##                break
##            val=int(float(x)/10000)
##            self.dlg.progressBar.setValue(val)
##            
##            QApplication.processEvents()
            

        
        TRANSPARENCY=255-float(self.dlg.transparencySlider.value())*255/100
        BORDERTRANS=TRANSPARENCY-20
        if BORDERTRANS<0:
            BORDERTRANS=0
            
        #pyqtRemoveInputHook()
        #pdb.set_trace()
        
        renderer=self.polyLayer.rendererV2()
        
        for symbol in renderer.symbols():
            sL=symbol.symbolLayer(0).fillColor().getRgb()
            symbol.symbolLayer(0).setColor(QColor.fromRgb(sL[0],sL[1],sL[2],TRANSPARENCY))
            sL=symbol.symbolLayer(0).borderColor().getRgb()
            symbol.symbolLayer(0).setBorderColor(QColor.fromRgb(sL[0],sL[1],sL[2],TRANSPARENCY))
        

         
        #self.polyLayer.setRendererV2(renderer)
        #self.polyLayer.setLayerTransparency(TRANSPARENCY)
        
        self.iface.mapCanvas().refresh()

    def exportPDF(self):
        self.pdfPathName=QFileDialog.getSaveFileName(None,("Open File"),"~/")
        self.YMQ=self.dlg.YMQbox.currentText()
        spliced=self.pdfPathName.split('/')
        self.PDFFILENAME=spliced[len(spliced)-1] #note: not sure if pdf auto added to end
        self.PATHTOPDF=self.pdfPathName.rstrip(self.PDFFILENAME)
        
        print self.pdfPathName

        

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&KTNY tracker'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        #run happens when icon is clicked
        # show the dialog
        
        self.dlg.tabWidget.setCurrentIndex(0) #so "mapAction" tab is shown
        
        canvas=self.iface.mapCanvas()
        if len(canvas.layers())==0:
                QMessageBox.information( self.iface.mainWindow(),"Info", 'Please load project before starting application')
                return
            
        self.connectPolyLayer()
        self.connectPointLayer()
        
        self.dlg.show()
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        #this runs when dialog is closed
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

#####################################################################################
        #all the functions ported from malnut
    def connectPolyLayer(self):
    
        if not self.dlg.polyLayerText.text():
            self.NAMEOFPOLYLAYER=self.dlg.polyLayerText.placeholderText()
        else:
            self.NAMEOFPOLYLAYER=str(self.dlg.polyLayerText.text())
        
        self.polyLayer=NULL
               
        for layer in self.iface.mapCanvas().layers():
                      
                if self.NAMEOFPOLYLAYER.encode('Utf-8') == layer.name().encode('Utf-8'):
                        self.polyLayer=layer
        
        if self.polyLayer==NULL:
                        QMessageBox.information( self.iface.mainWindow(),"Info", 'name of commune layer not found' )
                        
        elif self.dlg.sender()==self.dlg.polySaveButton:  #this means save button was clicked, not initial run
            QMessageBox.information( self.iface.mainWindow(),"Info", 'section layer loaded' )

    def connectPointLayer(self):
        if not self.dlg.cityLayerText.text():
            self.NAMEOFPOINTLAYER=self.dlg.cityLayerText.placeholderText()
        else:
            self.NAMEOFPOINTLAYER=str(self.dlg.cityLayerText.text())

        self.pointLayer=NULL

        for layer in self.iface.mapCanvas().layers():
                if self.NAMEOFPOINTLAYER.encode('Utf-8') == layer.name().encode('Utf-8'):
                                
                    self.pointLayer=layer

        if self.pointLayer==NULL:
                QMessageBox.information( self.iface.mainWindow(),"Info", 'name of city layer not found')
        elif self.dlg.sender()==self.dlg.citySaveButton:
                QMessageBox.information( self.iface.mainWindow(),"Info", 'city layer loaded' )


  
                
    def sendToMap(self):
        #self.queryFile must exist
        try:
            self.queryFile
        except AttributeError:
            QMessageBox.information( self.iface.mainWindow(),"Info", 'Please select a \n data file with query info' )
            return #note: might not break totally
        #if equal, calendar hasn't changed
        if self.dlg.startDate.date()==self.dlg.endDate.date():
            QMessageBox.information( self.iface.mainWindow(),"Info", 'please specify date in settings ' )
            return

        #note: save the renderer with self, so real time adjustment

        
##        this script displays the prevalence of malnutrition in different cities,
##        green cities have low prevalence and red cities have high prevalence.
##        malHat.py gathers data from iSante database query. city_dict is a dictionary
##        with key='city_name' and value=list of number of malnutrition patients in
##        the form of [mild,moderate,severe]. 
##        ex: {'Les Anglais':[0,0,0],'Port a Piment':[10,5,2]}
##        Note: qgis attributes in unicode
##        to set extent, go to makePicture module
##        when porting to windows, change open(PATH,'Utf-8') to open(PATH), and change
##        import Settings to true, change path of PYPDF2 file, path to spelList in spellingmod
##        5 pyscripts

        
        self.exit=False
        spliced=self.queryFile.split('/')
        QUERYFILENAME=spliced[len(spliced)-1] 
        PATHTOQUERYDATA=self.queryFile.rstrip(QUERYFILENAME)
        self.QUERYFILENAME=QUERYFILENAME
        self.PATHTOQUERYDATA=PATHTOQUERYDATA
        self.YMQ=self.dlg.YMQbox.currentText()

        
        
        self.cityList=[]
        FIELD='total' #pick which field to display on map
        CLASSES=3 #number of breaks, ie, colors displayed.
        #^^ Make higher for higher color resolution
        TRANSPARENCY=255 #zero is fully trans, 255 is fully opaque default:100
        #VISITDATEBETWEEN=['2013-01-01','2015-01-1'] #note: change this to scroll bar on QT interface
        
        if self.YMQ=='Monthly':
            MONTHLY=True
        else:
            MONTHLY=False
        if self.YMQ=='Quarterly':
            QUARTERLY=True
        else:
            QUARTERLY=False
        
        #EXPORTTOFILE=True  now button event
        MAPRESOLUTION=400 #resolution of basemap in dpi, usually 300
        ruleBased=True

        #fourth number is transparency, 255=opaque, 0=clear 77=current
        #'stops' makes the ramp pass through more colors, first number is at what %
        RAMP=QgsVectorGradientColorRampV2.create({'color1':'64,180,0,'+str(TRANSPARENCY),
                 'color2':'255,0,0,'+str(TRANSPARENCY),
                'stops':'0.75;255,244,0,'+str(TRANSPARENCY)})
        
       

        PATHTOQUERYDATA=PATHTOQUERYDATA+QUERYFILENAME

        [visitKey,cityKey,unMatchedList]=malHat.sortPatientData(self)

        totalPatients=len(visitKey)
        #here start iterating through malHat and makePicture
        #create actual date objects, easier to manipulate
        #dateMin=date(int(VISITDATEBETWEEN[0].split('-')[0]),int(VISITDATEBETWEEN[0].split('-')[1]),int(VISITDATEBETWEEN[0].split('-')[2]))
        #dateMax=date(int(VISITDATEBETWEEN[1].split('-')[0]),int(VISITDATEBETWEEN[1].split('-')[1]),int(VISITDATEBETWEEN[1].split('-')[2]))
        year=self.dlg.startDate.date().year()
        month=self.dlg.startDate.date().month()
        day=self.dlg.startDate.date().day()
        dateMin=date(year,month,day)
        year=self.dlg.endDate.date().year()
        month=self.dlg.endDate.date().month()
        day=self.dlg.endDate.date().day()
        dateMax=date(year,month,day)
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
                
                canvas = self.iface.mapCanvas()
                ## my layer and "layer" was is now self.pointLayer
                #set current layer to the main malnutrition one, edit it
                
                ##
                self.iface.setActiveLayer(self.pointLayer)
                #layer=myLayer
                #dRange in form [min,max] of date objects
                [city_dict]=malHat.getCityDict(dRange,visitKey,cityKey,self)
                self.dlg.progressBar.setValue(50)
                #city dict in form {city:(mild,moderate,severe)}
                #now place malnut values into QGIS for map export
                self.pointLayer.startEditing()



                if not ruleBased:   #renders all city points, this is obsolete
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



                
                for feature in self.pointLayer.getFeatures():
                        #get list of malnut values
                        #feature attribute strings are unicode
                       
                        
                        cityVals=city_dict[feature['city_name'].encode('Utf-8')]
                        #place in fields
                        feature['severe']=cityVals[2]
                        feature['moderate']=cityVals[1]
                        feature['mild']=cityVals[0]
                        feature['maltot']=cityVals[2]+cityVals[1] #not including mild
                        #feature['sevAndMod']=cityVals[2]+cityVals[1]
                        self.pointLayer.updateFeature(feature)
                        #float(cityVals[0]+cityVals[1]*3+cityVals[2]*6)/3.333

                if ruleBased:

                        #use rules to render only cities that have malnut values in them
                        
                        
                        # define some rules: label, expression, color name, (min scale, max scale)
                        cityRule = ('city', '"severe"+"moderate"+"mild">0  ', 'orange')
                            
                            
                        

                        # create a new rule-based renderer
                        symbol = QgsSymbolV2.defaultSymbol(self.pointLayer.geometryType())
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
                        self.pointLayer.setRendererV2(renderer)


                        #############

                        
                self.pointLayer.commitChanges()
                self.polyLayer.startEditing()
                #maxTotal=0
                #note: maybe add a canvas refresh here
                counter=0
                maxx=int(self.polyLayer.featureCount())*int(self.pointLayer.featureCount())
                increment=int(float(maxx)/20)
                self.dlg.progressBar.setMaximum(maxx)
                
                for feature in self.polyLayer.getFeatures():
                        feature[FIELD]=0  #initialize
                        self.polyLayer.updateFeature(feature)
                for pointObject in self.pointLayer.getFeatures():
                        for poly in self.polyLayer.getFeatures():
                                if self.exit:
                                    return
                                if counter%increment==0:  #only update in sections of 20
                                    self.dlg.progressBar.setValue(counter)
                                    QApplication.processEvents()
                                counter+=1
                                #pyqtRemoveInputHook()
                               # pdb.set_trace()
                                if poly.geometry().contains(pointObject.geometry()): #means point is in polygon
                                        
        
                                        poly[FIELD]=pointObject['maltot']+poly[FIELD]
                                        self.polyLayer.updateFeature(poly)
                                        #if poly[FIELD]>maxTotal:
                                               # maxTotal=poly[FIELD]



                        
                #creates the coloring pattern for the layer
                        #note: make this default, delete the true part of it
                if True:
                        malNutRange = (
                            ('0 to 2', 0.0, 2, [64,110,0,TRANSPARENCY]),
                            ('2 to 10', 2, 10, [210,210,0,TRANSPARENCY]),
                            ('10 to 20', 10, 20, [210,70,0,TRANSPARENCY]),
                            ('>20', 20, 999, [200,0,0,TRANSPARENCY]))
                                                        
                # maybe switch with: '20 to '+str(maxTotal)
                # create a category for each item 
                        ranges = []
                        for label, lower, upper, color in malNutRange:
                            symbol = QgsSymbolV2.defaultSymbol(self.polyLayer.geometryType())
                            symbol.setColor(QColor.fromRgb(color[0],color[1],color[2],color[3]))
                            rng = QgsRendererRangeV2(lower, upper, symbol, label)
                            ranges.append(rng)

                        # create the renderer and assign it to a layer
                        expression = FIELD # field name
                        renderer = QgsGraduatedSymbolRendererV2(expression, ranges)
                else:
                        renderer=QgsGraduatedSymbolRendererV2.createRenderer(self.polyLayer,'total',
                        CLASSES,QgsGraduatedSymbolRendererV2.Jenks,
                        QgsSymbolV2.defaultSymbol(self.polyLayer.geometryType()),RAMP)
                #set the border of the polygons
                for Symbol in renderer.symbols():
                        Symbol.symbolLayer(0).setBorderColor(QColor.fromRgb(0,0,0,TRANSPARENCY))
                for symbol in renderer.symbols():  #set border width for all symbols
                    symbol.symbolLayer(0).setBorderWidth(.08)
    
                
                self.polyLayer.setRendererV2(renderer)
                self.polyLayer.commitChanges()
                self.iface.mapCanvas().refresh()
                self.renderer=renderer
                #note might blow up

            
        QMessageBox.information( self.iface.mainWindow(),"Info", 'Processing Complete' )
        print '%.0f%% of patients unmatched' %(float(len(unMatchedList))/totalPatients*100)
        print 'total number of patients: '+str(totalPatients)
        
