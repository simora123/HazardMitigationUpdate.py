import json, os, uuid, collections, arcpy, shutil
# Downloaded Module. Will need to be referenced in the python.2.7 folder on your server in order for script to run property
from PyPDF2 import PdfFileMerger

arcpy.env.overwriteOutput = True

# Output to the scratch workspace
scratch = arcpy.env.scratchFolder
arcpy.AddMessage("  Scratch WS " + str(scratch))

# MXD variables for Hazard Data Driven Pages
#mxd = arcpy.mapping.MapDocument(arcpy.GetParameterAsText(0))
mxd = arcpy.mapping.MapDocument(r"C:\Web_Print\A4 Landscape2.mxd")
df = arcpy.mapping.ListDataFrames(mxd)[0]

# MXD variables for individual hazards
#mxd = arcpy.mapping.MapDocument(arcpy.GetParameterAsText(0))
mxd2 = arcpy.mapping.MapDocument(r"C:\Web_Print\A4 Landscape_Hazards.mxd")
df2 = arcpy.mapping.ListDataFrames(mxd2)[0]

# Search Variable
NameList = arcpy.GetParameterAsText(0)
#NameList = "0920402002100"

# Name of PDF Variable
output_name = str(NameList) + '.pdf'
# ScratchFolder Variables
PDF_File = os.path.join(arcpy.env.scratchFolder + '\\' + output_name)
OutputFile = os.path.join(arcpy.env.scratchFolder + '\\' + "Appended_" + output_name)

# Attached PDF Variables
flood_pdf = r"C:\Web_Print\Report\Intl_BestPractices_EU_2004.pdf"
inundation_pdf = r"C:\Web_Print\Report\fema_p_956_living_with_dams.pdf"
landslide_pdf = r"C:\Web_Print\Report\dcnr_014592.pdf"
radon_pdf = r"C:\Web_Print\Report\Citizens_Guide_to_Radon.pdf"

# PDF List
pdfs = []

# Field Names associated with lyr.name "Parcel Select" in mxd variable
fieldNames = ["PIDN", "PROPADR", "OWNER_FULL", "LUC", "FLOOD", "INUNDATION", "LANDSLIDE", "RADON", "ENIV_HAZARD", "LEVEE", "SINKHOLE", "NUCLEAR", "EARTHQUAKE", "DROUGHT", "WILDFIRE", "URBANFIRE"]

# Loops thru all layer in the mxd variable table of contents
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name == "Parcel Select":
        # Changes the Definition Query in Parcel Select in the TOC
        lyr.definitionQuery = "PIDN = '"+NameList+"'"
        # Starts Data Driven Pages Processes - Refresh
        mxd.dataDrivenPages.refresh()
        ddp = mxd.dataDrivenPages
        indexLayer = ddp.indexLayer
        arcpy.SelectLayerByAttribute_management(indexLayer, "NEW_SELECTION", "PIDN = '"+NameList+"'")

        # Loops thru selected Data Driven Pages in mxd variable
        for indexPage in ddp.selectedPages:
            ddp.currentPageID = indexPage
            # Exports to PDF
            ddp.exportToPDF(PDF_File, "CURRENT")

        # Appends to PDF List
        pdfs.append(PDF_File)

