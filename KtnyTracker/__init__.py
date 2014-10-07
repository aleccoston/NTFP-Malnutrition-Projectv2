# -*- coding: utf-8 -*-
"""
/***************************************************************************
 KtnyTracker
                                 A QGIS plugin
 geographically tracks patient info from EMR query data
                             -------------------
        begin                : 2014-07-21
        copyright            : (C) 2014 by Alec Coston
        email                : alec.coston@utsouthwester.edu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load KtnyTracker class from file KtnyTracker.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .KTNY_tracker import KtnyTracker
    return KtnyTracker(iface)
