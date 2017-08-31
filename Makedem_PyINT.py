#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Central South University & University of Miami   ###   
#################################################################

import numpy as np
import os
import sys  
import subprocess
import getopt
import time
import glob
import argparse



def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

#########################################################################

INTRODUCTION = '''
##############################################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyINT v1.0   
   
   Generate dem automatically for GAMMA processing.
   
'''

EXAMPLE = '''
    Usage:
            Makedem_PyINT.py projectName processor
 
    Examples:
            Makedem_PyINT.py ShanghaiT171F96S1A gamma

###################################################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate dem automatically.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of the projection.')
    parser.add_argument('processor',help='Name of the processor. [gamma or roi_pac]')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
    
    inps = cmdLineParse()
    projectName = inps.projectName
    processor = inps.processor
    scratchDir = os.getenv('SCRATCHDIR')
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    KK=os.listdir(slcDir)
    
    SLCNM = []
    
    for ll in KK:
        if is_number(ll):
            SLCNM.append(ll)
    SLC_PAR = slcDir + '/' + SLCNM[0] + '/'+ SLCNM[0] + '.slc.par'
    
    demDir = os.getenv('DEMDIR') 
    os.chdir(demDir)
    call_str = 'mkdir ' + projectName
    os.system(call_str)
    
    demDir2 = demDir + '/' + projectName
    os.chdir(demDir2)
    
    call_str= 'makedem.py ' + '-s ' + SLC_PAR + ' -p ' + processor + ' -o ' + projectName
    os.system(call_str)
    
    print 'Generate DEM for project %s is done.' % projectName
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    