# definition of the component:
# is the geometry point, curve or surface
# is a valid polysurface (solid)
# is the geometry at proper position
# is the geometry planner
# is the geometry complex : too many edges, short edges, too near curves

import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math
import ghpythonlib.component as ghc  
import Grasshopper as gh

# store all communication required to user
readMe = []
# invalid geometries are contained curves, points, surfaces
invalid_geometry = []
# suspicious geometries are contained too complex geometries,
# too many edges, too many short edges, closeness of edges
suspicious_geometry = []
# valid geometries should pass all the checks
valid_geometry = []

# the model tolerance presents a threshold by which the 0 value should be found
model_tolerance = 1e-6
rhino_tolerance = sc.doc.ModelAbsoluteTolerance

critics = {
    "max_edges": 1000,
    "min_tol": 0.1,
    "min_edge_length": rhino_tolerance / 10,
    "min_edge_distance": 10,
    "min_dimension": 3,
    "min_angel_within_curves": 1,
    "min_height": 1
}

messages = {
    "succced": "The model has passed the criterial successfully.",
}

displayMessage = {
    "tooMuchShort": "Short edge",
    "tooNearCrv": "Bad geometry",
    "tooMuchSmall": "Small surface",
    "tooMuchEdges": "Complex geo",
    "Non_enough_height": "Not 1 meter"
}

# ____________________________________________________________
# this function should get the base surface of given geometry
def getBaseSurface(faces):
    for f in faces:
        u = f.Domain(0).Mid
        v = f.Domain(1).Mid
        n = f.NormalAt(u, v)
        if n.Z < -0.999 and f.IsPlanar(model_tolerance):
            return f
    return None

def getFaceEdges(face):
    edges = []
    for loop in face.Loops:
        for trim in loop.Trims:
            edge = trim.Edge
            if edge and edge not in edges:
                edges.append(edge)
    return edges

# ____________________________________________________________
# this function renders the message to the user on a point
def renderError(p, text):
    sc.doc = Rhino.RhinoDoc.ActiveDoc
    dot = Rhino.Geometry.TextDot(text, p)
    sc.doc.Objects.AddTextDot(dot)
    sc.doc = ghdoc

# ____________________________________________________________
# this function deletes all textdots to avoid chaos
def deletTextDot():
    sc.doc = Rhino.RhinoDoc.ActiveDoc
    for obj in sc.doc.Objects:
        if isinstance(obj.Geometry, Rhino.Geometry.TextDot):
            sc.doc.Objects.Delete(obj, True)
    sc.doc = ghdoc

# ____________________________________________________________
# this function should check if the geometry is placed correctly
def zStatus(g):
    bb = g.GetBoundingBox(rg.Plane.WorldXY)
    return round(bb.Max.Z) == 0

# ____________________________________________________________
# this function should place the bad geometry in the right position
def placeOnZero(g):
    bb = g.GetBoundingBox(rg.Plane.WorldXY)
    zOffset = bb.Max.Z  
    g.Transform(rg.Transform.Translation(0, 0, -zOffset))
    return g

def getGeometryHeight(g):
    bb = g.GetBoundingBox(True)
    return bb.Max.Z - bb.Min.Z >= critics["min_height"], bb.Max.Z - bb.Min.Z

# ____________________________________________________________
# this function should return the vertex and edge of a surface
def getFaceEdge_Vertx(face):
    edges = []
    vertices = []
    for loop in face.Loops:
        for trim in loop.Trims:
            edge = trim.Edge
            if not edge:
                continue
            crv = edge.DuplicateCurve()
            if crv:
                edges.append(crv)
            v0 = edge.StartVertex
            v1 = edge.EndVertex
            if v0:
                vertices.append(v0.Location)
            if v1:
                vertices.append(v1.Location)
    return edges, vertices

# ____________________________________________________________
# this function should check if the geometry is planner
def isPlaner(faces):
    if getBaseSurface(faces):
        return True
    return False

# ____________________________________________________________
# this function should give the tangent of two curves
def tangentAtPoint(curve, point, model_tolerance=1e-6):
    if point.DistanceTo(curve.PointAtStart) <= model_tolerance:
        t = curve.Domain.T0
    elif point.DistanceTo(curve.PointAtEnd) <= model_tolerance:
        t = curve.Domain.T1
    else:
        return None
    tan = curve.TangentAt(t)
    tan.Unitize()
    return tan

# ____________________________________________________________
# this function checks if the angle between the curves are within defined tolerance
def curveProximity(face, min_angle_deg, geo_id):  
    edges, vertx = getFaceEdge_Vertx(face)
    isAccpetable = []

    for p in vertx:
        connected = []
        for crv in edges:
            if p.DistanceTo(crv.PointAtStart) <= model_tolerance or \
               p.DistanceTo(crv.PointAtEnd) <= model_tolerance:
                connected.append(crv)
        if len(connected) < 2:
            continue
        for i in range(len(connected)):
            for j in range(i + 1, len(connected)):
                t1 = tangentAtPoint(connected[i], p, model_tolerance)
                t2 = tangentAtPoint(connected[j], p, model_tolerance)
                if not t1 or not t2:
                    continue
                angle_deg = math.degrees(rg.Vector3d.VectorAngle(t1, t2))
                tightness_deg = 180.0 - angle_deg
                isAccpetable.append(tightness_deg > min_angle_deg)
    return all(isAccpetable)

