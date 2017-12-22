'''
Created on Dec 19, 2017

@author: David Stocker
'''

__author__ = 'David Stocker'
__copyright__ = 'Copyright 2017, David Stocker'   
 
__license__ = 'MIT'
__version__ = '0.0.1'
__maintainer__ = 'David Stocker'
__email__ = 'david.stocker@sap.com'


import sys
import os
import codecs
import zipfile
import tempfile
import argparse
from os.path import expanduser
from xml.dom import minidom

#classes
class NonMigratablePluginError(ValueError):
    pass


def listFromFile(listFileName):
    listFile = open ( listFileName )
    returnList = listFile.readlines()
    listFile.close()         
    return returnList
    
    
def getCodePageFromFile(fileURI):
    return "utf-8"



def walkRepository():
    '''
        Walk through the Analysis-config/plugins directory and catalog which plugins are:
        already 2.x capable
        can be migrated (are div with no modes attribute)
        of the Schema Repository given at <dataLocation> and return 
    '''
   
    #Go through the condition repository directory and load the files up
    theGood = []  #already 2.x capable
    theBad = []   #can be migrated (are div with no modes attribute)
    theUgly = []  #modes is present and commons only
    dontBother = []  #handlerType='sapui5' and there is no modes attribute, or it is commonls only
    
    homeDir = expanduser("~")
    plugindDir = os.path.join(homeDir, "Analysis-config", "plugins")
    pluginList = os.listdir(plugindDir)
    for pluginFile in pluginList:
        #Graph.logQ.put( [logType , logLevel.DEBUG , method , 'Examining %s' % package])
        if pluginFile.endswith(".jar"):
            fileName = os.path.join(plugindDir, pluginFile)
            jarContents = zipfile.ZipFile(fileName, 'r')
            for pluginFileName in jarContents.namelist():
                if pluginFileName == "contribution.xml":
                    pluginFile = os.path.join(homeDir, "Analysis-config", "plugins", pluginFileName)
                    fileObj = jarContents.read(pluginFileName)
                    fileStream = str(fileObj, "utf-8")
                    
                    fileXML = minidom.parseString(fileStream.encode( "utf-8" ))
                    if fileXML == None:
                        raise Exception("Invalid contribution.xml in plugin %s" %pluginFile)
                    
                    for componentElement in fileXML.getElementsByTagName("component"):
                        
                        title = componentElement.getAttribute("title")
                        handlerType = componentElement.getAttribute("handlerType")
                        try: 
                            modes = componentElement.getAttribute("modes")
                            if modes.endswith("m"):
                                theGood.append(title)
                            elif handlerType != "sapui5":
                                theUgly.append(title)
                            else:
                                dontBother.append(title)
                        except: 
                            if handlerType != "sapui5":
                                theBad.append(title)

    results = {'theGood':theGood, 'theBad':theBad,  'theUgly':theUgly, 'dontBother':dontBother}   
    return results





def migratePluginInstaller(installerLocation, sourceFile, targetFile):
    """
        Make the given file Lumira 2.x compatable, if possible.
        If contibution.xml has a component title element with attribute handlerType = 'div'
            AND the attribute modes reads modes='commons' or the modes attribute is missing
            
            replace the modes attribute (or add a new one) with modes = 'commons m'
            
        Throw an exception if handlerType='sapui5'
        
        Lumira Designer Installer .zip archives contain several .jar archives inside a container .zip .zip.  Contribution.xml is
            inside the .jar located in the plugins directory within the .zip, so we need to do the migration in two stages.
        1 - Open the .jar, copy all of its contents to a new jar and modify the contribution.xml.  Write the jar in a temp directory
        2 - Create the .zip, copying almost everything from the old .zip and substituting the new .jar
    """
    
    nFilesMigrated = 0
    
    if sourceFile.endswith(".zip"):
        pass
    else:
        sourceFile = "%s.zip" %sourceFile
        
    if targetFile.endswith(".zip"):
        pass
    else:
        targetFile = "%s.zip" %targetFile
    
    #create two temp directories, where we'll extract the outer .zip and inner.jar
    tempDirZip = tempfile.mktemp()
    
    pathSource = os.path.join(installerLocation, sourceFile)
    pathTarget = os.path.join(installerLocation, targetFile)

    
    zipSource = zipfile.ZipFile(pathSource)
    zipSource.extractall(tempDirZip)
    pathTempPlugins = os.path.join(tempDirZip, "plugins")
    jarNameList = os.listdir(pathTempPlugins)
    for jarName in jarNameList:
        jarPath = os.path.join(pathTempPlugins, jarName)
        tempDirJar = tempfile.mktemp()
        zipJar = zipfile.ZipFile(jarPath)
        zipJar.extractall(tempDirJar)
        zipJar.close()
        
        debugList = pathContribution = os.listdir(tempDirJar)
        pathContribution = os.path.join(tempDirJar, "contribution.xml")
        fileObj = codecs.open( pathContribution, "r", "utf-8" )
        fileStream = fileObj.read() # Returns a Unicode string from the UTF-8 bytes in the file   
        fileXML = minidom.parseString(fileStream.encode( "utf-8" ))
        if fileXML == None:
            raise Exception("Invalid contribution.xml in plugin %s" %pathSource)
        
        migrate = False
        
        for componentElement in fileXML.getElementsByTagName("component"):
            
            title = componentElement.getAttribute("title")
            handlerType = componentElement.getAttribute("handlerType")
            try: 
                modes = componentElement.getAttribute("modes")
                if modes.endswith("m"):
                    print("%s is already 2.x ready and needs no changes.  Left unchanged." %title)
                elif handlerType == "sapui5":
                    print("%s is a UI5 component and can't be automatically migrated.  Left unchanged." %title)
                else:
                    migrate = True
                    componentElement.attributes["modes"].value = "commons m"
            except: 
                if handlerType == "sapui5":
                    print("%s is a UI5 component and can't be automatically migrated.  Left unchanged." %title)
                else:
                    migrate = True
                    
                    modesAttribute = fileXML.createAttribute('modes')
                    modesAttribute.value = "commons m"
                    componentElement.setAttributeNode(modesAttribute)
                    nFilesMigrated = nFilesMigrated + 1
                    print("%s metadata modified to be Lumira 2.x compliant." %title)
                
        #all done.  Write back to the XML file
        fileObj.close()
        
        if migrate == True:
            fileObj = codecs.open( pathContribution, "w", "utf-8" )
            fileXML.writexml(fileObj)
            fileObj.close()
        
        jarPathDirList = os.listdir(tempDirJar)
        for unusedJarPathDirMember in jarPathDirList:
            updatedJar = zipfile.ZipFile(jarPath, mode='w')
            zipDir(updatedJar, tempDirJar)
    
    finalZip = zipfile.ZipFile(pathTarget, mode='w')
    zipDir(finalZip, tempDirZip)
    print ("Migrated %s components" %nFilesMigrated)



