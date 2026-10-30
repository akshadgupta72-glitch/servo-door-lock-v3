# SPDX-License-Identifier: MIT
"""SG90 slotted-yoke prototype. Generated designs: CC-BY-4.0; units: mm."""
import os
import math
import json
import FreeCAD as App
import Part
import MeshPart
import Import

ROOT = os.path.dirname(os.path.abspath(__file__))
V = App.Vector
RADIUS = 35.0
AXIS = V(100, 50, 0)
COLORS = {}


def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))


def cylinder(x, y, z, radius, height, axis=V(0, 0, 1)):
    return Part.makeCylinder(radius, height, V(x, y, z), axis)


def capsule(x, y0, y1, radius, z, height):
    return cylinder(x, y0, z, radius, height).fuse(cylinder(x, y1, z, radius, height)).fuse(box(x-radius, y0, z, 2*radius, y1-y0, height)).removeSplitter()


def add(doc, name, shape, color, label=None):
    obj = doc.addObject('Part::Feature', name)
    obj.Shape = shape.removeSplitter()
    obj.Label = label or name.replace('_', ' ')
    COLORS[name] = color
    if App.GuiUp:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = (0.18, 0.18, 0.18)
    return obj


def build():
    doc = App.newDocument('Round_Handle_Lock_V3')
    doc.CreatedBy = 'akshadgupta72-glitch'
    doc.License = 'CC BY 4.0'
    doc.LicenseURL = 'https://creativecommons.org/licenses/by/4.0/'
    brass = (0.73, 0.57, 0.22)
    steel = (0.7, 0.72, 0.75)
    params = doc.addObject('App::FeaturePython', 'Design_Notes')
    for name, value in [('BoltTravel',35), ('HandleDiameter',10), ('SocketDepth',12), ('HandleTopHeight',30), ('HandleGripLength',15), ('HornTopHeight',30), ('HornOverallLength',20), ('CrankPinRadius',35)]:
        params.addProperty('App::PropertyLength', name, 'Reference dimensions')
        setattr(params, name, value)
        params.setEditorMode(name, 1)
    params.addProperty('App::PropertyString','FitStatus')
    params.FitStatus = 'Glue-bond trial prototype. Servo housing, horn width/thickness and mounting ears remain approximate.'
    rail = box(0,0,0,200,30,2)
    for x in (10,190):
        for y in (4,26):
            rail = rail.cut(cylinder(x,y,-1,2.2,4))
    add(doc,'Lock_backplate',rail,brass,'Lock plate - 200 x 30 mm')
    for name, x, length in [('Front_barrel',4,47), ('Rear_barrel',135,60)]:
        tube = cylinder(x,15,9,7,length,V(1,0,0)).cut(cylinder(x-1,15,9,5.35,length+2,V(1,0,0)))
        add(doc,name,tube,brass)
    add(doc,'Sliding_bolt',cylinder(-5,15,9,5,190,V(1,0,0)),steel)
    handle = cylinder(80,15,9,5,21).fuse(cylinder(80,15,13,6.5,2))
    add(doc,'Round_handle_10mm',handle,brass,'Round handle - diameter 10, top 30, smooth length 15 mm')

    # Open round socket fits within the measured 15 mm straight handle section.
    clamp = cylinder(80,15,16,9,12).cut(cylinder(80,15,15,5.3,14))
    # Raised side bridge keeps the yoke above the crank, clear of the round handle.
    bridge = box(85,10,24,4,14,15.5).fuse(box(85,10,35.5,15,14,4))
    yoke = capsule(100,14,51,8,35.5,4)
    clamp = clamp.fuse(bridge).fuse(yoke).cut(capsule(100,14,51,2.3,34.5,6))
    clamp = clamp.cut(cylinder(80,15,15,5.3,16)).removeSplitter()
    add(doc,'Print_clamp_yoke',clamp,(0.1,0.65,0.6),'PRINT - glue-on round socket and slotted arm')

    # Manufacturer body envelope; output location, ears and horn details are assumed.
    servo = box(94,43.9,0,23,12.2,22)
    servo = servo.fuse(cylinder(100,50,22,6,4))
    servo = servo.fuse(cylinder(100,50,26,2.3,2))
    ears = box(89.5,43.9,16,32,12.2,2.5)
    for x in (92,119):
        ears = ears.cut(cylinder(x,50,15,1.1,5))
    servo = servo.fuse(ears)
    add(doc,'SG90_reference',servo,(0.12,0.32,0.85),'SG90 9 g - sourced envelope, approximate details')
    horn = capsule(100,36,50,3,28,2)
    horn = horn.fuse(cylinder(100,50,26,3,4))
    add(doc,'Supplied_servo_horn',horn,(0.92,0.92,0.9),'Existing servo horn - do not print spline')
    crank = capsule(100,15,50,5,30.5,4)
    for yy, radius in [(50,2),(15,1.6)]:
        crank = crank.cut(cylinder(100,yy,29.5,radius,6))
    add(doc,'Print_servo_arm',crank,(0.92,0.43,0.12),'PRINT - flat glue face, 35 mm crank radius')
    bond = capsule(100,36,50,3,30,0.5).cut(cylinder(100,50,29,2,3))
    add(doc,'Glue_layer_reference',bond,(0.94,0.78,0.42),'Glue layer allowance - 0.5 mm, not a printed part')
    add(doc,'Pin_shoulder_reference',cylinder(100,15,34.5,2,7.5).cut(cylinder(100,15,34,1.55,9)),steel,'4 mm OD sleeve on M3 screw - hardware')
    add(doc,'Pin_screw_reference',cylinder(100,15,29,1.5,14).fuse(cylinder(100,15,28,2.8,1)),steel)

    # Simple pedestal under the servo ears, with feet for fixing to the door.
    mount = box(86,40,0,39,20,2).cut(box(93.7,43.6,-1,23.6,12.8,4))
    for x in (89.5,117):
        mount = mount.fuse(box(x,43,2,4.5,14,14))
    for x in (92,119):
        mount = mount.cut(cylinder(x,50,13,0.85,5))
    for x in (89,122):
        for y in (42,58):
            mount = mount.cut(cylinder(x,y,-1,1.7,4))
    add(doc,'Print_servo_mount',mount,(0.3,0.32,0.36),'PRINT - provisional servo pedestal')
    doc.recompute()
    return doc


