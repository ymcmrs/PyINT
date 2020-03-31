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
import time
import glob
import argparse

from pyint import _utils as ut


def get_s1_date(raw_file):
    file0 = os.path.basename(raw_file)
    date = file0[17:25]
    return date

def get_satellite(raw_file):
    if 'S1A_IW_SLC_' in raw_file:
        s0 = 'A'
    else:
        s0 = 'B'
    
    return s0
        

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate Ifg from Sentinel-1 raw data with orbit correction using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='name of the project.')
    parser.add_argument('Mdate',help='master date for interferometry.')
    parser.add_argument('Sdate',help='slave date for interferometry.')
       
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
---------------------------------------------------------------------------------------------------
   Generate unwrapped differential Ifg from Sentinel-1 raw data with orbit correction using GAMMA.
   
   Note: 1) Precise orbit data will be downloaded and processed automatically
         2) SRTM-1 will be downloaded and processed automatically if not provided 
            in the template file.

'''

EXAMPLE = """Usage:
  
        raw2ifg_s1.py projectName Mdate Sdate
---------------------------------------------------------------------------------------------------- 
"""

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
    
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    masterDate = templateDict['masterDate']
    downDir = scratchDir + '/' + projectName + '/DOWNLOAD'
    #M_raw = glob.glob(downDir + '/S1*_' + ut.yyyymmdd(Mdate)+'*')[0]
    #S_raw = glob.glob(downDir + '/S1*_' + ut.yyyymmdd(Sdate)+'*')[0]
    slcDir    = scratchDir + '/' + projectName + '/SLC'
    
    
    ######### down 2 slc #############
    call_str = 'down2slc_sen.py ' + projectName + ' ' + Mdate
    os.system(call_str)
    
    call_str = 'down2slc_sen.py ' + projectName + ' ' + Sdate
    os.system(call_str)
    
    ########## extract common bursts ##
    #call_str = 'extract_s1_bursts.py ' + projectName + ' ' + Mdate
    #os.system(call_str)
    
    #call_str = 'extract_s1_bursts.py ' + projectName + ' ' + Sdate
    #os.system(call_str)
    
    ######### generate rdc_dem ##########
    demDir = scratchDir + '/' + projectName + '/DEM'
    HGTSIM      = demDir + '/' + masterDate + '_' + rlks + 'rlks.rdc.dem'
    if not os.path.isfile(HGTSIM):
        call_str = 'generate_rdc_dem.py ' + projectName
        os.system(call_str)
    
    ########## coregister SLC ########
    
    call_str = 'coreg_s1_gamma.py ' + projectName + ' ' + Mdate
    os.system(call_str)
    
    call_str = 'coreg_s1_gamma.py ' + projectName + ' ' + Sdate
    os.system(call_str)
    
    ######## Interferometry process ###########
    call_str = 'diff_gamma.py ' + projectName + ' ' + Mdate + ' ' + Sdate
    os.system(call_str)
    
    call_str = 'unwrap_gamma.py ' + projectName + ' ' + Mdate + ' ' + Sdate
    os.system(call_str)
    
    call_str = 'geocode_gamma.py ' + projectName + ' ' + Mdate + '-' + Sdate
    os.system(call_str)

    print("Generate Ifg from raw-TOPs data is done! ")
    ut.print_process_time(start_time, time.time()) 
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
