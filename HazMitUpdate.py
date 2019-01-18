# Import system modules
import arcpy, os, sys, time, datetime, traceback, string, shutil, glob

# Time stamp variables
currentTime = datetime.datetime.now()
# Date formatted as month-day-year (1-1-2017)
dateToday = currentTime.strftime("%m-%d-%Y")

# Create text file for logging results of script
file = r'\\YCPCFS\GIS_Projects\IS\Scripts\Python\Logs\HazardMitigation_Update_{}.txt'.format(dateToday)
# Open text file in write mode and log results of script
report = open(file,'w')

# Define functions
# If an error occurred, write line number and error message to log
def ErrorMessageEnvironment(e):
    tb = sys.exc_info()[2]
    report.write("\nFailed at Line %i \n" % tb.tb_lineno)
    report.write('Error: {}\n'.format(str(e)))

# If an error occurred, write line number and error message to log
def ErrorMessageException(e):
    tb = sys.exc_info()[2]
    report.write("\nFailed at Line %i \n" % tb.tb_lineno)
    report.write('Error: {} \n'.format(e.message))

# Write messages to a log file
def message(report,message):
    """ Write a message to a text file
        report is the text file to write the messages to
        report should be defined as report = open(path to file, mode)
         message is the string to write to the file
    """
    timeStamp = time.strftime("%b %d %Y %H:%M:%S")
    report.write("{} {} \n \n".format(timeStamp,message))
    print "{}: ".format(timeStamp) + message
# End functions

# Variable used to determine time that script started
ScriptStartTime = datetime.datetime.now()

arcpy.env.overwriteOutput = True

# Hazitmit Workspaces
arcpy.env.workspace = r"\\YCPCFS\GIS_Projects\Long_Range\hazard_mitigation\web_application\Test_Data\Production.gdb"
Test_gdb =r"\\YCPCFS\GIS_Projects\Long_Range\hazard_mitigation\web_application\Test_Data\Hazmit_Data.gdb"
Base_DataGDB = r"\\YCPCFS\GIS_Projects\Long_Range\hazard_mitigation\web_application\Test_Data\Base_Data.gdb"

# Edit Hazmit Data
Hazmit_Data = os.path.join(arcpy.env.workspace, 'HazMit_Parcels')

# Variables coming from York SDE
YorkParcel = r"\\YCPCFS\GIS_Projects\IS\GIS_Connections\GIS@York.sde\York.GIS.Land_Base\York.GIS.Parcels"
York_Floodplain = r"\\YCPCFS\GIS_Projects\IS\GIS_Connections\GIS@York.sde\\York.GIS.HYDRO_Floodplains"

# Variables coming from York Projects SDE
York_Projects_HazMit_Parcel = r"\\YCPCFS\GIS_Projects\IS\GIS_Connections\GIS@York_Projects.sde\York_Projects.GIS.HazMit_Parcels_WebViewer_Data"

# Base_Data.gdb variables
York_DamInundation = os.path.join(Base_DataGDB,"inundation_area")
York_Landslide = os.path.join(Base_DataGDB,"Landslide_Final")
York_Radon = os.path.join(Base_DataGDB,"Radon_Zipcodes_w_R_AVG")
York_Eniv_Hazard = os.path.join(Base_DataGDB,"SARA_HazardRt_Pipeline")
York_Levee = os.path.join(Base_DataGDB,"YorkCounty_LeveeData")
York_Sinkhole = os.path.join(Base_DataGDB,"Karst_Topography")
York_Nuclear = os.path.join(Base_DataGDB,"NuclearIncident_10mile_Buffer")
York_Earthquake = os.path.join(Base_DataGDB,"Earthquake")
York_Drought = os.path.join(Base_DataGDB,"stressed_area")
York_Wild_Fire = os.path.join(Base_DataGDB,"WildfireArea_Finished")
York_Urban_Fire = os.path.join(Base_DataGDB,"UrbanFire_TotalArea_Dsslv2")

