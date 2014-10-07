# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VectorSelectByPoint
                                 A QGIS plugin
 a simple example for plugin builder
                              -------------------
        begin                : 2014-09-02
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Meeeee!
        email                : alec.coston@utsouthwestern.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import * #QSettings, QTranslator, qVersion, QCoreApplication
from qgis.gui import * #new
from qgis.core import QgsGeometry, QgsFeature
from PyQt4.QtGui import * #QAction, QIcon
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from vector_sbp_dialog import VectorSelectByPointDialog
import os.path


class VectorSelectByPoint:
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
            'VectorSelectByPoint_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = VectorSelectByPointDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&vector_selectbypoint')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'VectorSelectByPoint')
        self.toolbar.setObjectName(u'VectorSelectByPoint')
        ############
        self.canvas = self.iface.mapCanvas() #CHANGE
        # this QGIS tool emits as QgsPoint after each click on the map canvas
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        self.provider=None
        self.selectList=[]
        self.clayer=None

        

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
        return QCoreApplication.translate('VectorSelectByPoint', message)


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

        icon_path = ':/plugins/VectorSelectByPoint/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'some text for the menu'),
            callback=self.run,
            parent=self.iface.mainWindow())

        QObject.connect(self.dlg.chkActivate,SIGNAL("stateChanged(int)"),self.stateChanged)
        
        #QMessageBox.information( self.iface.mainWindow(),"Info", "connect = %s"%str(result) )
        # connect our select function to the canvasClicked signal
        
        #QMessageBox.information( self.iface.mainWindow(),"Info", "connect = %s"%str(result) )


    def stateChanged(self, state):
        
        if state==Qt.Checked:
            result = QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDown)
            result = QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeature)

        else:
            result = QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeature)
            result = QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDown)

    
    def handleMouseDown(self, point, button):
        self.dlg.clearTextBrowser()
        self.dlg.setTextBrowser( str(point.x()) + " , " +str(point.y()) )
        #QMessageBox.information( self.iface.mainWindow(),"Info", "X,Y = %s,%s" % (str(point.x()),str(point.y())) )


    def selectFeature(self, point, button):
       #QMessageBox.information( self.iface.mainWindow(),"Info", "in selectFeature function" )
       # setup the provider select to filter results based on a rectangle
       pntGeom = QgsGeometry.fromPoint(point)
       # scale-dependent buffer of 2 pixels-worth of map units
       pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       rect = pntBuff.boundingBox()
       # get currentLayer and dataProvider
       #self.cLayer = self.canvas.currentLayer()
       self.selectList = []
    
       if self.cLayer:
              # print pntGeom.asPoint()
               
               #self.provider = self.cLayer.dataProvider()
               ##feat = QgsFeature()
               # create the select statement
             ##  provider.select([],rect) # the arguments mean no attributes returned, and do a bbox filter with our buffered rectangle to limit the amount of features
               #while provider.nextFeature(feat):
               for feat in self.provider.getFeatures():
                       
                       # if the feat geom returned from the selection intersects our point then put it in a list
                       if feat.geometry().intersects(pntGeom):
                               
                               self.selectList.append(feat.id())
                               self.feature=feat

               # make the actual selection
               if self.selectList:
                   self.cLayer.setSelectedFeatures(self.selectList)
                   self.updateTextBrowser()
       else:
               #QMessageBox.information( self.iface.mainWindow(),"Info", "No layer currently selected in TOC" )
               print 'u messed up'

    def updateTextBrowser(self):
    # if we have a selected feature
        if self.selectList:
            # find the index of the 'NAME' column, branch if has one or not
            nIndx = self.provider.fieldNameIndex('commune')
            # get our selected feature from the provider, but we have to pass in an empty feature and the column index we want
            sFeat = QgsFeature()
            if self.feature:
                # only if we have a 'NAME' column
                if nIndx != -1:
                    # get the feature attributeMap
                    attMap = self.feature.attributes()
                    # clear old TextBrowser values
                    self.dlg.clearTextBrowser()
                    # now update the TextBrowser with attributeMap[nameColumnIndex]
                    # when we first retrieve the value of 'NAME' it comes as a QString so we have to cast it to a Python string
                    self.dlg.setTextBrowser( str( attMap[nIndx] ))
        print self.dlg.comboBox.currentText()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&vector_selectbypoint'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.cLayer=self.iface.mapCanvas().currentLayer()
        if self.cLayer:
            self.provider=self.cLayer.dataProvider()
        self.canvas.setMapTool(self.clickTool)
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
