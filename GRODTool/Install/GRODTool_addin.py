import arcpy, pythonaddins, numpy, os

arcpy.env.overwriteOutput = True

# new field variable declarations
decidefield = "GROD_Eva"
evaluatefield = "Evaluation"
curbfield = "Kurbs"
newx = "x2"
newy = "y2"
movecount = "movecount"

def validateandrun(thingtodo, answer, clickedx, clickedy):
    # set active mxd, and layer which is currently selected in the TOC
    mxd = arcpy.mapping.MapDocument("CURRENT")
    lyr = arcpy.mapping.ListLayers(mxd, pythonaddins.GetSelectedTOCLayerOrDataFrame())[0]
    try:
        matchcount = len(lyr.getSelectionSet())
    except:
        # error message if a layer and a row within that layer are not both selected
        pythonaddins.MessageBox("select both layer and row", "Error", {0})
    else:
        # check that only one row is selected
        if matchcount == 1:
            # calls a function to to one of: update attribute (1), move the point (2), move view to next point (3),
            # reset to original point location (4), or visualize the current and original location of points (5)
            if thingtodo == 1: # filling text into grod_eva field
                groddecide(answer)
            elif thingtodo == 2: # there will be a move with two extra parameters
                movepoint(clickedx, clickedy)
            elif thingtodo == 3: # button next point
                pantonext()
            elif thingtodo == 4: # the moved point will be reset to its original location
                resetpoint()
            elif thingtodo == 5: # filling text into curb field
                curbdecide(answer)
            elif thingtodo == 6: # filling text into evaluation field
                evaluate(answer)
        else:
            # error message if multiple rows are selected
            pythonaddins.MessageBox("more than one row selected", "Error", {0})

# update grodeva field with text, without moving the point
def groddecide(answer):
    mxd = arcpy.mapping.MapDocument("CURRENT")
    lyr = arcpy.mapping.ListLayers(mxd, pythonaddins.GetSelectedTOCLayerOrDataFrame())[0]
    # create cursor for selected point
    with arcpy.da.UpdateCursor(lyr, ["count", decidefield]) as features:
        for feature in features:
            # update decision field with user's answer
            feature[1] = str(answer)
            # update attributes to store values of current x and y coordinates of the point WITHOUT moving it
            features.updateRow(feature)
            # create query to select the next row based on count field
            thisid = int(feature[0])
            expression = 'count = ' + str(thisid+1)
            exp2 = expression.replace("'", "")

# update curb field with text, without moving the point
def curbdecide(answer):
    mxd = arcpy.mapping.MapDocument("CURRENT")
    lyr = arcpy.mapping.ListLayers(mxd, pythonaddins.GetSelectedTOCLayerOrDataFrame())[0]
    # create cursor for selected point
    with arcpy.da.UpdateCursor(lyr, ["count", curbfield]) as features:
        for feature in features:
            # update decision field with user's answer
            feature[1] = str(answer)
            # update attributes to store values of current x and y coordinates of the point WITHOUT moving it
            features.updateRow(feature)
            # create query to select the next row based on count field
            thisid = int(feature[0])
            expression = 'count = ' + str(thisid+1)
            exp2 = expression.replace("'", "")

# update evaluattion field with text, without moving the point
def evaluate(answer):
    mxd = arcpy.mapping.MapDocument("CURRENT")
    lyr = arcpy.mapping.ListLayers(mxd, pythonaddins.GetSelectedTOCLayerOrDataFrame())[0]
    # create cursor for selected point
    with arcpy.da.UpdateCursor(lyr, ["count", evaluatefield]) as features:
        for feature in features:
            # update decision field with user's answer
            feature[1] = str(answer)
            # update attributes to store values of current x and y coordinates of the point WITHOUT moving it
            features.updateRow(feature)
            # create query to select the next row based on count field
            thisid = int(feature[0])
            expression = 'count = ' + str(thisid+1)
            exp2 = expression.replace("'", "")

