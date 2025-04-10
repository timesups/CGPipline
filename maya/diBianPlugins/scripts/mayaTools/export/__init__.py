#coding=utf-8
import pymel.core as pm



def install(menu_id):
    pm.setParent(menu_id,menu=True)
    pm.menuItem("exportTool",label=u'导出工具',subMenu=True,tearOff=True)
    #pm.menuItem(label=u'腾讯导出工具',command=openNormalizeExport)
    pm.menuItem(label=u'abc导出工具',command=openAbcExport)
    pm.menuItem(label=u'相机导出工具',command=openCameraExport)
    pm.menuItem(label=u'XGen导出工具',command=openxGenExport)

    pm.menuItem(label=u'UE角色材质导出工具',command=openchUeExport)
    pm.menuItem(label=u'动画烘焙导出工具',command=openanimtionExport)
    pm.menuItem(label=u'动画自动烘焙导出工具',command=openanimtionAutoExport)



openNormalizeExport = """
from mayaTools.export.normalizeExport import gui
gui.showUI()
"""

openAbcExport = """
from mayaTools.export.abcExport import gui
gui.showUI()
"""

openCameraExport = """
from mayaTools.export.cameraExport import gui
gui.showUI()
"""

openxGenExport = """
from mayaTools.export.xGenExport import gui
gui.showUI()"""





openchUeExport = """
from mayaTools.export.chUeExport import gui
gui.showUI()"""


openanimtionExport = """
from mayaTools.export.animtionExport import gui
gui.showUI()"""


openanimtionAutoExport = """
from mayaTools.export.animtionAutoExport import gui
gui.showUI()"""