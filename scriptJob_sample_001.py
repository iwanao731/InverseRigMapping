def printaiTranslate():
    print 'printaiTranslate'

def printaiRotate():
    print 'printaiRotate'

def selectJob():
    nodes = cmds.ls(sl=True)

jobID3 = cmds.scriptJob( attributeChange=['pSphere7.translate', printaiTranslate] )    
jobID3 = cmds.scriptJob( attributeChange=['pSphere7.rotate', printaiRotate] )    
