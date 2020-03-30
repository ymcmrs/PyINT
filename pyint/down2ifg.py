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

import datetime as dt
from dateutil.relativedelta import relativedelta

from pyint import _utils as ut

def get_e_s_date(date):
    date = str(date)
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    
    org_date = dt.date(day=int(day), month=int(month), year=int(year))
    sdate = org_date - relativedelta(days=1)
    edate = org_date + relativedelta(days=1)
    
    return sdate, edate

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
   Generate unwrapped differential Ifg from downloading Sentinel-1 raw data with orbit correction using GAMMA.
   
   Note: 1) Precise orbit data will be downloaded and processed automatically
         2) SRTM-1 will be downloaded and processed automatically if not provided 
            in the template file
         3) SSARA is used 

'''

EXAMPLE = """Usage:
  
        down2ifg.py projectName Mdate Sdate
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
    
    track = templateDict['track']
    frame = templateDict['frame']
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    masterDate = templateDict['masterDate']
    projectDir = scratchDir + '/' + projectName
    downDir = scratchDir + '/' + projectName + '/DOWNLOAD'
    slcDir    = scratchDir + '/' + projectName + '/SLC'
    
    ######### download data ############
    print('Start to download data ...')
    
    if not os.path.isdir(projectDir):
        os.mkdir(projectDir)
    if not os.path.isdir(downDir): 
        os.mkdir(downDir)
        
    os.chdir(downDir)
    call_str = 'ssara_federated_query.py -p Sentinel-1A,Sentinel-1B -r ' + track + ' -f ' + frame + ' --date ' + Mdate + ',' + Sdate + ' --print --download --parallel 10'
    print(call_str)
    os.system(call_str)
    
    ######### down 2 slc #############
    #M_raw = glob.glob(downDir + '/S1*_' + ut.yyyymmdd(Mdate)+'*')[0]
    #S_raw = glob.glob(downDir + '/S1*_' + ut.yyyymmdd(Sdate)+'*')[0]
    
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
    
    
    
    
    
    