def initial_placements(doc):
    return {o.Name: App.Placement(o.Placement) for o in doc.Objects if hasattr(o,'Shape')}


def pose(doc, initial, degrees):
    theta = math.radians(degrees)
    shift = RADIUS * math.sin(theta)
    delta = App.Placement(V(shift,0,0), App.Rotation())
    for name in ('Sliding_bolt','Round_handle_10mm','Print_clamp_yoke'):
        doc.getObject(name).Placement = delta.multiply(initial[name])
    rot = App.Rotation(V(0,0,1),degrees)
    spin = App.Placement(AXIS-rot.multVec(AXIS),rot)
    for name in ('Supplied_servo_horn','Print_servo_arm','Glue_layer_reference','Pin_shoulder_reference','Pin_screw_reference'):
        doc.getObject(name).Placement = spin.multiply(initial[name])
    doc.recompute()
    return shift


def validate(doc):
    initial = initial_placements(doc)
    for obj in doc.Objects:
        if hasattr(obj,'Shape'):
            assert obj.Shape.isValid(), obj.Name
            assert len(obj.Shape.Solids)==1, (obj.Name,len(obj.Shape.Solids))
    checks = [('Print_clamp_yoke','SG90_reference'),('Print_clamp_yoke','Print_servo_arm'),('Print_clamp_yoke','Pin_shoulder_reference'),('Print_clamp_yoke','Round_handle_10mm'),('Print_clamp_yoke','Front_barrel'),('Print_clamp_yoke','Rear_barrel'),('Print_servo_arm','Round_handle_10mm'),('Print_servo_arm','SG90_reference'),('Print_clamp_yoke','Supplied_servo_horn'),('Print_clamp_yoke','Pin_screw_reference'),('Print_servo_mount','SG90_reference')]
    maxima = {a+' / '+b:0.0 for a,b in checks}
    for angle in range(91):
        travel = pose(doc,initial,angle)
        for a,b in checks:
            overlap = doc.getObject(a).Shape.common(doc.getObject(b).Shape).Volume
            maxima[a+' / '+b] = max(maxima[a+' / '+b],overlap)
            assert overlap < 1e-5, (angle,a,b,overlap)
        pin_x = 100 + RADIUS*math.sin(math.radians(angle))
        pin_y = 50 - RADIUS*math.cos(math.radians(angle))
        assert abs(pin_x-(100+travel))<1e-8 and 14<=pin_y<=51
    pose(doc,initial,0)
    return {'sweep_degrees':[0,90], 'samples':91, 'travel_mm':35, 'all_shapes_valid_single_solids':True, 'selected_interference_max_volume_mm3':maxima, 'limitations':'Ideal rigid geometry only; no force, friction, hardware-fastener or print-tolerance validation.'}


def export(doc, report):
    doc.saveAs(os.path.join(ROOT,'Round_Handle_Lock_V3.FCStd'))
    objects = [o for o in doc.Objects if hasattr(o,'Shape')]
    Import.export(objects,os.path.join(ROOT,'Round_Handle_Lock_V3.step'))
    for name in ('Print_clamp_yoke','Print_servo_arm','Print_servo_mount'):
        shape = doc.getObject(name).Shape.copy()
        bounds = shape.BoundBox
        shape.translate(V(-bounds.XMin,-bounds.YMin,-bounds.ZMin))
        mesh = MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.08,AngularDeflection=0.15,Relative=False)
        mesh.write(os.path.join(ROOT,name+'_FIT_CHECK.stl'))
    with open(os.path.join(ROOT,'validation.json'),'w') as stream:
        json.dump(report,stream,indent=2)


if __name__ == '__main__':
    model = build()
    result = validate(model)
    export(model,result)
    print(json.dumps(result,indent=2))
