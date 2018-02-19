# -*- coding: utf-8 -*-

from qgis.core import (
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsVectorLayer,
    QgsPointXY,
    QgsGeometry,
    QgsFeature,
    QgsProject)
import math
from PyQt5.QtCore import QCoreApplication


ORTHODEF = '+proj=ortho +lat_0={} +lon_0={} +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'


class Rhumbs:
    def __init__(self, count):
        self.count = count
        self.sin = []
        self.cos = []
        if count != 8:
            raise Exception('Only 8 rhumbs calculation is supported')
        for a in range(0, 405, 45):
            rad = math.radians(a)
            self.sin.append(math.sin(rad))
            self.cos.append(math.cos(rad))


class SpzBuilder:
    def __init__(self, srclayer, nspz, probs):
        self.srclayer = srclayer
        self.nspz = nspz
        self.probs = probs
        self.po = 100 / len(probs)

    def tr(self, message):
        return QCoreApplication.translate('SpzBuilder', message)

    @staticmethod
    def gemAsPoint(g):
        return g.asPoint()

    @staticmethod
    def polygonCentroid(g):
        return g.centroid().asPoint()

    def dirspz(self, p):
        return (self.nspz * p / self.po) if (p > self.po) else self.nspz

    def build(self):
        geomtype = self.srclayer.geometryType()
        topoint = None
        if geomtype == QgsWkbTypes.PointGeometry:
            topoint = self.gemAsPoint
        elif geomtype == QgsWkbTypes.PolygonGeometry:
            topoint = self.polygonCentroid
        geomtype = None
        project = QgsProject.instance()
        features = self.srclayer.getFeatures()
        layercrs = self.srclayer.crs()
        QgsCoordinateTransform.invalidateCache()
        wgstr = QgsCoordinateTransform(layercrs, QgsCoordinateReferenceSystem('EPSG:4326'), project)
        rhumbs = Rhumbs(len(self.probs))
        spzlayer = QgsVectorLayer('Polygon?crs=' + layercrs.toWkt(),
                                  self.tr('SPZ temporary layer'), 'memory')
        spzdata = spzlayer.dataProvider()
        spzlayer.startEditing()
        for f in features:
            geom = f.geometry()
            if geom.isEmpty():
                continue
            geom.transform(wgstr)
            zero_point = topoint(geom)
            pointcrs = QgsCoordinateReferenceSystem.fromProj4(ORTHODEF.format(zero_point.y(), zero_point.x()))
            QgsCoordinateTransform.invalidateCache()
            pointtr = QgsCoordinateTransform(pointcrs, layercrs, project)
            spzpoints = []
            for i in range(rhumbs.count):
                p = self.probs[i]
                l = self.dirspz(p)
                lat = l * rhumbs.cos[i]
                lon = l * rhumbs.sin[i]
                spzpoints.append(pointtr.transform(lon, lat))
            spzgeom = QgsGeometry.fromPolygonXY([spzpoints])
            spzfeature = QgsFeature()
            spzfeature.setGeometry(spzgeom)
            spzdata.addFeatures([spzfeature])
        spzlayer.commitChanges()
        spzlayer.updateExtents()
        project.addMapLayer(spzlayer)