try:
    message (report,"""
#------------------------------------------------------------------------------------------------------#
# Name:        HazardMitigation_Update.py (Updates HazMit_Parcels_WebViewer_Data GIS Layer             #
#               on York Projects SDE)                                                                  #
#                                                                                                      #
# Purpose:     Script Updates the Hazmit_Parcels_WebViewer_Data on the York Projects SDE.              #
#                Script does as follows:                                                               #
#                   1- Deletes and Creates New HazMit_Parcel Edit Data                                 #
#                   2- Adds Fields to HazMit_Parcel Edit                                               #
#                   3- Creates temporary Union, Sort and Dissolve Layer                                #
#                   4- Joins Finished HazMit_Parcel Dissolve to HazMit_Parcels Edit GIS Layer          #
#                   5- Calculates and Updates Hazard Fields in HazMit_Parcel Edit Layer                #
#                   6- Deletes Features in Hazmit_Parcels_WebViewer_Data and Appends New Features      #
#                                                                                                      #
# Authors:     Joseph Simora - York County Planning (YCPC)                                             #
# Credits:                                                                                             #
# Created:     January 10 2019                                                                         #
# Revised:                                                                                             #
# Copyright:   (c) York County Planning Commission                                                     #
#------------------------------------------------------------------------------------------------------#
""")

    message (report,"Deleting Feature Class {}".format("HazMit_Parcels"))
    arcpy.Delete_management(Hazmit_Data)

    message (report,"Creating Feature Class {}".format("HazMit_Parcels"))
    arcpy.CreateFeatureclass_management(arcpy.env.workspace, 'HazMit_Parcels', "POLYGON")

    fieldNames = ["PIDN", "PROPADR", "OWNER_FULL", "LUC", "FLOOD", "INUNDATION", "LANDSLIDE", "RADON", "ENIV_HAZARD", "LEVEE", "SINKHOLE", "NUCLEAR", "EARTHQUAKE", "DROUGHT", "WILDFIRE", "URBANFIRE"]

    for f in fieldNames:
        message (report,"Adding Field {} to {}".format(f, Hazmit_Data))
        if f != "OWNER_FULL":
            arcpy.AddField_management(Hazmit_Data, f, "TEXT", "", "", 50, f, "NULLABLE", "")
        else:
            arcpy.AddField_management(Hazmit_Data, f, "TEXT", "", "", 255, f, "NULLABLE", "")

    del f

    message (report,"Appending {} Data from York_Edit to HazMit_Parcel_Edit".format(fieldNames[0:3]))
    arcpy.Append_management(YorkParcel, Hazmit_Data, "NO_TEST",\
        "Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#;\
        Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#;\
        PIDN \"PIDN\" true true false 50 Text 0 0 ,First,#,"+YorkParcel+",PIDN,-1,-1;\
        PROPADR \"PROPADR\" true true false 50 Text 0 0 ,First,#,"+YorkParcel+",PROPADR,-1,-1;\
        OWNER_FULL \"OWNER_FULL\" true true false 255 Text 0 0 ,First,#,"+YorkParcel+",OWNER_FULL,-1,-1;\
        LUC \"LUC\" true true false 50 Text 0 0 ,First,#,"+YorkParcel+",LUC,-1,-1;\
        FLOOD \"FLOOD\" true true false 50 Text 0 0 ,First,#;\
        INUNDATION \"INUNDATION\" true true false 50 Text 0 0 ,First,#;\
        LANDSLIDE \"LANDSLIDE\" true true false 50 Text 0 0 ,First,#;\
        RADON \"RADON\" true true false 50 Text 0 0 ,First,#","")

    print " \n"
    Input_Features = [York_Floodplain,\
     York_DamInundation,\
     York_Landslide,\
     York_Radon,\
     York_Eniv_Hazard,\
     York_Levee,\
     York_Sinkhole,\
     York_Nuclear,\
     York_Earthquake,\
     York_Drought,\
     York_Wild_Fire,\
     York_Urban_Fire]
