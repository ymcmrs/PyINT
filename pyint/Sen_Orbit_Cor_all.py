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

def StrNum(S):
    S = str(S)
    if len(S)==1:
        S='0' +S
    return S

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
   
   Download and update the orbit data of Sentinel-1A/B slc par files for the whole project based on the AUX_POEORB data.
   See also:  Sen_PreOrbit.py, Update_Orbit_Sen.py and Sen_Orbit_Cor.py.
   
'''

EXAMPLE = '''
    Usage:
            Sen_Orbit_Cor_all.py projectName
 
    Examples:
            Sen_Orbit_Cor_all.py projectName

###################################################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Correct orbit data for all of the Sentinel-1 data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of the projection.')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
    
    inps = cmdLineParse()
    projectName = inps.projectName
    
    scratchDir = os.getenv('SCRATCHDIR')
    slcDir     = scratchDir + '/' + projectName + "/SLC" 
    SAR = os.listdir(slcDir)
    if os.path.isfile('run_Sen_OrbCor'):
        call_str = 'rm run_Sen_OrbCor'
        os.system(call_str)
    
    for kk in SAR:
        if is_number(kk):
            call_str ='echo Sen_Orbit_Cor.py ' + projectName + ' ' + kk + ' >> run_Sen_OrbCor' 
            os.system(call_str)
    
    call_str = 'rm job*'
    os.system(call_str)
    
    call_str = 'rm z_out*'
    os.system(call_str)
    
    
    call_str = '$INT_SCR/createBatch.pl run_Sen_OrbCor memory=3700 walltime=0:30'
    os.system(call_str)
    
    
    print 'Correct the orbit for project %s is done.' % projectName
    
if __name__ == '__main__':
    main(sys.argv[:])
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
