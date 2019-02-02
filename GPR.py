import maya.cmds as cmds
import numpy as np
import random
import csv
from numpy import linalg as LA

n = 24
targetFileNo = 30
theta = 0.0001

def computeKernel(x1, x2): 
	return np.sqrt(np.power(LA.norm(x1 - x2), 2) + np.power(theta,2))
    
def selectFilePath():
    o_file = str(cmds.fileDialog(m=0))
    print o_file
    return o_file

def loadJointData(o_file):

    # Load csv file
    reader = csv.reader(file(o_file, 'r'))

    # skip first row line
    header = next(reader)

    arr = np.empty((0,3), dtype = np.float64)

    # Show each attribute
    for row in reader:
        translateX = np.float64(row[2])
        translateY = np.float64(row[3])
        translateZ = np.float64(row[4])
        arr = np.append(arr, np.array([[translateX,translateY,translateZ]]), axis=0)

    return arr
    

def loadJointData2(o_file):

    # Load csv file
    reader = csv.reader(file(o_file, 'r'))

    # skip first row line
    header = next(reader)

    arr = np.empty((0,3), dtype = np.float64)

    # Show each attribute
    for row in reader:
        jointName = row[1]
        vec = cmds.xform(jointName, q=True, ws=True, t=True)
        translateX = np.float64(vec[0])
        translateY = np.float64(vec[1])
        translateZ = np.float64(vec[2])
        arr = np.append(arr, np.array([[translateX,translateY,translateZ]]), axis=0)

    return arr
    
def loadRigData():

    # load first rig data
    reader = csv.reader(file(defineYFilePath(1), 'r'))
    row_count = sum(1 for row in reader)

    print "row_count"
    print row_count

    MAXCOL = 30
    Y = np.arange(n * row_count * MAXCOL).reshape(n, row_count, MAXCOL)
    
    print Y.shape
    # Show each attribute
    for i in range(n):
        reader = csv.reader(file(defineYFilePath(i), 'r'))
        header = next(reader)
        
        j = 0
        for row in reader:
            Y[i][j][0] = int(row[0])    # number
            #Y[i][j][1] = str(row[1])    # ctrlName
            Y[i][j][2] = int(row[2])    # numAttrib
            for k in range(int(row[2])):
                r = 3 + k * 2
                #Y[i][j][r+0] = long(row[r+0])
                Y[i][j][r+1] = float(row[r+1])
            
            j = j + 1
        
    return Y


def loadRigData2():

    # Show each attribute
    for i in range(n):      
        if i == 0:
            reader = csv.reader(file(defineYFilePath(i), 'r'))
            header = next(reader)
            tmp = list(reader)
        else:
            reader = csv.reader(file(defineYFilePath(i), 'r'))
            header = next(reader)
            b = list(reader)
            tmp = np.append(tmp, b, axis=0)

    return tmp
    
def defineXFilePath(count):
    fileDir = 'D:\Dropbox\Digihari\cgvfx\InverseRigMapping\data'
    
    if count < 10:
        name = '0' + str(count)
    else:
        name = str(count)
        
    name = fileDir + '\stewart_all_joint_pose_' + name + '.csv'
    print name
    return name


def defineYFilePath(count):
    fileDir = 'D:\Dropbox\Digihari\cgvfx\InverseRigMapping\data'
    
    if count < 10:
        name = '0' + str(count)
    else:
        name = str(count)
        
    name = fileDir + '\stewart_all_rig_pose_' + name + '.csv'
    print name
    return name

def computeK():
    
    K = np.empty((n,n), dtype = np.float64)
    
    for i in range(n):
        a = loadJointData(defineXFilePath(i))
        for j in range(n):
            b = loadJointData(defineXFilePath(j))
            K[i][j] = computeKernel(a, b)
    
    #print K
    return K

# Computation the difference between current pose and database poses
def computeKast():
    
    # TBD
    Kast = np.empty((1,n), dtype = np.float64)

    # Input arbitrary joint positions (TBD)lo
    #a = loadJointData(defineXFilePath(targetFileNo))
    
    a = loadJointData2(defineXFilePath(targetFileNo))
   
    for i in range(n):
        b = loadJointData(defineXFilePath(i))
        Kast[0][i] = computeKernel(a, b)    
            
    return Kast
    
