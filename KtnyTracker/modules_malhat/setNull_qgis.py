
from qgis.utils import iface
from PyQt4.QtCore import QVariant

###resets malnutrition values of each city to NULL

layer=iface.activeLayer()       
layer.startEditing()
for feature in layer.getFeatures():
        feature['severe']=NULL
        feature['moderate']=NULL
        feature['mild']=NULL
        feature['maltot']=NULL
        layer.updateFeature(feature)
#end with:        
layer.commitChanges()
print 'processing complete'



        


