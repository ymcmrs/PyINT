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
import subprocess
import getopt
import time
import glob
import argparse

from pyint import _utils at ut
#########################################################################

INTRODUCTION = '''
-------------------------------------------------------------------  
   
       Generate SLCs from Sentinel-1 raw dataset with orbit correction using GAMMA.
   
'''

EXAMPLE = '''
    Usage: 
            down2slc_sen_all.py projectName
            down2slc_sen_all.py projectName --parallel 4
 
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate SLCs from Sentinel-1 raw dataset with orbit correction using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    
    
    inps = parser.parse_args()
    return inps


def main(argv):
    inps = cmdLineParse() 
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    projectDir = scratchDir + '/' + projectName 
    downDir    = scratchDir + '/' + projectName + "/DOWNLOAD"

    
    os.chdir(downDir)
    
    call_str = 'ls  > ttt0'
    os.system(call_str)
    
    
    call_str = 'grep .zip ttt0 > ttt'
    os.system(call_str)
    ZIP = np.loadtxt('ttt',dtype = np.string_)
    N = ZIP.size
    DATE = []
    
    if N>1:
        for i in range(N):
            RAWNAME = ZIP[i].decode("utf-8")
            Date = RAWNAME[19:25]
            if (not (Date in DATE)) and len(Date)>0:
                DATE.append(Date) 
                
    call_str = 'grep SAFE ttt0 > ttt'
    os.system(call_str)
    SAFE = np.loadtxt('ttt',dtype  = np.string_)
    N = SAFE.size
    
    if N >1:
        for i in range(N):
            RAWNAME = SAFE[i].decode("utf-8")
            Date = RAWNAME[19:25]
            if (not (Date in DATE)) and len(Date)>0:
                DATE.append(Date) 
    
    N = len(DATE)
    
    run_down2slc_sen = downDir + '/run_down2slc_sen'
    f_down2slc =open(run_down2slc_sen,'w')
    
    for i in range(N):
        str_script = 'Down2SLC_Sen_Gamma.py ' + projectName + ' ' + DATE[i] + '\n'
        f_down2slc.write(str_script)
        print('Add download raw S1 data: ' + DATE[i])
    f_down2slc.close()
    
    print('')
    print('Start processing down2sl for project: ' + projectName)
    
    #call_str='$INT_SCR/createBatch.pl ' + run_down2slc_sen + ' memory=7000  walltime=0:30'
    #os.system(call_str)
    
    call_str='process_loop_runfile.py ' + run_down2slc_sen
    os.system(call_str)
    
    
    print("Down to SLC for project %s is done! " % projectName)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
