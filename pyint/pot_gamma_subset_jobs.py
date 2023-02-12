#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2022, Yunmeng Cao                   ###  
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

from pyint import _utils as ut


INTRODUCTION = '''
-------------------------------------------------------------------  
       Pixel offset tracking for co-registered Images. TOPs should be deramped in advance.
   
'''

EXAMPLE = '''
    Usage: 
            pot_gamma_subset_jobs.py projectName Mdate Sdate --memory memory_single_job --walltime walltime_single_job
            pot_gamma_subset_jobs.py PacayaT163TsxHhA 20150102 20150601 --memory 5000 --walltime 00:30:00
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Pixel offset tracking based Azimuth/Range dispalcement estimation.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('Mdate',help='Master date.')
    parser.add_argument('Sdate',help='Slave date.')
    parser.add_argument('--memory',dest = 'memory',default = '5000', help='memory to be allocated for one job, default: 5GB')
    parser.add_argument('--walltime',dest = 'walltime',default = '00:30:00', help='walltime to be allocated for one single job')
    inps = parser.parse_args()
    inps = parser.parse_args()
    return inps


def main(argv):
    
    start_time = time.time()
    inps = cmdLineParse() 
    Mdate = inps.Mdate
    Sdate = inps.Sdate
    
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    
    
    slcDir = scratchDir + '/' + projectName + '/SLC'
    rslcDir = scratchDir + '/' + projectName + '/RSLC'
    
    MrslcDir = rslcDir + '/' + Mdate
    SrslcDir = rslcDir + '/' + Sdate
    Pair = Mdate + '-' + Sdate
    batch_txt = scratchDir + '/' + projectName + '/ifgrams/' + Pair + '/Batch_POT'
    workDir = scratchDir + '/' + projectName + '/ifgrams/' + Pair
    if not os.path.isdir(workDir):
        os.mkdir(workDir)
    os.chdir(workDir)
    if os.path.isfile(batch_txt):
        os.remove(batch_txt)
    
    mrslc_list = glob.glob(MrslcDir + '/*_0*.rslc');mrslc_list.sort(); nn = len(mrslc_list)
    print('Total patch numbers: ' + str(nn))
    
    for i in range(nn):
        base0 = os.path.basename(mrslc_list[i]); subset1 = base0.split('_')[1]; subset0 = subset1.split('.rslc')[0]
        str0 = 'pot_gamma_subset.py ' + projectName + ' ' + Mdate + ' ' + Sdate + ' ' + subset0
        call_str = 'echo ' + str0 + ' >>' + batch_txt
        os.system(call_str)

    call_str = 'sbatch_jobs.py ' + batch_txt + ' --memory ' + inps.memory + ' --walltime ' + inps.walltime + ' --job-name ' + Pair + '_POT'
    os.system(call_str)
    

    print("Pixel offset tracking is Done!")
    ut.print_process_time(start_time, time.time())
    #sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
