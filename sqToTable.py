import pandas as pd

#Might want to connect this to file on ANSP //files.drexel.edu path
#Path: smb://files.drexel.edu/ANS/CSBE_Data/malac/SHARED/Grants/Digitizing Invertebrates DigIn 2020/Integrate_For_GI_Database
key_df = pd.read_excel('./Data_from_Card_Files.xlsx', sheet_name='SQ2Key')
keyLookup={}
wordList=[]

def getKeys():
    numberList=key_df['Number']
    wordList=key_df['SheetName']
    if(len(wordList)==len(numberList)):
        x=0
        for i in numberList:
            keyLookup[i]=wordList[x]
            x+=1
    return wordList

def readData(wordList):

    #initialize some variables
    dataDict={}
    file_df = pd.DataFrame(columns=wordList);

    #this defines the current row that will be updates
    #will be cleared once we hit 001 (meaning id which is a new record in the sq2 file)
    currentRow={}

    #open the file
    f = open("./sq2Files/CNUS19.SQ2", "r")
    # bool first=True
    for x in f:
        #setup dictionary
        lineInfo=x.split(" ")
        #id example: 00069391400101
        fieldId=lineInfo[0][9:12]
        getFieldName=keyLookup[fieldId]
        #if the key already exists have to append the information
        currentRow[getFieldName]=lineInfo[1]
        #dataDict[lineInfo[0]]=lineInfo[1]
        # while((not first) and fieldID)
        file_df = file_df.append(currentRow, ignore_index = True)
    f.close()

wordList = getKeys()
readData(wordList)