def constructY(allY, i):
    
	numRows = (allY.shape[0]/n)
	numAttrib = int(allY[i, 2])
	A = np.zeros((n, numAttrib))
	
	for k in range(n):
	    for j in range(numAttrib):
	        #print k, j, allY[k*numRows+i, 3+j*2+1]
	        A[k, j] = float(allY[k*numRows+i, 3+j*2+1])
	        
	return A

# Pre-computing from the database for learning
def computePreGPR():

    theta = 0.00001
    I = np.identity(n, dtype=float)
    
    return computeKast().dot( LA.inv(computeK() + (theta * I)) )
    

def saveFileDialog():
    dialog = cmds.fileDialog(m=1);
    o_file = str(dialog)

    if not (cmds.file(o_file,query=True, exists=True)):
        tmp_csv_file = open(o_file, 'w' ,os.O_CREAT)
    else:
        tmp_csv_file = open(o_file, 'w')
    
    writer = csv.writer(tmp_csv_file, lineterminator='\n')
    
    all_rows = cmds.scriptTable('table', query=True, rows=True)
    for o_r in range(all_rows):
            
        all_colums = cmds.scriptTable('table', query=True, columns=True)
        data_list = []
        for o_c in range( all_colums - 1):
            if o_r == 0:
                data_list = ["No.", "JointName", "transrateX","transrateY","transrateZ"]
            else:
                cell_list = cmds.scriptTable('table', cellIndex=(o_r,o_c + 1), query=True, cellValue=True)
                if o_c == 0:
                    if type(cell_list) == list:
                        cell_text = "".join(cell_list)
                        #print cell_text
                    elif cell_list == None:
                        cell_text = u''
                    else:
                        cell_text = cell_list
                    data_list.append(cell_text)
                elif o_c == 1:
                    if type(cell_list) == list:
                        cell_text = "".join(cell_list)
                        #print cell_text
                    elif cell_list == None:
                        cell_text = u''
                    else:
                        cell_text = cell_list
                    data_list.append(cell_text)
                else:
                    if type(cell_list) == list:
                        cell_text = "".join(cell_list)
                    elif cell_list == None:
                        cell_text = u''
                    else:
                        cell_text = cell_list
                    data_list.append(cell_text)
        writer.writerow(data_list)
    tmp_csv_file.close()
    
def setParam(allY):
    
#----------------------------------
#    dialog = cmds.fileDialog(m=1);
#    o_file = str(dialog)

#    if not (cmds.file(o_file,query=True, exists=True)):
#        tmp_csv_file = open(o_file, 'w' ,os.O_CREAT)
#    else:
#        tmp_csv_file = open(o_file, 'w')
    
#    writer = csv.writer(tmp_csv_file, lineterminator='\n')
#----------------------------------
    
    # intialize
    i = 0
    rowList = []

    # pre computing
    pre = computePreGPR()

    # load data
    reader = csv.reader(file(defineYFilePath(0), 'r'))

    # skip first row line
    header = next(reader)

    for row in reader:
        
        # initialize
        rowList.append([]) 

        # compute main
        Yi = pre.dot(constructY(allY, i))

        # set parameter
        for k in range(Yi.size):
            ctrlName = row[1] + "." + row[3 + k * 2]
            settable = cmds.getAttr(ctrlName, settable = True)
            lockable = cmds.getAttr(ctrlName, lock = True)
            if(settable == True and lockable == False):
                cmds.setAttr(ctrlName, Yi[0, k])        

        # save file
        #for k in range(Yi.size):
        #    row[3 + k * 2  + 1] = Yi[0, k]
        
        #writer.writerow(row)

        #rowList.append(row)    
            
        i = i + 1
            
def computeGPR():

    #pre = computePreGPR()
    
    # load training data
    allY = loadRigData2()    

    # estimate rig paramters
    setParam(allY)    

computeGPR()

