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
    parser = argparse.ArgumentParser(description='Generate SLC from Sentinel-1 raw data with orbit correction using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='project name. e.g., ChangningT55S1A')
    parser.add_argument('date',help='date to be processed. e.g., 20180101')
       
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  

   Generate SLC from Sentinel-1 raw data using S1_import_SLC_from_zipfiles with orbit correction.
   [Precise orbit data will be downloaded automatically]
'''

EXAMPLE = """Usage:
  
  down2slc_sen.py projectName date
  
  down2slc_sen.py ChangningT55S1A 20180517
  
------------------------------------------------------------------- 
"""

def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
    date = inps.date
    scratchDir = os.getenv('SCRATCHDIR')
    projectDir = scratchDir + '/' + projectName 
    
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    
    Mdate = templateDict['masterDate']
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    
    slc_dir =  projectDir + '/SLC'
    rslc_dir =  projectDir + '/RSLC'
    down_dir = projectDir + '/DOWNLOAD'
    opod_dir = projectDir + '/OPOD'
    
    if not os.path.isdir(slc_dir):
        os.mkdir(slc_dir)
    if not os.path.isdir(opod_dir):
        os.mkdir(opod_dir)
        
    work_dir = slc_dir + '/' + date
    if not os.path.isdir(work_dir):
        os.mkdir(work_dir)
    
    os.chdir(work_dir)
    master_burst_numb = down_dir + '/master.burst_numb_table'
    if not os.path.isfile(master_burst_numb):
        call_str = 'get_master_burst_numb.py ' + projectName
        os.system(call_str)
        
    
    t_date = 't_' + date
    
    call_str = 'ls ' + down_dir + '/S1*' + date + '*.zip > ' + t_date
    os.system(call_str)
  
    start_swath = templateDict['start_swath']
    end_swath = templateDict['end_swath']
    
    
    if (start_swath == '1') and (end_swath == '1'):
        k_swath = '1'
    elif (start_swath == '2') and (end_swath == '2'):
        k_swath = '2'
    elif (start_swath == '3') and (end_swath == '3'):
        k_swath = '3'
    elif (start_swath == '1') and (end_swath == '2'):
        k_swath = '4'
    elif (start_swath == '2') and (end_swath == '3'):
        k_swath = '5' 
    elif (start_swath == '1') and (end_swath == '3'):
        k_swath = '0' 
    
    
    raw_files = ut.read_txt2list(t_date)
    satellite = get_satellite(raw_files[0])
    
    orbit_file = ut.download_s1_orbit(date,opod_dir,satellite=satellite)
    
    kml_list = glob.glob(work_dir + '/*IW*.kml') 
    if not len(kml_list) > 0:
        call_str = 'S1_import_SLC_from_zipfiles ' + t_date + ' ' + master_burst_numb + ' vv 0 ' + k_swath + ' ' + opod_dir + ' 1 1 '
        os.system(call_str)
        
        os.chdir(work_dir)
    
        call_str = "rename 's/vv.slc.iw1/IW1.slc/g' *"
        os.system(call_str)
        call_str = "rename 's/vv.slc.iw2/IW2.slc/g' *"
        os.system(call_str)
        call_str = "rename 's/vv.slc.iw3/IW3.slc/g' *"
        os.system(call_str)
    
        call_str = "rename 's/.tops_par/.TOPS_par/g' *"
        os.system(call_str)
    
        SLC_Tab = work_dir + '/' + date+'_SLC_Tab'
        RSLC_Tab = work_dir + '/' + date+'_RSLC_Tab'
    
        SLC_list = glob.glob(work_dir + '/*IW*.slc') 
        SLC_par_list = glob.glob(work_dir + '/*IW*.slc.par') 
        TOP_par_list = glob.glob(work_dir + '/*IW*.slc.TOPS_par') 
    
        if os.path.isfile(SLC_Tab):
            os.remove(SLC_Tab)
        if os.path.isfile(RSLC_Tab):
            os.remove(RSLC_Tab)
    
        SLC_list = sorted(SLC_list)
        SLC_par_list = sorted(SLC_par_list)
        TOP_par_list = sorted(TOP_par_list)
     
        for kk in range(len(SLC_list)):
            call_str = 'echo ' + SLC_list[kk] + ' ' + SLC_par_list[kk] + ' ' + TOP_par_list[kk] + ' >> ' + SLC_Tab
            os.system(call_str)
        
            call_str = 'echo ' + rslc_dir + '/' + date + '/' + os.path.basename(SLC_list[kk]).replace('.slc','.rslc') + ' ' + rslc_dir + '/' + date + '/'+ os.path.basename(SLC_par_list[kk]).replace('.slc','.rslc') + ' ' + rslc_dir + '/' + date + '/' + os.path.basename(TOP_par_list[kk]).replace('.slc','.rslc') + ' >> ' + RSLC_Tab
            os.system(call_str)
        
            BURST = SLC_par_list[kk].replace('slc.par','burst.par')
            KML = SLC_par_list[kk].replace('slc.par','kml')
            call_str = 'ScanSAR_burst_corners ' + SLC_par_list[kk] + ' ' +  TOP_par_list[kk] + ' ' + KML + ' > ' +BURST
            os.system(call_str)
        
        if date == Mdate:
            TSLC = workDir + '/' + date + '.slc'
            TSLCPar = workDir + '/' + date + '.slc.par'
    
            call_str = 'SLC_mosaic_S1_TOPS ' +  SLC_Tab + ' ' + TSLC + ' ' + TSLCPar + ' ' + rlks + ' ' + azlks
            os.system(call_str)
        
        
        
    
    print("Down to SLC for %s is done! " % date)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
