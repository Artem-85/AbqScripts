

import sys
import datetime
import time
import math
import os, os.path, re
from collections import namedtuple

# simple class for parsing additional arguments: "abaqus viewer/cae -nogui -- -job <jobname> -path <path>"  etc.
class AbqArgParse:

    __inp_args = []

    def parse(self):

        params = {
            'job':None,
            'path':None,
            # 'output':None,
            # 'start':None,
            # 'end':None
            }

        for pair in self.__inp_args:

            if ' ' in pair:
                
                key, val = pair.split(' ',1)

                key = key.strip()

                val = val.strip()

                if key in params:

                    params[key] = val

        indices = ' '.join([param for param in params])
                    
        arg_list = [params[param] for param in params]

        Args = namedtuple('Args', indices)

        self.args = Args(*arg_list)

        return self.args

    def __init__(self):

        # read arguments from the system and re-split them 

        cmd_line = ' '.join(sys.argv)

        self.__inp_args = cmd_line.split(' -')

        return

# write error log in case of typical errors
def error_log(message,ex=True):

    with open('error_log.txt', 'a') as ferr:

        ferr.write(message)

    if ex:

        ferr.close()

        sys.exit()

def get_xyplot(x_label,y_label,nset,step):

    # define additional variables

    plot = "{}-vs-{}".format(y_label,x_label)

    force_type = 'Reaction moment' if 'RM' in y_label else 'Reaction force'

    displ_type = 'Rotational displacement' if 'UR' in x_label else 'Spatial displacement'

    y_title = 'Reaction moment [N*m]' if 'RM' in y_label else 'Reaction force [N]'

    x_title = 'Deflection [mm]' if 'UR' in x_label else 'Rotation angle [rad]'

    tiff_file = '{}/{}_{}.tiff'.format(plot_dir,job_name,plot)

    csv_file = '{}/{}_{}.csv'.format(csv_dir,job_name,plot)

    # CREATING XY DATA FOR REACTION FORCE IN DIR 1

    xy0 = xyPlot.XYDataFromHistory(odb = odb, 
        outputVariableName='{}: {} PI: rootAssembly Node 1 in NSET {}'.format(force_type,y_label,nset), 
        steps=(step, ), suppressQuery=True, __linkedVpName__='Viewport: 1')

    session.XYData(name=y_label, objectToCopy=xy0, sourceDescription='abs({})'.format(y_label))
    del session.xyDataObjects[xy0.name]
            
    # CREATING XY DATA FOR DISPLACEMENT IN DIR 1

    xy0 = xyPlot.XYDataFromHistory(odb = odb, 
        outputVariableName='{}: {} PI: rootAssembly Node 1 in NSET {}'.format(displ_type,x_label,nset), 
        steps=(step, ), suppressQuery=True, __linkedVpName__='Viewport: 1')

    session.XYData(name=x_label, objectToCopy=xy0, sourceDescription='abs({})'.format(x_label))
    del session.xyDataObjects[xy0.name]

    # OPERATING ON XY DATA

    xy1 = session.xyDataObjects[x_label]
    xy2 = session.xyDataObjects[y_label]

    xy3 = combine(xy1, xy2)
    xy3.setValues(sourceDescription = 'combine ( "{}","{}" )'.format(x_label,y_label))
    tmpName = xy3.name
    session.xyDataObjects.changeKey(tmpName, '{} {} {} {}'.format(mode,inc,mat,plot))

    del session.xyDataObjects[xy1.name]
    del session.xyDataObjects[xy2.name]

    # GENERATING THE FINAL XY PLOT

    xyp = session.XYPlot('XYPlot-1')
    chartName = xyp.charts.keys()[0]
    chart = xyp.charts[chartName]
    xy_combo = session.xyDataObjects['{} {} {} {}'.format(mode,inc,mat,plot)]
            
    c1 = session.Curve(xyData = xy_combo)
    chart.setValues(curvesToPlot = (c1, ), )
    VPort.setValues(displayedObject = xyp)
    session.charts.items()[-1][1].axes1[0].axisData.setValues(useSystemTitle = False, 
        title = x_title)
    session.charts.items()[-1][1].axes2[0].axisData.setValues(useSystemTitle = False, 
        title = y_title)
    
    session.printToFile(fileName = tiff_file, format = TIFF, 
        canvasObjects = (VPort, ))

    output_lines = []

    output_lines.append('$' + ('%3.8f' %  max_mises) + DL + str(max_node) + NL)

    output_lines.append(x_title + DL + y_title + NL)

    for DataSet in xy_combo:

        output_lines.append(
            ('%3.8f' % DataSet[0]) #.replace('.', ',')
            + DL + 
            ('%3.8f' % DataSet[1]) #.replace('.', ',')
             + NL)

    output_lines.append('\n# END')
    
    with open(csv_file, 'w') as fres:

        for DataSet in output_lines:

            fres.write(DataSet)

    # PURGE XY DATA
    del session.xyDataObjects['{}_vs_{}_{}'.format(y_label,x_label,job_id)]
    del session.xyDataObjects[y_label]
    del session.xyDataObjects[x_label]
    del session.xyPlots['XYPlot-1']
    del session.charts['Chart-1']

