import os
import matplotlib as matplot
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.patches as patches
import math
import numpy as np
import pandas as pd
from datetime import datetime
import cv2

input_directory = r"C:\I24 Motion Project\YB Animation Software\csvData"

class Animation :
    def __init__(self, filename) :
        self.data_path = input_directory + "\\" + filename
        
    def csv_to_framesnaps(self, maxFrameNum=0) :
        # Divide all the data into frame numbers(1 ~ 2000). Then save each frame snapshot as a .jpg file 
        # within a separate folder to later create an animation.
        df = read_full_data(self.data_path, 0)
        
        maxFrameNum = int(max(df['Frame #']))    # Find the maximum number of frame
        xmin, xmax = findMinMax('all')
        ymax = 120
        aspectRatio = (xmax-xmin) / (3 * ymax)
        timeStamp = ''
        
        for i in range(100):
            # Plot dimension setup
            fig, ax = plt.subplots(figsize=(15,8))
            # img = plt.imread('../background_img/highway_360ft.jpg')
            # ax.imshow(img, extent=[xmin,xmax,0,ymax])
            ax.set_aspect(aspectRatio)
            plt.xlim(xmin, xmax)
            plt.ylim(0, ymax)
            plt.xlabel('feet')
            plt.ylabel('feet')

            # Lane drawing only for development mode
            plt.axhline(108, c = 'black', ls='dashed', dashes=(10,20))
            plt.axhline(96, c = 'black', ls='dashed', dashes=(10,20))
            plt.axhline(84, c = 'black', ls='dashed', dashes=(10,20))
            plt.axhline(71, c = 'yellow', ls='solid')
            plt.axhline(49, c = 'yellow', ls='solid')
            plt.axhline(36.5, c = 'black', ls='dashed', dashes=(10,20))
            plt.axhline(24, c = 'black', ls='dashed', dashes=(10,20))
            plt.axhline(12, c = 'black', ls='dashed', dashes=(10,20))

            plt.figure(i+1)

            # extract the ID & road coordinates of the bottom 4 points of all vehicles at frame # i
            frameSnap = df.loc[(df['Frame #'] == i)]
            frameSnap = np.array(frameSnap[['tr_x','tr_y','tl_x','tl_y','bl_x','bl_y','br_x','br_y',
                                            'ID','direction','Timestamp', 'speed']])
            coordToFt(frameSnap)

            # Looping thru every car in the frame
            for j in range(len(frameSnap)):  
                carID = frameSnap[j,8]
                carSpeed = frameSnap[j,11] 
                coord = frameSnap[j,0:8]     # Road Coordinates of the Car
                coord = np.reshape(coord,(-1,2)).tolist()
                coord.append(coord[0])
                xs, ys = zip(*coord)

                xcoord = frameSnap[j,2]
                ycoord = frameSnap[j,3]

                # Displaying information above the car
                if xcoord < xmax and xcoord > xmin and ycoord < ymax :
                    # Prod Mode
                        # plt.text(xcoord, ycoord, str(int(carSpeed * 2.2369)) + ' mph', weight='bold')
                    # Dev Mode
                    if(not(math.isnan(carID))) :
                        plt.text(xcoord, ycoord, int(carID), fontsize='xx-large', weight='bold')

                oneCarColor = getCarColor(carSpeed, carID)

                # Plotting the car
                newxs = fillBetweenX(xs)
                newys = fillBetweenY(ys)
                ax.plot(newxs, newys, c = oneCarColor)
                ax.fill(newxs, newys, c = oneCarColor)

            # Prod Mode : Timestamp
            # If there are cars in this frame, update timeStamp. If not, timeStamp from previous cycle
            # will be used
            # if(len(frameSnap) != 0 and not(math.isnan(frameSnap[0,10]))) :
            #     timeStamp = datetime.fromtimestamp(frameSnap[0,10]).strftime("%H:%M:%S")

            plt.title(i, fontdict={'fontsize':'x-large','fontweight':'bold'}, pad=20)
            # plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
            # plt.margins(0,0)
            # add when creating for presentation-> , dpi=100
            plt.savefig('../Animation/Pictures/TM_1000_GT/' + format(i,"04d") + '.jpg', dpi=100)
            
            
    def csv_to_framesnap_synth(self) :
        # Divide all the data into frame numbers(1 ~ 2000). Then save each frame snapshot as a .jpg file 
        # within a separate folder to later create an animation.
        df = read_synth_data(self.data_path, 0)
        df = df.reindex(columns=['x','y','Frame #','Timestamp','ID','speed'])
        
        maxFrameNum = int(max(df['Frame #']))    # Find the maximum number of frame
        xmin, xmax = 3000, 3800
        ymax = 20
        aspectRatio = (xmax-xmin) / (3 * ymax)
        
        for i in range(500) :
            # Plot dimension setup
            fig, ax = plt.subplots(figsize=(15,8))
            ax.set_aspect(aspectRatio)
            plt.xlim(xmin, xmax)
            plt.ylim(0, ymax)
            plt.xlabel('meters')
            plt.ylabel('meters')

            plt.figure(i+1)
            
            # extract the ID & road coordinates of the bottom 4 points of all vehicles at frame # i
            frameSnap = df.loc[(df['Frame #'] == i)]
            frameSnap = np.array(frameSnap[['x','y','Frame #','Timestamp','ID','speed']])

            # Looping thru every car in the frame
            for j in range(len(frameSnap)):  
                carID = frameSnap[j,4]
                carSpeed = frameSnap[j,5] 
                xs, ys = frameSnap[j,0], frameSnap[j,1]

                # Displaying information above the car
                plt.text(xs, ys, int(carID), fontsize='large')
                oneCarColor = getCarColor(carSpeed, carID)
                # Plotting the car
                ax.plot(xs, ys, c = 'red', marker='o', markersize=15)

            plt.title(i, fontdict={'fontsize':'x-large','fontweight':'bold'}, pad=20)
            # plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
            # plt.margins(0,0)
            plt.savefig('../Animation/Pictures/chunk10/' + format(i,"04d") + '.jpg', dpi=100)


    def animate(self) :
        image_folder = '../Animation/Pictures/chunk10'
        video_name = '../Animation/Videos/chunk10.mp4'

        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        images.sort()

        frame = cv2.imread(os.path.join(image_folder, images[1]))
        height, width, layers = frame.shape
        video = cv2.VideoWriter(video_name, 0, 10, (width,height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()


def read_full_data(file_name, skiprows = 0, index_col = False):
    df = pd.read_csv(file_name, skiprows = skiprows, index_col = index_col)
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


def read_synth_data(file_name, skiprows = 0, index_col = False) :
    df = pd.read_csv(file_name, skiprows = skiprows, index_col = index_col)
    df = df[['x','y','Frame #','Timestamp','ID','speed']]
    
    return df


def findMinMax(cameraNum) :    
    camVisionRange = {
        1 : [200, 440],
        2 : [400, 680],
        3 : [630, 790],
        4 : [640, 810],
        5 : [700, 950],
        6 : [820, 1240],
        'all': [200, 1200]
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