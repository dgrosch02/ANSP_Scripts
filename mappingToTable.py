import openpyxl
import pandas as pd
import os
from openpyxl import load_workbook
import warnings
import dataToFilemaker
warnings.simplefilter(action='ignore', category=FutureWarning)


#Might want to connect this to file on ANSP //files.drexel.edu path
#Path: smb://files.drexel.edu/ANS/CSBE_Data/malac/SHARED/Grants/Digitizing Invertebrates DigIn 2020/Integrate_For_GI_Database
#dtype=str makes sure all inputs are read in as a string. This is important for Numbers of fields so their not brought in as int.
key_df = pd.read_excel('./FieldMappings.xlsx', sheet_name='SQ2Key', dtype = str)
keyLookup={}

#These are the ids we should pass and not import. Manually put in right now
#TODO - make excel sheet with the ids we should not grab and pass that information to this list.
dontImport=['005', '023', '027', '028', '165', '170', '174', '024', '141', '025', '026', '180']

def getKeys():
    numberList=key_df['Number']
    wordList=key_df['Map to GI Field']
    isImport=key_df['In Tables']
    # wordList=key_df['Map to GI Field']
    if(len(wordList)==len(numberList) and len(numberList)==len(isImport)):
        x=0
        for i in numberList:
            if(isImport[x]=="Y"):
                keyLookup[i]=wordList[x]
            x+=1
    else:
        print("Make sure all cells are filled out in table")
    
    #When doing the key lookup make sure there is no problem with 
    for i in range(0, len(wordList)):
        for x in range(i+1, len(wordList)):
            if(wordList[i]==wordList[x] and wordList[i]!="Don't Import"):
                print("DUPLICATE IN KEY LOOKUP, PLEASE FIX: "+wordList[i])

def readData():

    #initialize some variables
    dataDict={}
    file_df = pd.DataFrame({}, columns=keyLookup.values());

    #this defines the current row that will be updates
    #will be cleared once we hit 001 (meaning id which is a new record in the sq2 file)
    currentRow={}
    allList=[]
    sq2Files="./sq2Files"
    dirList = os.listdir(sq2Files)

    writer = pd.ExcelWriter('sq2Output.xlsx', engine='openpyxl')
    # writer.book = book

    for fileName in dirList:
        f = open("./sq2Files/"+fileName, "r")

        first=True
        # file_df.reset_index(drop=True, inplace=True)

        for x in f:
            
            #setup dictionary
            lineInfo=x.split(" ", 1)
            fieldID=str(lineInfo[0][9:12])
            if(not(fieldID in dontImport)):
                if(fieldID=="001"):
                    if(not first):
                        file_df = pd.concat([file_df, pd.DataFrame(currentRow, index=[0])])
                        currentRow={}
                    else:
                        first=False
                if(fieldID in keyLookup.keys()):
                    getFieldName=keyLookup[fieldID]
                else:
                    getFieldName=fieldID
                #if the key already exists have to append the information

                #TODO - Append information for 01, 02, etc.
                if(getFieldName in currentRow.keys()):
                    currentRow[getFieldName]=currentRow[getFieldName]+lineInfo[1]
                else:
                    currentRow[getFieldName]=lineInfo[1]

        f.close()
    # file_df.apply(dataToFilemaker.fixSQData, axis=1)
    finalDataFrame = dataToFilemaker.fixSQData(file_df)
    finalDataFrame.to_excel(writer,sheet_name="CollectedData")
    writer.close()

if __name__=="__main__":
    getKeys()
    readData()