import maya.cmds as cmds
import csv

def GetJointNames():

    # select hierarchy
    cmds.select(hierarchy=True)
    
    # select all type of joints
    all_joint_name = cmds.ls(sl=True, type='joint')
    
    return all_joint_name
        
def ConstructPositionHash(bones):

    positions = []
#    val = 1
    for bone in bones:
        vec = cmds.xform(bone, q=True, ws=True, t=True)
        #print "[%d] %s: %f %f %f" %(val, bone, vec[0], vec[1], vec[2])
        positions.append(vec[0])
        positions.append(vec[1])
        positions.append(vec[2])
 #       val = val + 1

    return positions

def edit_cell(row, column, value):
    return 1

def add_row(*args):
    last_row_num = cmds.scriptTable('table', query=True, rows=True)
    cmds.scriptTable('table', edit=True,insertRow=last_row_num)

def delete_row(*args):
    last_row_num = cmds.scriptTable('table', query=True, rows=True)
    cmds.scriptTable('table', edit=True,deleteRow=last_row_num - 1)

def setParam(*args):
    # set joint name to form
    count = 1
    select_names = GetJointNames()

    # set pos to form
    for j in select_names:
        cmds.scriptTable('table', cellIndex=(count,1), edit=True, cellValue=count)
        cmds.scriptTable('table', cellIndex=(count,2), edit=True, cellValue=j)
        count = count + 1
    
    positions = ConstructPositionHash(select_names)

    count = 0
    for t in positions:
        row = count/3 + 1
        col = count%3 + 3
        cmds.scriptTable('table', cellIndex=(row,col), edit=True, cellValue=t)
        count = count + 1
    
def saveFileDialog(*args):
    dialog = cmds.fileDialog(m=1);
    
#    fdialog = pm.fileDialog2(
#       ocm="on_save_dialog_file",
#       fm=0,
#        ff="CSV Files (*.csv);;All Files (*.*)",
#        dialogStyle=2)
    
    o_file = str(dialog)
    #print o_file

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
    
def JointComponentEditor(*args):
        
    window = cmds.window(title='Joint Component Editor', widthHeight=(720, 310))
    
    form = cmds.formLayout()
    table =  cmds.scriptTable('table',rows=len(GetJointNames()), columns=5,columnWidth=([1,30], [2,300],[3,120],[4,120],[5,120]),
            label=[(1,"No."), (2,"JointName"), (3,"transrateX"), (4,"transrateY"), (5,"transrateZ")],
            cellChangedCmd=edit_cell)
    
#    resetButton = cmds.button(label="Reset",command=add_row)
    resetButton = cmds.button(label='Save', command=saveFileDialog)

#    closeButton = cmds.button(label="Delete Row",command=delete_row)
    closeButton = cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)') )
    
    setParam()
#    setRigAttribute()

    cmds.formLayout(form, edit=True, 
        attachForm=[(table, 'top', 0), (table, 'left', 0), (table, 'right', 0), 
        (resetButton, 'left', 0), (resetButton, 'bottom', 0), 
        (closeButton, 'bottom', 0), (closeButton, 'right', 0)],
        attachControl=(table, 'bottom', 0, resetButton), 
        attachNone=[(resetButton, 'top'),(closeButton, 'top')], 
        attachPosition=[(resetButton, 'right', 0, 50), (closeButton, 'left', 0, 50)]
        )

    cmds.showWindow( window )
    

def LoadRigAttribute(*args):

    # Open Dialog to select csv file
    dialog = cmds.fileDialog(m=0);        
    o_file = str(dialog)
    #print o_file

    # Load csv file
    reader = csv.reader(file(o_file, 'r'))
    #print reader

    # skip first row line
    header = next(reader)

    # Show each attribute
    for row in reader:
        #print row[0] + ',' + row[1] + ',' + row[2]
        number = int(row[0])
        ctrlName = row[1];
        numAttrib = int(row[2])

        for i in range(numAttrib):
            att = row[3 + i*2+0]
            val = float(row[3 + i*2+1])
            #print ctrlName + "." + att + " : " + str(val)

            settable = cmds.getAttr(ctrlName + "." + att, settable = True)
            lockable = cmds.getAttr(ctrlName + "." + att, lock = True)

            if(settable == True and lockable == False):
                gettype = cmds.setAttr(ctrlName + "." + att, val)