# ____________________________________________________________
# this function checks if the geometry is big enough
def isBigEnough(face, min_dimension):
    area_props = rg.AreaMassProperties.Compute(face)
    return area_props.Area > min_dimension, area_props.Area

# ____________________________________________________________
# this function checks geometry at the high level
def brepReport(g, geo_id): 
    if not isinstance(g, rg.Brep):
        geo_type = ""
        if isinstance(g, rg.Curve):
            geo_type = "curve"
        elif isinstance(g, rg.Point) or isinstance(g, rg.Point3d):
            geo_type = "point"
        elif isinstance(g, rg.Surface):
            geo_type = "Surface"
        invalid_geometry.append(g)
        readMe.append(f"geometry by index {geo_id} is a {geo_type}, it is automatically removed from geometry list")
        return False
    elif g.Faces.Count == 1 and not g.IsSolid:
        invalid_geometry.append(g)
        readMe.append(f"geometry by index {geo_id} is a surface, it is automatically removed from geometry list")
        return False
    elif not isPlaner(list(g.Faces)):
        invalid_geometry.append(g)
        readMe.append(f"geometry by index {geo_id} is not planer, (if they are bridge or leveled street can be ignored)")
        return False
    else:
        baseSrf = getBaseSurface(list(g.Faces))
        baseEdg = getFaceEdges(baseSrf)
        return {
            "faces": [f for f in g.Faces],
            "edges": [e for e in g.Edges],
            "vertices": [v for v in g.Vertices],
            "faces_count": g.Faces.Count,
            "edges_count": g.Edges.Count,
            "edges_Vertices": g.Vertices.Count,
            "is_solid": g.IsSolid,
            "is_valid": g.IsValid,
            "is_manifold": g.IsManifold,
            "baseFace": baseSrf,
            "baseEdges": baseEdg,
        }

# ____________________________________________________________
# this function utilizes the brepReport to evaluate the complexity of a geometry
def checkGeometryValidation(r, geo_id):  
    def edgeShortCheck():
        result = []
        for l in r["baseEdges"]:
            state = l.GetLength() > critics["min_edge_length"]
            result.append(state)
            if not state:
                renderError(l.PointAtEnd, displayMessage["tooMuchShort"])
        return all(result)

    def curveProximityCheck():
        result = curveProximity(r["baseFace"], critics["min_angel_within_curves"], geo_id)
        if not result:
            pt = rg.AreaMassProperties.Compute(r["baseFace"]).Centroid
            renderError(pt, displayMessage["tooNearCrv"])
        return result

    def dimensionCheck():
        isEnough, actualArea = isBigEnough(r["baseFace"], critics["min_dimension"])
        if not isEnough:
            pt = rg.AreaMassProperties.Compute(r["baseFace"]).Centroid
            renderError(pt, displayMessage["tooMuchSmall"])
        return isEnough

    def edgeNumCheck():
        isSimple = r["edges_count"] < critics["max_edges"]
        if not isSimple:
            pt = rg.AreaMassProperties.Compute(r["baseFace"]).Centroid
            renderError(pt, displayMessage["tooMuchEdges"])
        return isSimple

    def heightCheck():
        hasProperHeight, height = getGeometryHeight(g)
        if not hasProperHeight:
            pt = rg.AreaMassProperties.Compute(r["baseFace"]).Centroid
            renderError(pt, displayMessage["Non_enough_height"])
        return hasProperHeight

    def positionCheck():
        isOk = zStatus(geo[geo_id])
        if not isOk:
            readMe.append(f"Geometry by index [{geo_id}] is not placed at zero or not planner")
        return isOk

    return all((edgeShortCheck(), curveProximityCheck(), dimensionCheck(), edgeNumCheck(), heightCheck(), positionCheck()))

def isNull(geo):
    if len(geo) == 0:
        return True
    return any(g is None for g in geo)

try:
    if isNull(geo):
        raise RuntimeError("Input geometry failed to collect data")

    if rhino_tolerance < 0.1:
        readMe.append(f"The tolerance of the model is very small (found it as {rhino_tolerance}), change it to {critics['min_tol']} to avoid troubles.")

    deletTextDot()

    for geo_id, g in enumerate(geo): 
        report = brepReport(g, geo_id)
        if report and all((report["is_solid"], report["is_manifold"], report["is_valid"])):
            if not checkGeometryValidation(report, geo_id):
                suspicious_geometry.append(g)
            else:
                valid_geometry.append(g)
        elif report and not all((report["is_solid"], report["is_manifold"], report["is_valid"])):
            readMe.append(f"The geometry by id {geo_id} is not valid because it is not an acceptable geometry.")
            invalid_geometry.append(g)

    if place_at_plane:
        for g in suspicious_geometry[:]:
            if not zStatus(g):
                g = placeOnZero(g)
                valid_geometry.append(g)
                suspicious_geometry.remove(g)  

    if len(valid_geometry) == len(geo):
        readMe.append(messages["succced"])

except Exception as e:
    ghc.add_warning(f"{e}")
