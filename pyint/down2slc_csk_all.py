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


def get_csk_date(raw_file):
    file0 = os.path.basename(raw_file)
    date = file0[27:35]
    return date


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
    parser.add_argument('--parallel', dest='parallelNumb', type=int, default=1, help='Enable parallel processing and Specify the number of processors.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    start_time = time.time()
    inps = cmdLineParse() 
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    projectDir = scratchDir + '/' + projectName 
    downDir    = scratchDir + '/' + projectName + "/DOWNLOAD"
    raw_file_list = glob.glob(downDir + '/CSK*.tar.gz')
    
    # get the burst number table of the mater date
    
    date_list = []
    for kk in range(len(raw_file_list)):
        date0 = get_csk_date(os.path.basename(raw_file_list[kk]))
        date_list.append(date0)
        
    date_list = set(date_list)
    date_list = sorted(date_list)
    
    print('Date to be processed:')
    for k0 in date_list:
        print(k0)
    
    err_txt = scratchDir + '/' + projectName + '/down2slc_csk_all.err'
    if os.path.isfile(err_txt): os.remove(err_txt)
    
    data_para = []
    for i in range(len(date_list)):
        cmd0 = ['down2slc_csk.py',projectName,date_list[i]]
        data0 = [cmd0,err_txt]
        data_para.append(data0)
    
    ut.parallel_process(data_para, work, n_jobs=inps.parallelNumb, use_kwargs=False)
    os.chdir(downDir)
    print("Down to SLC for project %s is done! " % projectName)
    ut.print_process_time(start_time, time.time())
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
