# SPDX-License-Identifier: MIT
"""Run using FreeCAD's bundled Python with its lib directory on PYTHONPATH."""
import os
import json
import FreeCAD as App
import FreeCADGui as Gui
from PySide6 import QtWidgets
import build_model as model

Gui.showMainWindow()
doc = model.build()
initial = model.initial_placements(doc)
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
report = model.validate(doc)
model.export(doc,report)
model.pose(doc,initial,35)
for _ in range(5):
    QtWidgets.QApplication.processEvents()
Gui.activeDocument().activeView().fitAll()
Gui.activeDocument().activeView().saveImage(os.path.join(model.ROOT,'freecad_preview.png'),1600,1000,'White')
model.pose(doc,initial,0)
doc.save()
print('Saved coloured FreeCAD document and native 3D preview')
Gui.getMainWindow().hide()
