# -*- coding: utf-8 -*-

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from .ui.SpzBuilderDialog import SpzBuilderDialog
import os.path
import qgis


class SpzBuilderPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')
        qm_file = '{}/i18n/SpzBuilder_{}.qm'.format(self.plugin_dir, locale)
        if not os.path.exists(qm_file):
            qm_file = '{}/i18n/SpzBuilder_{}.qm'.format(self.plugin_dir, locale[0:2])
        if os.path.exists(qm_file):
            self.translator = QTranslator()
            self.translator.load(qm_file)
            QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        return QCoreApplication.translate('SpzBuilderPlugin', message)

    def initGui(self):
        icon = self.plugin_dir + '/icons/menu.png'
        self.action = QAction(QIcon(icon),
                              self.tr("SPZ Builder"),
                              self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToVectorMenu(self.tr('SPZ'), self.action)

    def unload(self):
        self.iface.removePluginVectorMenu(self.tr('SPZ'), self.action)

    def run(self):
        dlg = SpzBuilderDialog(qgis.utils.iface.mainWindow())
        dlg.exec_()
        dlg = None