def ClearXYData():
    
    getridkeys = session.xyDataObjects.keys()
    
    for i in range(0,len(getridkeys)):
        
        del session.xyDataObjects[getridkeys[i]]    

def GetMaxMises(inst, elset):
    
    maxMises = -1
    
    maxNode = -1

    xyList = session.xyDataListFromField(odb = odb,
                                         
        outputPosition = ELEMENT_NODAL,
        
        variable = (( 'S', INTEGRATION_POINT,((INVARIANT, 'Mises'),)), ),
        
        nodeSets = (inst.name + '.' + elset, ))

    for node in inst.nodes:
        
        XYPoint = 'S:Mises (Avg: 100%) PI: ' + inst.name + ' N: ' + str(node.label)
        
        avgMises = session.xyDataObjects[XYPoint].data[-1][1]
        
        if avgMises > maxMises: 
            
            maxMises = avgMises
            
            maxNode = node.label
            
    ClearXYData()

    return maxMises,maxNode

#########################################

cmd_line = ' '.join(sys.argv)

parser = AbqArgParse()

args = parser.parse()

if '-viewer' not in cmd_line and '-cae' not in cmd_line:

    pass

else:

    from abaqus import *
    from abaqusConstants import *
    from viewerModules import *
    from driverUtils import executeOnCaeStartup
    executeOnCaeStartup()
# TODO:
# then determine by absence of '-noGUI' in cmd_line that script is invoked from GUI, thus determine settings not from arguments but from the open model 

# write full command line and re-parsed arguments to the error log:
with open('error_log.txt', 'w') as ferr:

    ferr.write("Full command line: {}\n".format(cmd_line))

    ferr.write("job={}\n".format(args.job))

    # ferr.write("output={}\n".format(args.output))

    ferr.write("path={}\n".format(args.path))

    # ferr.write("start={}\n".format(args.start))

    # ferr.write("end={}\n".format(args.end))

ferr.close()

if not args.job:

   error_log("You must provide the job name template\n")

# job_dir = os.path.dirname(os.path.abspath(args.job))

job_dir, job_template = os.path.split(args.job) 

# job_template - beginning part of all study's files

# job_dir - the path where to search for the files to process

if args.path:

    if not os.path.isdir(args.path):

        error_log("Provided path does not exist\n")

    else:

        work_dir = args.path

else:

    work_dir = job_dir

# work_dir - the path where to store the resulting files. By default it's the same as job_dir

search_str = "^{}.+\.odb$".format(job_template)

base_template = os.path.basename(job_template)

