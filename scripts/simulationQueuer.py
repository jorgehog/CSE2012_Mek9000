import sys, os, time





############### DESCRIPTION ################
"""
-Set case, and make sure you have a libfolder for it in the same dir as this file, i.e. dirCylinder for case Cylinder.

-This libDir have to contain the completed file structure. The following parts are modifyable from this program: 
              *controlDict: dt, endtime, writeInterval (if given by deltaT), runTimeModifiable
              *decomposeParDict: the number of processors (nCores)
              *LESProperties: The LESModel 
              
-Implement the solvertype for a given case in the 'prepare for runtime' section before the mainloop.
-Set values for deltaT, endTime, etc. (see the parameters class) in a parameter object. Load objects into a list corresponding to the LESModel list.

-The program will update the initialization files, build the mesh, decompose it, start the simulation, reconstruct it for all LESModels (with
 parameters) given by the user.
-The program will create a directory with a name reflecting the case and time of simulations.
-Each different (MUST BE DIFFERENT) simulation will get a subfolder corresponding to the LESModel and deltaT.
-If output to file is selected as True, a folder named "Output" in the case-time directory will hold all the different processes' output.
"""
##########################################



class parameters:
    """
    Struct-like class for keeping track of different parameter setups.
    """
    def __init__(self, deltaT, endTime, writeInterval = -1, runTimeMod = False, outputToFile = False):
        self.deltaT, self.endTime, self.writeInterval, self.runTimeModifiable = \
            deltaT, endTime, writeInterval, runTimeMod
        
        #If no interval is given, the simulation is set to dump data every 0.5 sec
        if writeInterval == -1:
            self.writeInterval = int(0.5/deltaT);





####### USER INITIALIZATIONS ############

nCores = 2; #number of processor cores aviable
case = "Cylinder"

dt = 0.0025;
endTime = 20;
outputToFile = True


#Set different parameters for different models (order respective to LESModels list)
LESModels = ['oneEqEddy', 'Smagorinsky','homogeneousDynSmagorinsky', 'dynLagrangian']
Parameters = [parameters(dt, endTime), parameters(dt, endTime), parameters(dt, endTime), parameters(dt, endTime)]

#Prepare Runtime
if outputToFile:
    os.system("mkdir %s/Output" % masterDir)

if case == 'Cylinder':
    solver = "pimpleFoam"

######################################











########## FOLDER STRUCTURE ##########
homeMaster = os.getcwd() + "/"

rawDateTime = time.asctime(time.localtime())
masterDir = homeMaster + case + rawDateTime.replace(' ', '')

libDir = homeMaster + "lib" + case

libFolders = ['0','constant','system']

print "initializing directory %s" % masterDir
os.mkdir(masterDir)

########################################



###### CHECKING NECESSITIES #######

if not os.path.exists(libDir):
    print "Case library not found: %s\n" % libDir
    exit(1)
libContainer = os.listdir(libDir);
    
quit = False;
for subfolder in libFolders:
    if subfolder not in libContainer:
        print "Missing folder %s/%s/" % (libDir, subfolder)
        quit = True

if quit:
    sys.exit(1);

##################################



########### MAIN LOOP ############

for i in range(len(LESModels)):

    LESModel = LESModels[i]
    params = Parameters[i]

    print "Running simulation '%s_dt%.3E'..." % (LESModel, params.deltaT)

    subDir = masterDir + "/" + LESModel + '_dt%.3E' % params.deltaT
    
    os.system("mkdir %s" % subDir)
    os.system("cp -r %s/* %s" % (libDir, subDir))
    
    print "Building mesh"
    os.system(("blockMesh -case %s" % subDir) + (" > %s/Output/meshOut_sim%d.txt" % (masterDir, i))*outputToFile)

    print "Updating inifiles"

    #Updating the LESProperties file
    LESfile = open("%s/constant/LESProperties" % subDir, 'r');
    rawLESFile = ''
    for line in LESfile: 
        if "LESModel" in line:
            tmpline = line.split();
            tmpline[1] = LESModel + ";"
            line = tmpline[0] + "        " + tmpline[1]
        rawLESFile += line

    LESfile.close()
    LESfile = open("%s/constant/LESProperties" % subDir, 'w');
    LESfile.write(rawLESFile)
    LESfile.close()


    #Updating the controlDict
    controlDict = open("%s/system/controlDict" % subDir, 'r');
    rawControlDict = ''
    for line in controlDict:
        for param in ['endTime', 'deltaT', 'writeInterval', 'runTimeModifiable']:
            if param in line:
                if param in line.split()[0]:
                    tmpline = line.split();
                    tmpline[1] = str(eval("params.%s" % param)) + ";"
                    line = tmpline[0] + "\t" + tmpline[1]
        rawControlDict += line

    controlDict.close()
    controlDict = open("%s/constant/LESProperties" % subDir, 'w');
    controlDict.write(rawControlDict)
    controlDict.close()


    #Seting the parallelization file if necessary
    if nCores != 1:
        paraDict = open("%s/system/decomposeParDict" % subDir, 'r')
        rawParaDict = ''
        for line in paraDict:
            if "numberOfSubdomains" in line:
                tmpline = line.split();
                tmpline[1] = str(nCores) + ";"
                line = tmpline[0] + "\t" + tmpline[1]
            rawParaDict += line;

        paraDict.close()
        paraDict = open("%s/constant/LESProperties" % subDir, 'w');
        paraDict.write(rawParaDict)
        paraDict.close()
        
        print "Decomposing mesh"
        os.system("decomposePar -case " + subDir + (" > %s/Output/decomposeParOut_sim%d.txt" % (masterDir, i))*outputToFile)
        
        print "Solving..."
        os.system(("mpirun -np %d" % nCores) + solver + " -parallel" + " -case " + subdir + \
                      (" > %s/Output/SolverOut_sim%d.txt" % (masterDir, i))*outputToFile)
        
        print "Reconstructing mesh values"
        os.system("reconstructPar -case " + subDir + (" > %s/Output/reconstructParOut_sim%d.txt" % (masterDir, i))*outputToFile)
    else:
        os.sysem(solver + " -case " + subDir + (" > %s/Output/SolverOut_sim%d.txt" % (masterDir, i))*outputToFile)

    print "Finished.\n"

################################
