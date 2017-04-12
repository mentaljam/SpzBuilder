# -*- coding: utf-8 -*-

import os, qgis
from PyQt4 import QtGui
from .ui_SpzBuilderDialog import Ui_SpzBuilderDialog
from SpzBuilder.SpzBuilder import SpzBuilder
from qgis.gui import QgsMapLayerProxyModel


class SpzBuilderDialog(QtGui.QDialog, Ui_SpzBuilderDialog):
    def __init__(self, parent=None):
        super(SpzBuilderDialog, self).__init__(parent)
        self.setupUi(self)
        self.srcLayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer | QgsMapLayerProxyModel.PolygonLayer)
        self.windRoseLabel.setPixmap(QtGui.QPixmap(
            os.path.dirname(__file__) + '/../icons/windrose.png'))
        qgis.core.QgsApplication.instance().focusChanged.connect(self.onFocusChanged)
        self.accepted.connect(self.onAccepted)
        self.srcLayerComboBox.currentIndexChanged.connect(self.setOkEnabled)
        self.setOkEnabled()

    def allSpinBoxes(self):
        sbs = [ self.nSpinBox, self.neSpinBox, self.eSpinBox, self.seSpinBox,
               self.sSpinBox, self.swSpinBox, self.wSpinBox, self.nwSpinBox ]
        return sbs

    def onFocusChanged(self, old, now):
        sbs = self.allSpinBoxes()
        if not now in sbs:
            return
        sbs.remove(now)
        maxFrec = 100.0
        for sb in sbs:
            maxFrec -= sb.value()
        now.setMaximum(maxFrec)

    def onAccepted(self):
        sbs = self.allSpinBoxes()
        probs = []
        for sb in sbs:
            probs.append(sb.value())
        builder = SpzBuilder(
            self.srcLayerComboBox.currentLayer(),
            self.nSpzSpinBox.value(),
            probs)
        builder.build()

    def setOkEnabled(self):
        okButton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        okButton.setEnabled(self.srcLayerComboBox.currentIndex() != -1)

    def closeEvent(self, evnt):
        qgis.core.QgsApplication.instance().focusChanged.disconnect(self.onFocusChanged)
