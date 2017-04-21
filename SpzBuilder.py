# -*- coding: utf-8 -*-

from qgis.core import (
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsVectorLayer,
    QgsPoint,
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

    @staticmethod
    def trToWgs(crs):
        wgscrs = QgsCoordinateReferenceSystem()
        wgscrs.createFromString('EPSG:4326')
        return QgsCoordinateTransform(crs, wgscrs)

    @staticmethod
    def trToPointCrs(point, crs):
        pointcrs = QgsCoordinateReferenceSystem()
        pointcrs.createFromProj4(ORTHODEF.format(point.y(), point.x()))
        return QgsCoordinateTransform(pointcrs, crs)

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
        features = self.srclayer.getFeatures()
        layercrs = self.srclayer.crs()
        wgstr = self.trToWgs(layercrs)
        rhumbs = Rhumbs(len(self.probs))
        spzlayer = QgsVectorLayer('Polygon?crs=' + layercrs.toWkt(), self.tr('SPZ temporary layer'), 'memory')
        spzdata = spzlayer.dataProvider()
        spzlayer.startEditing()
        for f in features:
            geom = f.geometry()
            if geom.isEmpty():
                continue
            spzpoints = []
            for i in range(rhumbs.count):
                p = self.probs[i]
                l = self.dirspz(p)
                lat = l * rhumbs.cos[i]
                lon = l * rhumbs.sin[i]
                spzpoints.append(QgsPoint(lon, lat))
            spzgeom = QgsGeometry.fromPolygon([spzpoints])
            geom.transform(wgstr)
            pointtr = self.trToPointCrs(topoint(geom), layercrs)
            spzgeom.transform(pointtr)
            spzfeature = QgsFeature()
            spzfeature.setGeometry(spzgeom)
            spzdata.addFeatures([spzfeature])
        spzlayer.commitChanges()
        spzlayer.updateExtents()
        QgsProject.instance().addMapLayer(spzlayer)