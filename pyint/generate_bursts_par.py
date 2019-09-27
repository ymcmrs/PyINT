#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################

import numpy as np
import os
import sys  
import glob
import argparse

from pyint import _utils as ut



INTRODUCTION = '''
-------------------------------------------------------------------  

   Generate burst par files for a project.
'''

EXAMPLE = """Usage:
  
  generate_bursts_par.py projectName
  
------------------------------------------------------------------- 
"""

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Check common busrts for TOPS data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of project.')

    inps = parser.parse_args()

    return inps

################################################################################    
    
    
def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
           
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    Mdate =  templateDict['masterDate']
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir     = scratchDir + '/' + projectName + "/RSLC"
    dateList = ut.get_project_slcList(slcDir)
    
    for i in range(len(dateList)):
        slc_dir = slcDir + '/' + dateList[i]
            for j in range(3):
                SLC    = slc_dir + '/' + dateList[i] + '.IW' + str(kk+1)+'.slc'
                SLCPar = slc_dir + '/' + dateList[i] + '.IW' + str(kk+1)+'.slc.par'
                TOPPar = slc_dir + '/' + dateList[i] + '.IW' + str(kk+1)+'.slc.TOPS_par'
                BURST = slc_dir + '/' + dateList[i] + '.IW' + str(kk+1)+'.burst.par'
                
                call_str = 'SLC_burst_corners ' + SLCPar + ' ' +  TOPPar + ' > ' +BURST
                os.system(call_str)
                
                
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
