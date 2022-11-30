import openpyxl
import pandas as pd
import os
from openpyxl import load_workbook
import warnings
import math
import numpy as np
warnings.simplefilter(action='ignore', category=FutureWarning)

"""
TODO - add all these rules to the tabled data before we import them to filemaker for

SQ2 Rules:

DONE -  Collecting Event	CollectingBegin(Day/Month/Year) TO CollectingEnd(Day/Month/Year)	Need to be parsed Should go in the CollectingBeginDay/Month/Year fields but they are seperated fields and might have to parse this one out and to CollectingEndDay/Month/Year 

identifications	Identified(Day/Month/Year)	Should go in the IdentifiedDay/Month/Year fields but they are seperated fields and might have to parse this one out


MalPub	MalPub::Year	Have to determine which publication it connects to in MalPub
MalPub	Parent Title	Have to determine which publication it connects to in MalPub
MalPub + Citations	Volume + Pages	Have to sepearte field into two lookups

Identifications	Synonymy	String separated by a delimiter that needs to go in identifications table
Identifications	Previously Identified As	String separated by a delimiter that needs to go in identifications table


Master	dry_catalog_(day/month/year)	Date needs to be parsed
Master	alc_catalog_(day/month/year)	Date needs to be parsed


Provenance	DonorSource(NamedCollection)	Another Donor Source so will have to import it multiple times into provenance

Comments	219	Append the information to the Remarks information
Comments	220	Append the information to the Remarks information

"""

def fixSQData(df):
    #adding empty columns to dataframe
    df['CollectingBeginDay']=np.nan
    df['CollectingBeginMonth']=np.nan
    df['CollectingBeginYear']=np.nan
    df['CollectingEndDay']=np.nan
    df['CollectingEndMonth']=np.nan
    df['CollectingEndYear']=np.nan
    df['IdentifiedDay']=np.nan
    df['IdentifiedMonth']=np.nan
    df['IdentifiedYear']=np.nan
    df['Volume'] =np.nan
    df['VolumeNumber']=np.nan
    df['Series']=np.nan
    df['Pagination']=np.nan
    df['PreviousGenus']=np.nan
    df['PreviousSubGenus']=np.nan
    df['PreviousSpecies']=np.nan
    df['PreviousSubSpecies']=np.nan
    df['dry_catalog_day']=np.nan
    df['dry_catalog_month']=np.nan
    df['dry_catalog_year']=np.nan
    df['alc_catalog_day']=np.nan
    df['alc_catalog_month']=np.nan
    df['alc_catalog_year']=np.nan
    df = df.reset_index()
    for index, row in df.iterrows():

        if(checkIsGood(row['CollectingBegin(Day/Month/Year) TO CollectingEnd(Day/Month/Year)'])):
            collectDates = row['CollectingBegin(Day/Month/Year) TO CollectingEnd(Day/Month/Year)'].split("TO")
            if(len(collectDates)>=1):
                beginList=collectDates[0].split(" ")
                addColumnValue(df, index, "CollectingBeginDay", beginList[0])
                addColumnValue(df, index, "CollectingBeginMonth", beginList[1])
                addColumnValue(df, index, "CollectingBeginYear", beginList[2])
                if(len(collectDates)>1):
                    endList=collectDates[1].split(" ")
                    addColumnValue(df, index, "CollectingEndDay", endList[0])
                    addColumnValue(df, index, "CollectingEndMonth", endList[1])
                    addColumnValue(df, index, "CollectingEndYear", endList[2])
        
        if(checkIsGood(row['Identified(Day/Month/Year)'])):
            identDate = row['Identified(Day/Month/Year)'].split(" ")
            if(len(identDate)>=3):
                addColumnValue(df, index, 'IdentifiedDay', identDate[0])
                addColumnValue(df, index, 'IdentifiedMonth', identDate[1])
                addColumnValue(df, index, 'IdentifiedYear', identDate[2])

        #Parse volumes and pages into their own column

        #2(4) - two is volume and 4 is number
        #search for titles in malpub and change them in data right before import.
        #pagination
        if(checkIsGood(row['Volume + Pages'])):
            infoSplit=row['Volume + Pages'].split(":")
            if(len(infoSplit)>=1):
                if(len(infoSplit[0])>=4 and ("(" in infoSplit[0])):
                    volumeNumber=infoSplit[0].split("(")
                    row['Volume'] = volumeNumber[0]
                    row['VolumeNumber']=(volumeNumber[1].split(")"))[0]
                elif(infoSplit[0]=="NEWSERIES"):
                    row['Series']=infoSplit[0]
                elif(len(infoSplit[0])<4):
                    row['Volume']=infoSplit[0]
            if(len(infoSplit)>1):
                row['Pagination']=infoSplit[1]

        #word in the middle with parenthesis is the subgenus.
        #if not parenthesis then word in the middle is species and third word is subspecies.
        if(checkIsGood(row['Previously Identified As'])):
            prevIdent = row['Previously Identified As'].split(" ")
            row['PreviousGenus']=prevIdent[0]
            if(len(prevIdent)>2):
                if("(" in prevIdent[1]):
                    row['PreviousSubGenus']=prevIdent[1]
                    row['PreviousSpecies']=prevIdent[2]
                else:
                    row['PreviousSpecies']=prevIdent[1]
                    row['PreviousSubSpecies']=prevIdent[2]
            else:
                row['PreviousSpecies']=prevIdent[1]
            
        if(checkIsGood(row['dry_catalog_(day/month/year)'])):
            drySplit = row['dry_catalog_(day/month/year)'].split(" ")
            row['dry_catalog_day']=drySplit[0]
            row['dry_catalog_month']=drySplit[1]
            row['dry_catalog_year']=drySplit[2]
        
        if(checkIsGood(row['alc_catalog_(day/month/year)'])):
            drySplit = row['alc_catalog_(day/month/year)'].split(" ")
            row['alc_catalog_day']=drySplit[0]
            row['alc_catalog_month']=drySplit[1]
            row['alc_catalog_year']=drySplit[2]

        if(checkIsGood(row['219'])):
            row['Remarks']=row['Remarks']+" "+row['219']
        
        if(checkIsGood(row['220'])):
            row['Remarks']=row['Remarks']+" "+row['220']
    return df

def checkIsGood(info):
    return type(info)==type(str())
    # if(type(info)!=type(str())):
    #     return not math.isnan(info)
    # return True

def addColumnValue(dFrame, index, column, value):
    dFrame.loc[index, column]=value