files = [f_name for f_name in os.listdir(job_dir) if re.search(r'{}'.format(search_str), f_name)]

jobs_num = len(files)

if not jobs_num:

    error_log("No files found according to your template\n")

DL = '; '
	
NL = '\n'



plot_dir = work_dir + '/plots'

if not os.path.isdir(plot_dir):

    if not os.path.exists(plot_dir):

        os.makedirs(plot_dir)
    
    else:

        error_log("Delete the file called 'plots' from the working directory\n")

csv_dir = work_dir + '/data_sets'

if not os.path.isdir(csv_dir):

    if not os.path.exists(csv_dir):

        os.makedirs(csv_dir)
    
    else:

        error_log("Delete the file called 'data_sets' from the working directory\n")

mmises_dir = work_dir + '/maxmises'

if not os.path.isdir(mmises_dir):

    if not os.path.exists(mmises_dir):

        os.makedirs(mmises_dir)
    
    else:

        error_log("Delete the file called 'maxmises' from the working directory\n")

# fres.write( '# FULL RESULTS FOR ' + str(jobs_num) + ' STUDIES\n\n' )

for job_name in files:
    
    job_id = job_name.split(base_template,1)[1][:-4] # job_id - name of the job without the prefix
    
    odb_name = '/'.join((job_dir,job_name))

    job_name = job_name[:-4]

    error_log('Start processing job: {}\n'.format(job_name),False)

    prefix,mat,mode,inc,study = job_name.split('_',4)

    obj = session.openOdb(name = odb_name)
    
    odb = session.odbs[odb_name]

    assembly = odb.rootAssembly

    VPort = session.viewports['Viewport: 1']

    VPort.setValues(displayedObject = obj)

    VPort.view.setValues(session.views['Iso'])

    VPort.makeCurrent()

    VPort.maximize()

    VPort.view.setProjection(projection = PARALLEL)

    session.graphicsOptions.setValues(backgroundStyle = SOLID, 
        backgroundColor = '#FFFFFF')

    VPort.odbDisplay.commonOptions.setValues(
        visibleEdges = NONE)

    VPort.odbDisplay.display.setValues(plotState = (
        CONTOURS_ON_DEF, ))

    VPort.odbDisplay.basicOptions.setValues(
        averagingThreshold = 100)

    inst = assembly.instances['PART-1-1']

    max_mises,max_node = GetMaxMises(inst, 'WHOLE_CUBE')

    # Show SMISES:    

    VPort.odbDisplay.setPrimaryVariable(
        variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(INVARIANT, 
        'Mises'), )
        
    # Set MISES local MAX:

    VPort.odbDisplay.contourOptions.setValues(
        maxAutoCompute=ON, minAutoCompute=OFF, showMaxLocation=ON)
        # maxAutoCompute=ON, minAutoCompute=OFF, minValue = 40, showMaxLocation=ON)

    # Write to file:

    mmises_file = '{}/{}_max-mises.png'.format(mmises_dir,job_name)

    session.printToFile(fileName = mmises_file, format=PNG,
        canvasObjects=(VPort, ))

    if "tens" in job_name:

        get_xyplot('U2','RF2','RP_1','Step-1')

    if "compres" in job_name:

        get_xyplot('U2','RF2','RP_1','Step-1')

    elif "shear" in job_name:

        get_xyplot('U1','RF1','RP_1','Step-1')

        get_xyplot('U3','RF3','RP_1','Step-1')
    
    elif "complex" in job_name:

        get_xyplot('U1','RF1','RP_1','Step-1')

        get_xyplot('U2','RF2','RP_1','Step-1')

        get_xyplot('U3','RF3','RP_1','Step-1')

        get_xyplot('UR2','RM2','RP_1','Step-1')
    
    odb.close()

    error_log('Finish processing job: {}\n'.format(job_name),False)

error_log('All done\n',False)

# fres.close()