def zipDir(zipArchive, tempDirZip, extractPath = None):
    """
        Adds a folder to an open .zip (or .jar) archive, zipArchive
        tempDirZip is the location of the directory to be migrated
        This method is recursive for nested folders.  extractPath tracks the folder structure within the zip file
    """
    zipFileContentList = os.listdir(tempDirZip)
    for sFileName in zipFileContentList:
        sFilePath = os.path.join(tempDirZip, sFileName)
        basename = os.path.basename(sFilePath)
        if extractPath is None:
            nestedEP = "%s/%s" %(basename, sFileName)
            zipArchive.write(sFilePath, basename)
            if os.path.isdir(sFilePath):
                zipDir(zipArchive, sFilePath, basename)
        else:
            nestedEP = "%s/%s" %(extractPath, sFileName)
            zipArchive.write(sFilePath, nestedEP)
            if os.path.isdir(sFilePath):
                zipDir(zipArchive, sFilePath, nestedEP)          
                


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lumira Designer SDK Extension migration tool.  This is not officially supported SAP software no guarantee\n is made that any extension migrated with this utility will work properly.")
    parser.add_argument("-r", "--report", nargs='?', const=True, type=bool, help="|String| Generate a report, showing the 2.x compatibility of currently installed extensions.  If this flag is used, all others are ignored.")
    parser.add_argument("-f", "--folder", type=str, help="|String| If an installer file is to be migrated, this is its folder location.  Use the location of the .zip installer, not the Analysis-config\\plugins folder.")
    parser.add_argument("-s", "--srcfile", type=str, help="|String| The extension .zip installer file to be migrated.")
    parser.add_argument("-t", "--targfile", type=str, help="|String| The filename of the 'updated' installer file")
    args = parser.parse_args()
    
    
    #Read the command line options
    genReport = True
    if args.report:
        genReport = True
    elif args.folder:
        genReport = False
            
    if genReport:
        report = walkRepository()
        strReport = "Overview of installed extensions.  \n"
        
        strReport = "%sAlready 2.x compatible and can run in m mode:\n" %strReport
        for cExtension in report["theGood"]:
            strReport = "%s  %s\n" %(strReport, cExtension)
            
        strReport = "%s\nNot  2.x compatible, but are *likely* candidates for migration.  They have no modes attribute, but are div based and unlikely to have a UI5 problem:\n" %strReport
        for bExtension in report["theBad"]:
            strReport = "%s  %s\n" %(strReport, bExtension)
           
        strReport = "%s\nNot 2.x compatible, but are *possible* candidates for migration.\n   They have a modes attribute that explicitly limits them to commons based apps, but are div based and unlikely to have a UI5 problem:\n" %strReport
        for uExtension in report["theUgly"]:
            strReport = "%s  %s\n" %(strReport, uExtension)
            
        strReport = "%s\nAre UI5 based extensions that support only commons mode and can't be used in Lumira 2.x:\n" %strReport
        for xExtension in report["dontBother"]:
            strReport = "%s  %s\n" %(strReport, xExtension)
            
        strReport = "%s\nExercise caution when migrating components, keep the original .zip installer and test thoroughly, before deploying productively.  Also, it is always best to get a 2.x compatible version of the extension from the original developer, if possible." %strReport
        print(strReport)
    else:
        if args.srcfile and args.targfile:
            #be forgiving, if the user has not added a .zip suffic in the -s and -t file names
            if args.srcfile.endswith(".zip"):
                sFile = args.srcfile
            else:
                sFile = "%s.zip" %args.srcfile
                
            if args.targfile.endswith(".zip"):
                tFile = args.targfile
            else:
                tFile = "%s.zip" %args.targfile
                
            if sFile == tFile:
                print("If the -f parameter is used, there valid (and unique) values for the -s and -t parameters.  %s is source (-s).\n    -t must be a different file name, to ensure that no destructive changes are made and the original is preserved")
                sys.exit()
            else:
                migratePluginInstaller(args.folder, sFile, tFile)
                print("%s created in folder %s, with SAP UI5 modes commons and m.\n  Uninstall the original from the Lumira Designer client and the BIP and install the updated version" %(tFile, args.folder))
                sys.exit()
        else:
            print("If the -f parameter is used, there valid (and unique) values for the -s and -t parameters.")
            sys.exit()          