# Loops thru all layer in the mxd2 variable table of contents
for lyr in arcpy.mapping.ListLayers(mxd2):
    if lyr.name == "Parcel Select":
        # Changes the Definition Query in Parcel Select in the TOC
        lyr.definitionQuery = "PIDN = '"+NameList+"'"
        # Sets Extent to Parcel Select in TOC
        ext = lyr.getExtent()
        df2.extent = ext

        # Search Cursor on Parcel Select
        with arcpy.da.SearchCursor(lyr, fieldNames) as cursor:
            # Loops thru Parcel Select and associated Field Names
            for row in cursor:
                arcpy.AddMessage(u'{0}, {1}, {2}, {3}, {4}, {5}, {6}'.format(row[0], row[4], row[5], row[6], row[7], row[8], row[9]))
                # if condition for Flood Field
                if row[4] != 'Not in any FEMA FLOOD ZONES':
                    # Flood Field Variables
                    FloodFile = os.path.join(arcpy.env.scratchFolder + '\\' + "Flood_" + output_name)
                    flood_layer = arcpy.mapping.ListLayers(mxd2, "Floodplains", df2)[0]
                    FloodMap_File = os.path.join(arcpy.env.scratchFolder + '\\' + "FloodMap" + output_name)
                    # Changes Flood Layer in TOC to visible
                    flood_layer.visible = True
                    # Refreshes TOC
                    arcpy.RefreshTOC()
                    arcpy.RefreshActiveView()
                    # Loops thru Layout Text Elements
                    for elm in arcpy.mapping.ListLayoutElements(mxd2, "TEXT_ELEMENT"):
                        # Looks for text called "Input Hazard" in mxd2 layout
                        if elm.text == "Input Hazard":
                            print "Yes"
                            # Renames text
                            elm.text = 'Floodplain'
                    # Exports MXD2 to PDF
                    arcpy.mapping.ExportToPDF(mxd2,FloodMap_File)
                    # Appends Output PDF to PDF List
                    pdfs.append(FloodMap_File)
                    # Copies and Appends Flood PDF to PDF List
                    shutil.copy2(flood_pdf, FloodFile)
                    pdfs.append(FloodFile)
                    flood_layer.visible = False
                    # Refreshes TOC
                    arcpy.RefreshTOC()
                    arcpy.RefreshActiveView()
                    for elm in arcpy.mapping.ListLayoutElements(mxd2, "TEXT_ELEMENT"):
                        # Looks for text called "Input Hazard" in mxd2 layout
                        if elm.text == "Floodplain":
                            print "Yes"
                            # Renames text
                            elm.text = 'Input Hazard'

                # if condition for Inundation Field
                if row[5] != 'Not in Inundation Area':
                    # Inundation Field Variables
                    InundationFile = os.path.join(arcpy.env.scratchFolder + '\\' + "Inundation_" + output_name)
                    inundation_layer = arcpy.mapping.ListLayers(mxd2, "Inundation Area", df2)[0]
                    InundationMap_File = os.path.join(arcpy.env.scratchFolder + '\\' + "Inundation" + output_name)
                    # Changes Inundation Layer in TOC to visible
                    inundation_layer.visible = True
                    # Refreshes TOC
                    arcpy.RefreshTOC()
                    arcpy.RefreshActiveView()
                    # Loops thru Layout Text Elements
                    for elm in arcpy.mapping.ListLayoutElements(mxd2, "TEXT_ELEMENT"):
                        # Looks for text called "Input Hazard" in mxd2 layout
                        if elm.text == "Input Hazard":
                            print "Yes"
                            # Renames text
                            elm.text = 'Inundation'
                    # Exports MXD2 to PDF
                    arcpy.mapping.ExportToPDF(mxd2,InundationMap_File)
                    # Appends Output PDF to PDF List
                    pdfs.append(InundationMap_File)
                    # Copies and Appends Inundation PDF to PDF List
                    shutil.copy2(inundation_pdf, InundationFile)
                    pdfs.append(InundationFile)

                # if condition for Landslide Field
                if row[6] != 'Not in Landslide Area':
                    # Landslide Field Variables
                    LandslideFile = os.path.join(arcpy.env.scratchFolder + '\\' + "Landslide_" + output_name)
                    # Copies and Appends Landslide PDF to PDF List
                    shutil.copy2(landslide_pdf, LandslideFile)
                    pdfs.append(LandslideFile)

##r_pdfs = list(reversed(pdfs))

arcpy.AddMessage(pdfs)

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
    merger = PdfFileMerger()

    # Loops thru PDF List
    for pdf in pdfs:
        # Merges all pdfs in PDF List
        merger.append(pdf)
    # Writes all PDFs from PDF List into one PDF
    merger.write(OutputFile)

del mxd, mxd2

# Script Parameter. Pushes to Geoprocessing Service Folders
arcpy.SetParameterAsText(1, OutputFile)

arcpy.AddMessage("  Process Complete")