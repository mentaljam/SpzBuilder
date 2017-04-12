# -*- coding: utf-8 -*-

def classFactory(iface):
    from .SpzBuilderPlugin import SpzBuilderPlugin
    return SpzBuilderPlugin(iface)