# move selected point to a location based on the user's click
def movepoint(clickedx, clickedy):
    mxd = arcpy.mapping.MapDocument("CURRENT")
    lyr = arcpy.mapping.ListLayers(mxd, pythonaddins.GetSelectedTOCLayerOrDataFrame())[0]
    # create cursor for selected point
    with arcpy.da.UpdateCursor(lyr, [movecount, newx, newy, "SHAPE@X", "SHAPE@Y", decidefield]) as features:
        for feature in features:
            # update X and Y geometry fields (these are the LOCATION of the point, not written in the attribute table)
            # move point to the X,Y of the user's click
            feature[1] = clickedx
            feature[2] = clickedy
            feature[3] = clickedx
            feature[4] = clickedy
            feature[0] += 1
            feature[5] = "moved"
            features.updateRow(feature)
            # refresh map view to show new point
            arcpy.RefreshActiveView()

# pan map view to next point
def pantonext():
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
    lyr = arcpy.mapping.ListLayers(mxd, pythonaddins.GetSelectedTOCLayerOrDataFrame())[0]
    with arcpy.da.SearchCursor(lyr, ["count"]) as features:
        for feature in features:
            # create query and select the next row based on the "count" field
            nextid = int(feature[0]) + 1
            expression = 'count = ' + str(nextid)
            exp2 = expression.replace("'", "")
            arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", exp2)
            # move map view to centre on the next point at the same scale as is currently being used
            scalenow = df.scale
            df.extent = lyr.getSelectedExtent()
            df.scale = scalenow
            arcpy.RefreshActiveView()

# reset point location to original coordinates
def resetpoint():
    mxd = arcpy.mapping.MapDocument("CURRENT")
    lyr = arcpy.mapping.ListLayers(mxd, pythonaddins.GetSelectedTOCLayerOrDataFrame())[0]
    with arcpy.da.UpdateCursor(lyr, ["count", decidefield, newx, newy, "SHAPE@X", "SHAPE@Y", "longitude", "latitude", movecount]) as features:
        for feature in features:
            # set decision field and new x,y attribute fields to null
            feature[1] = None
            feature[2] = None
            feature[3] = None
            # set geometry attributes to X,Y coordinates based on attribute table
            feature[4] = feature[6]
            feature[5] = feature[7]
            # reset count of # of times feature has been moved to 0
            feature[8] = "0"
            features.updateRow(feature)
            # thisid = int(feature[0])
            # expression = 'count = ' + str(thisid)
            # exp2 = expression.replace("'", "")
            # arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", exp2)
    arcpy.RefreshActiveView()

class CURB(object):
    """Implementation for GRODTool_addin.button_8 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(5, "K", '', '')

class Canal(object):
    """Implementation for GRODTool_addin.button_5 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(1, "Canal", '', '')

class Duplicate(object):
    """Implementation for GRODTool_addin.button_4 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(1, "Duplicate", '', '')

class FMove(object):
    """Implementation for GRODTool_addin.button_7 (Button)"""
    def __init__(self):
        self.enabled = True
        self.shape = "NONE"
        self.cursor = 3
    def onMouseDownMap(self, x, y, button, shift):
        validateandrun(2, "moved", x, y)

class Fair(object):
    """Implementation for GRODTool_addin.button_10 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(6, "Fair", '', '')

class Full(object):
    """Implementation for GRODTool_addin.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(1, "Full", '', '')

class Multiple(object):
    """Implementation for GRODTool_addin.button_3 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(1, "Multiple", '', '')

class Next(object):
    """Implementation for GRODTool_addin.button_12 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(3, '', '', '')

class No(object):
    """Implementation for GRODTool_addin.button_2 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(1, "No", '', '')

class Partial(object):
    """Implementation for GRODTool_addin.button_1 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(1, "Partial", '', '')

class Poor(object):
    """Implementation for GRODTool_addin.button_11 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(6, "Poor", '', '')

class Reset(object):
    """Implementation for GRODTool_addin.button_13 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(4, '', '', '')

class Strong(object):
    """Implementation for GRODTool_addin.button_9 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(6, "Strong", '', '')

class Tributary(object):
    """Implementation for GRODTool_addin.button_6 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        validateandrun(1, "Tributary", '', '')