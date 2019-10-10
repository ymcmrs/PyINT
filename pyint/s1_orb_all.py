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
import getopt
import time
import glob
import argparse

import subprocess
from pyint import _utils as ut


def work(data0):
    cmd = data0[0]
    err_txt = data0[1]
    
    p = subprocess.run(cmd, shell=False,stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout = p.stdout
    stderr = p.stderr
    
    if type(stderr) == bytes:
        aa=stderr.decode("utf-8")
    else:
        aa = stderr
        
    if aa:
        str0 = cmd[0] + ' ' + cmd[1] + ' ' + cmd[2] + '\n'
        #print(aa)
        with open(err_txt, 'a') as f:
            f.write(str0)
            f.write(aa)
            f.write('\n')

    return 
#########################################################################

INTRODUCTION = '''
-------------------------------------------------------------------  
       Using precise orbit data for all rslcs.
   
'''

EXAMPLE = '''
    Usage: 
            generate_amp_all.py projectName
            generate_amp_all.py projectName --parallel 4
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Using precise orbit data for all rslcs.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('--parallel', dest='parallelNumb', type=int, default=1, help='Enable parallel processing and Specify the number of processors.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    start_time = time.time()
    inps = cmdLineParse() 
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    projectDir = scratchDir + '/' + projectName 
    slcDir    = scratchDir + '/' + projectName + '/SLC'
    rslcDir    = scratchDir + '/' + projectName + '/RSLC'   
    if not os.path.isdir(rslcDir): os.mkdir(rslcDir)
    
    cmd_command = 'generate_multilook_amp.py'
        
    err_txt = scratchDir + '/' + projectName + '/generate_amp_all.err'
    if os.path.isfile(err_txt): os.remove(err_txt)
    
    data_para = []
    slc_list = [os.path.basename(fname) for fname in sorted(glob.glob(rslcDir + '/*'))]
    #slc_list = ut.get_project_slcList(projectName)
    for i in range(len(slc_list)):
        rslcPar = rslcDir + '/' + slc_list[i] + '/' + slc_list[i] + '.rslc.par'
        #print(rslcPar)
        workDir0 = rslcDir + '/' + slc_list[i]
        Sensor = ut.read_gamma_par(rslcPar,'read','sensor')
        if 'A' in Sensor: satellite = 'A'
        else: satellite = 'B'
        ut.download_s1_orbit(slc_list[i],workDir0,satellite=satellite)
        
        BB = glob.glob(workDir0 + '/*.EOF')
        if len(BB) > 0:
            orb_file = BB[0]
            
            call_str = 'S1_OPOD_vec ' + rslcPar + ' ' + orb_file + ' 31'
            os.system(call_str)

    print("Using precise orbit data for all rslcs is done! ")
    ut.print_process_time(start_time, time.time())
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    