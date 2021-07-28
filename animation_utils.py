from matplotlib import cm
import numpy as np
import pandas as pd
import math


def read_data(file_name, skiprows = 0, index_col = False):
    df = pd.read_csv(file_name, skiprows = skiprows,error_bad_lines=False,index_col = index_col)
    df = df[['bbr_x','bbr_y','fbr_x','fbr_y','fbl_x','fbl_y','bbl_x','bbl_y',
             'Frame #','Timestamp','ID','direction','speed']]
    
    rightToLeftDF = df.loc[df['direction'] == -1]
    rightToLeftDF.columns = ['tr_x','tr_y','tl_x','tl_y','bl_x','bl_y','br_x','br_y',
                             'Frame #','Timestamp','ID','direction','speed']
    leftToRightDF = df.loc[df['direction'] == 1]
    leftToRightDF.columns = ['bl_x','bl_y','br_x','br_y','tr_x','tr_y','tl_x','tl_y',
                             'Frame #','Timestamp','ID','direction','speed']
    leftToRightDF = leftToRightDF[['tr_x','tr_y','tl_x','tl_y','bl_x','bl_y','br_x','br_y',
                                   'Frame #','Timestamp','ID','direction','speed']]
    
    df = pd.concat([rightToLeftDF, leftToRightDF])
    return df


def findMinMax(cameraNum) :    
    camVisionRange = {
        1 : [200, 440],
        2 : [440, 650],
        3 : [640, 770],
        4 : [640, 770],
        5 : [750, 930],
        6 : [920, 1200],
        'all': [200, 1800]
    }
    
    return camVisionRange[cameraNum][0], camVisionRange[cameraNum][1]


def getCarColor(speed, carID) :
    if(carID == 316120) : return 'black'
    elif(carID == 344120) : return 'red'
    elif(carID == 399120) : return 'white'
    else :
        coolwarm = cm.get_cmap('coolwarm_r')
    
        if speed > 34 :
            return coolwarm(0.999)
        else :
            normVal = speed / 34.0
            return coolwarm(normVal)

        
def coordToFt(frameSnap) :
    for i in range(len(frameSnap)) :
        for j in range(0,8) :
            frameSnap[i,j] *= 3.28084
        # CarID
        if math.isnan(frameSnap[i,8]) : frameSnap[i,8] = 0
        # Timestamp
        if math.isnan(frameSnap[i,10]) : frameSnap[i,10] = 0
        # Speed
        if math.isnan(frameSnap[i,11]) : frameSnap[i,11] = 0
    
        

def fillBetweenX(xs) :
    # Minor misalignments between the coordinates causes the fill function
    # to fill color in random spaces. Fixing the numbers to be exact.
    temp = list(xs)
    temp[1] = temp[2]
    temp[3] = temp[0]
    newxs = tuple(temp)
    
    return newxs


def fillBetweenY(ys) :
    temp = list(ys)
    temp[1] = temp[0]
    temp[2] = temp[3]
    newys = tuple(temp)
    
    return newys