def setRigAttribute(*args):

    cmds.select(hierarchy=True)
    oSel = cmds.ls(sl=True, type='transform')    
    #print oSel

    row = 1

    for i in oSel:
        
        add_row()

        #name
        #print i
        cmds.scriptTable('table', cellIndex=(row,1), edit=True, cellValue=row-1)
        cmds.scriptTable('table', cellIndex=(row,2), edit=True, cellValue=i)
        
        numAttrib = 0

        for att in cmds.listAttr(i, unlocked = True , settable = True, visible = True , keyable = True, connectable = False, scalar = True, write = True, hd = True, hnd = False) or []:

            # only limited for translate and rotate
            if 'translate' in att or 'rotate' in att:
        
                #Tmpsel = cmds.ls(sl=True,type='transform')[0] 

                gettype = cmds.getAttr(i + "." + att, type=True)

                col = numAttrib*2 + 4

                if gettype == "bool":
                    BoolValue = cmds.getAttr(i + "." + att)
                    #print '%s : %i', att, BoolValue
                    cmds.scriptTable('table', cellIndex=(row,col), edit=True, cellValue=att)
                    cmds.scriptTable('table', cellIndex=(row,col+1), edit=True, cellValue=BoolValue)
                else:
                    getValue = cmds.getAttr(i + "." + att)
                    #print "[%s] %f" %(att, getValue)
                    cmds.scriptTable('table', cellIndex=(row,col), edit=True, cellValue=att)
                    cmds.scriptTable('table', cellIndex=(row,col+1), edit=True, cellValue=getValue)
#                    print getValue

                numAttrib = numAttrib + 1

        # add num of attribute
        cmds.scriptTable('table', cellIndex=(row,3), edit=True, cellValue=numAttrib)
        row = row + 1

def saveRigFileDialog(*args):
    dialog = cmds.fileDialog(m=1);
        
    o_file = str(dialog)
    print o_file

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
                data_list = ["No.", "RigName", "transrateX", "transrateY", "transrateZ", "rotateX", "rotateY", "rotateZ"]
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

def RigComponentEditor(*args):
        
    window = cmds.window(title='Rig Component Editor', widthHeight=(1200, 600))
    
    form = cmds.formLayout()

    table =  cmds.scriptTable(
            'table',rows=0, columns=15,columnWidth=([1,30],[2,300],[3,30],[4,80],[5,50],[6,80],[7,50],[8,80],[9,50],[10,80],[11,50],[12,80],[13,50],[14,80],[15,50]),
            label=[(1,"No."), (2,"rigName"), (3,"num"), (4,"label[0]"), (5,"val[0]"), (6,"label[1]"), (7,"val[1]"), (8,"label[2]"), (9,"val[2]"), (10,"label[3]"), (11,"val[3]"), (12,"label[4]"), (13,"val[4]"), (14,"label[5]"), (15,"val[5]")],
            cellChangedCmd=edit_cell)


    resetButton = cmds.button(label='Save', command=saveRigFileDialog)
    closeButton = cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)') )
    
    setRigAttribute()
        
    cmds.formLayout(form, edit=True, 
        attachForm=[(table, 'top', 0), (table, 'left', 0), (table, 'right', 0), 
        (resetButton, 'left', 0), (resetButton, 'bottom', 0), 
        (closeButton, 'bottom', 0), (closeButton, 'right', 0)],
        attachControl=(table, 'bottom', 0, resetButton), 
        attachNone=[(resetButton, 'top'),(closeButton, 'top')], 
        attachPosition=[(resetButton, 'right', 0, 50), (closeButton, 'left', 0, 50)]
        )

    cmds.showWindow( window )

def printTranslate():    
    print "printTranslate"

def printRotate():
    print "printRotate"

listJobID = []

def enableScriptJobs():
    
    # select all joint name
    select_names = GetJointNames()    

    for name in select_names:
        jobID1 = cmds.scriptJob( attributeChange=[name + '.translate', printTranslate] )    
        jobID2 = cmds.scriptJob( attributeChange=[name + '.rotate', printRotate] )
        listJobID.append(jobID1)
        listJobID.append(jobID2)

    print len(listJobID)

def disableScriptJobs():
    
    for id in listJobID:
        cmds.scriptJob(kill=id,force=True)

    #remove all job id    
    del listJobID [:]
    print len(listJobID)    

def InverseRigMapTool():
    # GUI Interface
    window = cmds.window(title='Inverse Rig Mapping Tool', widthHeight=(500, 100))
    cmds.columnLayout(adjustableColumn = True)
#    cmds.button(label='Save Joint/Rig Parameters', command=Save_Joint_Rig)
    cmds.button(label='Save Joint Positon', command=JointComponentEditor)
    cmds.button(label='Save Rig Parameters', command=RigComponentEditor)
#    cmds.button(label='Load Joint Pose', command=JointComponentEditor)
    cmds.button(label='Load Rig Parameters', command=LoadRigAttribute)
    cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)') )
    maya.cmds.showWindow()

