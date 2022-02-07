import pandas as pd
import numpy as np
from datetime import datetime

def read_data(file_name, skiprows = 0, index_col = False):
    df = pd.read_csv(file_name, skiprows = skiprows,error_bad_lines=False,index_col = index_col)
    df = df[['bbr_x','bbr_y','fbr_x','fbr_y','fbl_x','fbl_y','bbl_x','bbl_y',
             'Frame #','Timestamp','ID','direction','speed', 'width']]
    
    rightToLeftDF = df.loc[df['direction'] == -1]
    rightToLeftDF.columns = ['tr_x','tr_y','tl_x','tl_y','bl_x','bl_y','br_x','br_y',
                             'Frame #','Timestamp','ID','direction','speed', 'width']
    leftToRightDF = df.loc[df['direction'] == 1]
    leftToRightDF.columns = ['bl_x','bl_y','br_x','br_y','tr_x','tr_y','tl_x','tl_y',
                             'Frame #','Timestamp','ID','direction','speed','width']
    leftToRightDF = leftToRightDF[['tr_x','tr_y','tl_x','tl_y','bl_x','bl_y','br_x','br_y',
                                   'Frame #','Timestamp','ID','direction','speed','width']]
    
    df = pd.concat([rightToLeftDF, leftToRightDF])
    
    return df

def getOneCar(df, carID) :
    newdf = df.loc[df['ID'] == carID]
    return newdf

def runTests(oneID, oneCarDF) :
    errorDF = pd.DataFrame(columns=['Car ID','Error Message', 'Time'])
    errorDF = pd.concat([errorDF, withinLaneTest(oneID, oneCarDF)], ignore_index=True)
    errorDF = pd.concat([errorDF, widthTest(oneID, oneCarDF)], ignore_index=True)
    errorDF = pd.concat([errorDF, speedTest(oneID, oneCarDF)], ignore_index=True)
    
    errorDF.drop_duplicates(subset=['Car ID', 'Error Message'], keep='first', inplace=True)
    return errorDF

def withinLaneTest(oneID, oneCarDF) :
    errorDF = pd.DataFrame(columns=['Car ID','Error Message', 'Time'])
    tbCoord = np.array(oneCarDF[['tl_y','bl_y', 'Timestamp']])
    
    for i in range(len(tbCoord)) :
        for j in range(2) :
            tbCoord[i,j] *= 3.28084
        
        time = datetime.fromtimestamp(tbCoord[i,2]).strftime("%H:%M:%S")
        
        if(tbCoord[i,0] > 120) : 
            errorDF.loc[len(errorDF.index)] = [oneID, 'Vehicle is higher than y=120',time]
        if(tbCoord[i,1] < 0) : 
            errorDF.loc[len(errorDF.index)] = [oneID, 'Vehicle is lower than y=0',time]
        if((tbCoord[i,0] < 71 and tbCoord[i,0] > 49) or (tbCoord[i,1] < 71 and tbCoord[i,1] > 49)) :
            errorDF.loc[len(errorDF.index)] = [oneID, 'Vehicle is on the guardrail section',time]
    
    return errorDF


def widthTest(oneID, oneCarDF) :
    errorDF = pd.DataFrame(columns=['Car ID','Error Message', 'Time'])
    wid = np.array(oneCarDF[['width', 'Timestamp']])
    
    for i in range(len(wid)) :
        time = datetime.fromtimestamp(wid[i,1]).strftime("%H:%M:%S")
        
        if(wid[i,0] > 12) :
            errorDF.loc[len(errorDF.index)] = [oneID, 'Vehicle is wider than 12ft',time]
    
    return errorDF
    
def speedTest(oneID, oneCarDF) :
    errorDF = pd.DataFrame(columns=['Car ID','Error Message', 'Time'])
    speed = np.array(oneCarDF[['speed', 'Timestamp']])
    
    for i in range(len(speed)) :
        time = datetime.fromtimestamp(speed[i,1]).strftime("%H:%M:%S")
        
        if(speed[i,0] < 17.8816) :
            errorDF.loc[len(errorDF.index)] = [oneID, 'Vehicle is slower than 40 mph',time]
    
    return errorDF