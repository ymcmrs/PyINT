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
    err_file = data0[1]
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
        with open(err_file, 'a') as f:
            f.write(str0)
            f.write(aa)
            f.write('\n')

    return 
#########################################################################

INTRODUCTION = '''
-------------------------------------------------------------------  
       Extract reference TOPS related bursts for coregistration using GAMMA.
   
'''

EXAMPLE = '''
    Usage: 
            extract_s1_bursts_all.py projectName
            extract_s1_bursts_all.py projectName --parallel 4
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Extract reference TOPS related bursts for coregistration using GAMMA.',\
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
    slc_list = [os.path.basename(fname) for fname in sorted(glob.glob(slcDir + '/*'))]
    
    err_txt = scratchDir + '/' + projectName + '/extract_s1_bursts_all.err'
    if os.path.isfile(err_txt): os.remove(err_txt)
    
    data_para = []
    for i in range(len(slc_list)):
        cmd0 = ['extract_s1_bursts.py',projectName,slc_list[i]]
        data0 = [cmd0,err_txt]
        data_para.append(data0)
    
    ut.parallel_process(data_para, work, n_jobs=inps.parallelNumb, use_kwargs=False)
    print("Extract TOPS bursts for project %s is done! " % projectName)
    ut.print_process_time(start_time, time.time())
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    