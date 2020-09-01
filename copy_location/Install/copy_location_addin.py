import arcpy
import pythonaddins
import subprocess

# count: keeping track of the current row number in the attribute table
# SHAPE@X, SHAPE@Y: x and y coordinate of current point

def LocationCopy():
    # get the current map document and the layer currently selected in TOC
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
    lyr = arcpy.mapping.ListLayers(mxd, pythonaddins.GetSelectedTOCLayerOrDataFrame())[0]
    try:
        matchcount = len(lyr.getSelectionSet())
    except Exception as e1:
        # error message if a layer and a row within that layer are not both selected
        pythonaddins.MessageBox(str(e1), "Error: select both layer and row", {0})
    else:
        # check that only one row is selected
        if matchcount == 1:
            # create search cursor for selected point (read only)
            with arcpy.da.SearchCursor(lyr, ["SHAPE@X", "SHAPE@Y"]) as features:
                for feature in features:
                    # copy coordinates of point
                    try:
                        lx = str(feature[0])
                        ly = str(feature[1])
                        # swap lx ly to fit lat/long format in JRC Global Surface Water Explorer
                        location_text = ly + " " + lx
                        command = "echo " + location_text + " | clip"
                        i = subprocess.check_call(command, shell=True)
                        # message for successful coping
                        pythonaddins.MessageBox(location_text, "copied to clipboard", 0)
                    except Exception as e2:
                        # error message if unexpected errors
                        pythonaddins.MessageBox(str(e2), "Error: coping location", 0)
        else:
            # error message if multiple rows are selected
            pythonaddins.MessageBox("more than one row selected", "Error", {0})


def pantonext():
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
    lyr = arcpy.mapping.ListLayers(mxd, pythonaddins.GetSelectedTOCLayerOrDataFrame())[0]
    with arcpy.da.SearchCursor(lyr, ["FID"]) as features:
        for feature in features:
            # create query and select the next row based on the "count" field
            nextid = int(feature[0]) + 1
            expression = 'FID = ' + str(nextid)
            exp2 = expression.replace("'", "")
            arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", exp2)
            # move map view to centre on the next point at the same scale as is currently being used
            scalenow = df.scale
            df.extent = lyr.getSelectedExtent()
            df.scale = scalenow
            arcpy.RefreshActiveView()


class CopyLocationButton(object):
    """Implementation for copy_location_addin.copy_location (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        LocationCopy()

class NextPointButton(object):
    """Implementation for copy_location_addin.next_point (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pantonext()