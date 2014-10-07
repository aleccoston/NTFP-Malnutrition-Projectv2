# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VectorSelectByPoint
                                 A QGIS plugin
 a simple example for plugin builder
                             -------------------
        begin                : 2014-09-02
        copyright            : (C) 2014 by Meeeee!
        email                : alec.coston@utsouthwestern.edu
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
    """Load VectorSelectByPoint class from file VectorSelectByPoint.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .vector_sbp import VectorSelectByPoint
    return VectorSelectByPoint(iface)