##    Input_Features = [York_Drought, York_Wild_Fire, York_Urban_Fire]

    try:
        for i in Input_Features:
            if i == York_Floodplain:
                Haz_Union = "Parcels_" + i.split(".")[-1] + "_Union"
                message (report,"Start Union with {} and {}".format(YorkParcel.split("\\")[-1],i.split(".")[-1]))
                arcpy.Union_analysis (""+YorkParcel+"; "+i+"", os.path.join(Test_gdb, Haz_Union), "ALL", "")
                message (report,"Union Complete")
            else:
                Haz_Union = "Parcels_" + i.split("\\")[-1] + "_Union"
                message (report,"Start Union with {} and {}".format(YorkParcel.split("\\")[-1],i.split("\\")[-1]))
                arcpy.Union_analysis (""+YorkParcel+"; "+i+"", os.path.join(Test_gdb, Haz_Union), "ALL", "")
                message (report,"Union Complete")

            # Make a layer from the feature class
            arcpy.MakeFeatureLayer_management(os.path.join(Test_gdb, Haz_Union), "Selected_Layer")

            sort_fields = ["PIDN", "FLD_ZONE", "ZONE_SUBTY", "NAME", "R_AVG", "Envir_Hazard", "Feature_Name", "Karst_Feature", "NAME", "Hzrd_Zone", "TYPE_AREA", "Widfire_Type", "Urban_Type"]

            if i == York_Floodplain:
                #Haz_Select = "Parcels_" + i.split(".")[-1] + "_Select"
                ii = i.split(".")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split(".")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split(".")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[1], "ASCENDING"],[sort_fields[2], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split(".")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split(".")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split(".")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[1])+" FIRST;"+str(sort_fields[2])+" FIRST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_DamInundation:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[3], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[3])+" FIRST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Landslide:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", "", "MULTI_PART", "DISSOLVE_LINES")

                if len(arcpy.ListFields(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"),"TYPE"))>0:
                    message (report,"Field Exist")
                else:
                    message (report,"Field Doesn't Exist")
                    arcpy.AddField_management (os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), "TYPE", "TEXT", "", "", 100, "TYPE", "NULLABLE", "")
                    arcpy.CalculateField_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), "TYPE", "\"Parcel is susceptible to landslide\"", "PYTHON")

            if i == York_Radon:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[4], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[4])+" LAST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Eniv_Hazard:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[5], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[5])+" LAST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Levee:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[6], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[6])+" LAST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Sinkhole:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[7], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[7])+" LAST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Nuclear:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[8], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[8])+" LAST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Earthquake:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[9], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[9])+" LAST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Drought:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[10], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[10])+" LAST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Wild_Fire:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[11], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[11])+" LAST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Urban_Fire:
                #Haz_Select = "Parcels_" + i.split("\\")[-1] + "_Select"
                ii = i.split("\\")[-1]
                where = "NOT FID_"+str(ii)+" = -1 AND NOT PIDN = '' "

                arcpy.SelectLayerByAttribute_management ("Selected_Layer", "NEW_SELECTION", where)
                #arcpy.Select_analysis("Selected_Layer", os.path.join(Test_gdb, Haz_Select), "")
                message (report,"Start Sort Step for {}".format(i.split("\\")[-1]))
                arcpy.Sort_management("Selected_Layer", os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), [[sort_fields[0], "ASCENDING"],[sort_fields[12], "ASCENDING"]], "UR")
                message (report,"Start Dissolve Step for {}".format(i.split("\\")[-1]))
                arcpy.Dissolve_management(os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort"), os.path.join(Test_gdb, "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"), ""+str(sort_fields[0])+"", ""+str(sort_fields[12])+" LAST", "MULTI_PART", "DISSOLVE_LINES")

            if i == York_Floodplain:

                Sort_Dissolve = "Parcels_" + i.split(".")[-1] + "_Sort_Disso"

                # Make a layer from the feature class
                arcpy.MakeFeatureLayer_management(os.path.join(Test_gdb, Sort_Dissolve), Sort_Dissolve)

                # Make a layer from the feature class
                arcpy.MakeFeatureLayer_management(os.path.join(arcpy.env.workspace, "HazMit_Parcels"), "HazMit_Parcels_Layer")

                message (report,"Joining {} and {}".format("HazMit_Parcels_Layer", Sort_Dissolve))
                arcpy.AddJoin_management( "HazMit_Parcels_Layer", ""+str(sort_fields[0])+"", Sort_Dissolve, ""+str(sort_fields[0])+"")

                message (report,"Calculating")
                arcpy.CalculateField_management("HazMit_Parcels_Layer", "FLOOD", "!Parcels_HYDRO_Floodplains_Sort_Disso.FIRST_FLD_ZONE! + \" - \" + !Parcels_HYDRO_Floodplains_Sort_Disso.FIRST_ZONE_SUBTY!", "PYTHON", "")
                arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.FLOOD\" IS NULL")
                arcpy.CalculateField_management("HazMit_Parcels_Layer", "FLOOD", "\"Not in any FEMA FLOOD ZONES\"", "PYTHON", "")

                arcpy.RemoveJoin_management ("HazMit_Parcels_Layer")

            else:
                Sort_Dissolve = "Parcels_" + i.split("\\")[-1] + "_Sort_Disso"

                # Make a layer from the feature class
                arcpy.MakeFeatureLayer_management(os.path.join(Test_gdb, Sort_Dissolve), Sort_Dissolve)

                # Make a layer from the feature class
                arcpy.MakeFeatureLayer_management(os.path.join(arcpy.env.workspace, "HazMit_Parcels"), "HazMit_Parcels_Layer")

                message (report,"Joining {} and {}".format("HazMit_Parcels_Layer", Sort_Dissolve))
                arcpy.AddJoin_management( "HazMit_Parcels_Layer", ""+str(sort_fields[0])+"", Sort_Dissolve, ""+str(sort_fields[0])+"")

                if i == York_DamInundation:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "INUNDATION", "\"Yes - \" +  !"+Sort_Dissolve+".FIRST_NAME! ", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.INUNDATION\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "INUNDATION", "\"Not in Inundation Area\"", "PYTHON", "")

                if i == York_Landslide:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "LANDSLIDE", "!"+Sort_Dissolve+".TYPE!", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.LANDSLIDE\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "LANDSLIDE", "\"Not in Landslide Area\"", "PYTHON", "")

                if i == York_Radon:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "RADON", "!"+Sort_Dissolve+".LAST_R_AVG!", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.RADON\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "RADON", "\"N/A\"", "PYTHON", "")

                if i == York_Eniv_Hazard:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "ENIV_HAZARD", "!"+Sort_Dissolve+".LAST_Envir_Hazard!", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.ENIV_HAZARD\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "ENIV_HAZARD", "\"Not in Environmental Hazard Area\"", "PYTHON", "")
                    ####### +  !"+Sort_Dissolve+".LAST_FID_SARA_HazardRt_Pipeline!

                if i == York_Levee:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "LEVEE", "\"Yes - \" +  !"+Sort_Dissolve+".LAST_Feature_Name! ", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.LEVEE\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "LEVEE", "\"Not in Levee Risk Area\"", "PYTHON", "")

                if i == York_Sinkhole:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "SINKHOLE", "!"+Sort_Dissolve+".LAST_Karst_Feature!", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.SINKHOLE\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "SINKHOLE", "\"Not in Sinkhole Risk Area\"", "PYTHON", "")
                    ######## +  !str("+Sort_Dissolve+".LAST_Karst_Feature)!

                if i == York_Nuclear:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "NUCLEAR", "!"+Sort_Dissolve+".LAST_NAME! ", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.NUCLEAR\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "NUCLEAR", "\"Not in a 10 Mile Radius\"", "PYTHON", "")

                if i == York_Earthquake:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "EARTHQUAKE", "\"Yes - \" +  !"+Sort_Dissolve+".LAST_Hzrd_Zone! ", "PYTHON", "")

                if i == York_Drought:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "DROUGHT", "\"Yes - \" +  !"+Sort_Dissolve+".LAST_TYPE_AREA! ", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.DROUGHT\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "DROUGHT", "\"Not Water Challenged\"", "PYTHON", "")

                if i == York_Wild_Fire:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "WILDFIRE", "!"+Sort_Dissolve+".LAST_Widfire_Type!", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.WILDFIRE\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "WILDFIRE", "\"Not in Wildfire Zone\"", "PYTHON", "")
                    ##### +  !"+Sort_Dissolve+".FID_Widfire_Type!

                if i == York_Urban_Fire:
                    message (report,"Calculating")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "URBANFIRE", "!"+Sort_Dissolve+".LAST_Urban_Type!", "PYTHON", "")
                    arcpy.SelectLayerByAttribute_management ("HazMit_Parcels_Layer", "NEW_SELECTION", "\"HazMit_Parcels.URBANFIRE\" IS NULL")
                    arcpy.CalculateField_management("HazMit_Parcels_Layer", "URBANFIRE", "\"Not in Urban Fire Zone\"", "PYTHON", "")
                    ######  +  !"+Sort_Dissolve+".FID_Urban_Type!

                arcpy.RemoveJoin_management ("HazMit_Parcels_Layer")

        del i

        # Process: Delete Features
        message (report,"Deleting Old Hazmit Information")
        arcpy.DeleteFeatures_management(York_Projects_HazMit_Parcel)

        # Process: Append
        message (report,"Appending new hazmit information into York Projects")
        arcpy.Append_management(Hazmit_Data, York_Projects_HazMit_Parcel, "NO_TEST","\
        PIDN \"PIDN\" true true false 13 Text 0 0 ,First,#,"+Hazmit_Data+",PIDN,-1,-1;\
        PROPADR \"PROPADR\" true true false 8 Text 0 0 ,First,#,"+Hazmit_Data+",PROPADR,-1,-1;\
        OWNER_FULL \"OWNER_FULL\" true true false 8 Text 0 0 ,First,#,"+Hazmit_Data+",OWNER_FULL,-1,-1;\
        LUC \"LUC\" true true false 54 Text 0 0 ,First,#,"+Hazmit_Data+",LUC,-1,-1;\
        FLOOD \"FLOOD\" true true false 81 Text 0 0 ,First,#,"+Hazmit_Data+",FLOOD,-1,-1;\
        INUNDATION \"INUNDATION\" true true false 40 Text 0 0 ,First,#,"+Hazmit_Data+",INUNDATION,-1,-1;\
        LANDSLIDE \"LANDSLIDE\" true true false 40 Text 0 0 ,First,#,"+Hazmit_Data+",LANDSLIDE,-1,-1;\
        RADON \"RADON\" true true false 124 Text 0 0 ,First,#,"+Hazmit_Data+",RADON,-1,-1;\
        ENIV_HAZARD \"ENIV_HAZARD\" true true false 40 Text 0 0 ,First,#,"+Hazmit_Data+",ENIV_HAZARD,-1,-1;\
        LEVEE \"LEVEE\" true true false 40 Text 0 0 ,First,#,"+Hazmit_Data+",LEVEE,-1,-1;\
        SINKHOLE \"SINKHOLE\" true true false 40 Text 0 0 ,First,#,"+Hazmit_Data+",SINKHOLE,-1,-1;\
        NUCLEAR \"NUCLEAR\" true true false 40 Text 0 0 ,First,#,"+Hazmit_Data+",NUCLEAR,-1,-1;\
        EARTHQUAKE \"EARTHQUAKE\" true true false 1 Text 0 0 ,First,#,"+Hazmit_Data+",EARTHQUAKE,-1,-1;\
        DROUGHT \"DROUGHT\" true true false 4 Text 0 0 ,First,#,"+Hazmit_Data+",DROUGHT,-1,-1;\
        WILDFIRE \"WILDFIRE\" true true false 8 Double 8 38 ,First,#,"+Hazmit_Data+",WILDFIRE,-1,-1;\
        URBANFIRE \"URBANFIRE\" true true false 2 Text 0 0 ,First,#,"+Hazmit_Data+",URBANFIRE,-1,-1;\
        Shape \"Shape\" false false true 0 Double 0 0 ,First,#;\
        Shape.STArea() \"Shape.STArea()\" false false true 0 Double 0 0 ,First,#;\
        Shape.STLength() \"Shape.STLength()\" false false true 0 Double 0 0 ,First,#", "")

    # Section for error messaging
    except EnvironmentError as e:
        ErrorMessageEnvironment(e)
    except Exception as e:
        ErrorMessageException(e)

    message (report, "End\n")

# Section for error messaging
except EnvironmentError as e:
    ErrorMessageEnvironment(e)
except Exception as e:
    ErrorMessageException(e)

finally:
    try:
        message (report, "HazardMitigation_Update.py script is Completed\n")
        # Script Completion DateTime for Elapsed Time Calculation
        ScriptEndTime = datetime.datetime.now()
        # Total Script Elapsed Time Calculation
        ScriptElapsedTime = ScriptEndTime - ScriptStartTime
        # Prints out Total Time of Script
        message (report, "Total Elapsed Time:  - " + str(ScriptElapsedTime) + "\n")
        # del mxd
        message (report, "Done!")
        report.close()
    # Section for error messaging
    except EnvironmentError as e:
        ErrorMessageEnvironment(e)
    except Exception as e:
        ErrorMessageException(e)
