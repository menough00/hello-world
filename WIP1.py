Wimport clr
import sys
import os
import math
from System.Collections.Generic import List

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('RevitNodes')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')

from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Ensure document manager instance
doc = DocumentManager.Instance.CurrentDBDocument

# Correct path to the family template file
template_path = r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft'
save_path = r'C:\Users\nickm\OneDrive\Music\Documents\Revit\SiloFamily.rfa'

# Debugging information
print(f"Template path: {template_path}")
print(f"Save path: {save_path}")

# Check if template path exists
if not os.path.exists(template_path):
    print(f"Failed to find template path: {template_path}")
    raise Exception(f"Template path does not exist: {template_path}")
else:
    print(f"Template path exists: {template_path}")

# Check if save directory exists
if not os.path.isdir(os.path.dirname(save_path)):
    print(f"Failed to find save directory: {os.path.dirname(save_path)}")
    raise Exception(f"Save directory does not exist: {os.path.dirname(save_path)}")
else:
    print(f"Save directory exists: {os.path.dirname(save_path)}")

try:
    # Create a new family document
    famDoc = doc.Application.NewFamilyDocument(template_path)
    print("New family document created")

    # Start a transaction in the new family document
    famTransaction = Transaction(famDoc, "Create Silo")
    famTransaction.Start()
    print("Family transaction started")

    # Create a reference plane for the base
    base_plane = SketchPlane.Create(famDoc, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ.Zero))
    print("Base plane created")

    # Draw the base circle
    center = XYZ.Zero
    radius = 5.0
    base_circle = Arc.Create(center, radius, 0, 2 * math.pi, XYZ.BasisX, XYZ.BasisY)
    curveArray = CurveArray()
    curveArray.Append(base_circle)
    print("Base circle drawn")

    # Convert CurveArray to CurveLoop
    curveLoop = CurveLoop()
    for curve in curveArray:
        curveLoop.Append(curve)

    # Create the cylindrical body extrusion
    curveArrArray = CurveArrArray()
    curveArrArray.Append(curveArray)
    cylinder = famDoc.FamilyCreate.NewExtrusion(True, curveArrArray, base_plane, 20.0)
    print("Cylindrical body created")

    # Create the conical bottom
    top_radius = 5.0
    bottom_radius = 2.0
    height = 10.0

    # Define the top and bottom circles of the cone
    top_center = XYZ(0, 0, 20)
    bottom_center = XYZ(0, 0, 10)

    # Create CurveLoops for top and bottom profiles
    top_curveLoop = CurveLoop()
    top_curveLoop.Append(Arc.Create(XYZ.Zero, top_radius, 0, 2 * math.pi, XYZ.BasisX, XYZ.BasisY))

    bottom_curveLoop = CurveLoop()
    bottom_curveLoop.Append(Arc.Create(XYZ.Zero, bottom_radius, 0, 2 * math.pi, XYZ.BasisX, XYZ.BasisY))

    # Create a list of CurveLoops
    top_profile = List[CurveLoop]()
    top_profile.Add(top_curveLoop)

    bottom_profile = List[CurveLoop]()
    bottom_profile.Add(bottom_curveLoop)

    # Create the blend
    blend = famDoc.FamilyCreate.NewBlend(True, top_profile, bottom_profile, height)
    print("Conical bottom created")

    # Create the support structure
    # Four legs
    leg_height = 10.0
    leg_radius = 0.2
    leg_positions = [
        XYZ(top_radius - leg_radius, top_radius - leg_radius, 0),
        XYZ(-(top_radius - leg_radius), top_radius - leg_radius, 0),
        XYZ(top_radius - leg_radius, -(top_radius - leg_radius), 0),
        XYZ(-(top_radius - leg_radius), -(top_radius - leg_radius), 0)
    ]

    for pos in leg_positions:
        # Create a circle for the leg
        leg_base_circle = Arc.Create(pos, leg_radius, 0, 2 * math.pi, XYZ.BasisX, XYZ.BasisY)
        leg_curveArray = CurveArray()
        leg_curveArray.Append(leg_base_circle)

        # Convert to CurveLoop
        leg_curveLoop = CurveLoop()
        for curve in leg_curveArray:
            leg_curveLoop.Append(curve)

        # Create the extrusion for the leg
        leg_curveArrArray = CurveArrArray()
        leg_curveArrArray.Append(leg_curveArray)
        leg_extrusion = famDoc.FamilyCreate.NewExtrusion(True, leg_curveArrArray, base_plane, leg_height)
        print("Support leg created at position:", pos)

    # Commit the family transaction
    famTransaction.Commit()
    print("Family transaction committed")

    # Save the family
    famDoc.SaveAs(save_path)
    print(f"Family saved successfully at {save_path}")

    # Close the family document
    famDoc.Close(False)
    print("Family document closed")

except Exception as e:
    if famTransaction.HasStarted():
        famTransaction.RollBack()
    print(f"An error occurred: {e}")
    raise e
