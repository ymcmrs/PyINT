#! /usr/bin/env python
###########################################################
#  Project: PyINT                                         #     
#  Purpose: Interferograms process using python/GAMMA     #                                       
#  Author:  Yunmeng Cao                                   #
#  Created: Feb. 2017                                     #                                                         
#  Contact : ymcmrs@gmail.com                             #  
#  Copy Right (c): 2017-2019, Yunmeng Cao                 # 
###########################################################

import numpy as np
import os
import sys  
import subprocess
import time
import argparse

from pyint import _utils as ut


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Interferograms processing using PyINT.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='name of the project.')

    inps = parser.parse_args()
    return inps


INTRODUCTION = '''
-----------------------------------------------------------------------------------

   Single or time-series of interferometry processing for satellite based 
   Synthetic  Aperture  Radar (SAR) images start from downloading data to 
   generate unwrapped-differential interferograms.
   
   Details please check: https://github.com/ymcmrs/PyINT
   
   General work-flow: 
   
   1) download data  :  download SLCs using SSARA (please check https://github.com/bakerunavco/SSARA)
                        [You should provide Sensor, Track, Frame, or Time information in template]                     
   2) generate SLC   :  raw 2 slc (multi-frame processing is also supported)
                        [include orbit correction for S1,ASAR,ERS and burst-extraction for S1]                      
   3) generate DEM   :  reference image related geo-dem, rdc-dem, lookup table will be generated. 
                        [SRTM-1 will be downloaded and processed automatically if not provided]                       
   4) coregister SLC :  coregister SLCs to the reference SLC iamge.
                        [with assistant of DEM]  
   5) select pairs   :  select interferometric pairs for time-series processing.
                        [networks of sbas, sequential, delaunay, and stars are supported]                     
   6) interferometry :  generate unwrapped differential interferograms.
                        [include differential, unwrapping, and geocoding]
                         
   Note: 
   
   i) Single interferogram processing please use slc2ifg.py or raw2ifg.py
  ii) Multi-processor parallel processing is supported, but keep in mind GAMMA calls multi-threads already.
                      
'''

EXAMPLE = """Usage:
        
        pyintApp.py -h
        pyintApp.py projectName       #[projectName.template should be available in TEMPLATEDIR]

------------------------------------------------------------------------------------ 
"""

def main(argv):
    
    start_time = time.time()
    inps = cmdLineParse()
    projectName = inps.projectName
    templateDir = os.getenv('TEMPLATEDIR')
    scratchDir = os.getenv('SCRATCHDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict = ut.update_template(templateFile)
    masterDate = templateDict['masterDate']
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    HGTSIM = scratchDir + '/' + projectName + '/DEM/' + ut.yyyymmdd(masterDate) + '_' + rlks + 'rlks.rdc.dem' 
    
    ### download data
    
    if templateDict['download_data'] == '1':
        call_str = 'ssara_federated_query.py -p ' +  templateDict['sensor'] + ' -r ' + templateDict['track'] + ' -f ' + templateDict['frame'] + ' -s ' + templateDict['start_time'] + ' -e ' + templateDict['end_time'] + ' --print --download --parallel ' + templateDict['down_parallel']
        os.system(call_str)
        
    ### raw 2 slc 
    if templateDict['raw2slc_all'] == '1':   # only for S1 data now
        call_str = 'down2slc_sen_all.py ' + projectName + ' --parallel ' + templateDict['raw2slc_all_parallel']
        os.system(call_str)
        
    ### extract bursts  
    if templateDict['extract_burst_all'] == '1':
        call_str = 'extract_s1_bursts_all.py ' + projectName + ' --parallel ' + templateDict['extract_all_parallel']
        os.system(call_str)
        
    ### generate rdc_dem
    if not os.path.isfile(HGTSIM):
        call_str = 'generate_rdc_dem.py ' + projectName 
        os.system(call_str)
    
    ### coreg SLC  
    if templateDict['coreg_all'] == '1':
        call_str = 'coreg_gamma_all.py ' + projectName + ' --parallel ' + templateDict['coreg_all_parallel']
        os.system(call_str)
    
    ### select interferometric pairs 
    if templateDict['select_pairs'] == '1':
        call_str = 'select_pairs.py ' + projectName
        os.system(call_str)
    
    ### diff ifg
    if templateDict['diff_all'] == '1':
        call_str = 'diff_gamma_all.py ' + projectName + ' --parallel ' + templateDict['diff_all_parallel']
        os.system(call_str)
    
    ### unw ifg
    if templateDict['unwrap_all'] == '1':
        call_str = 'unwrap_gamma_all.py ' + projectName + ' --parallel ' + templateDict['unwrap_all_parallel']
        os.system(call_str)
        
    ### geocode ifg
    if templateDict['geocode_all'] == '1':
        call_str = 'geocode_gamma_all.py ' + projectName + ' --parallel ' + templateDict['geocode_all_parallel']
        os.system(call_str)
        
    ### load data
    if templateDict['load_data'] == '1':
        call_str = 'load_data_pyint.py ' + projectName
        os.system(call_str)
    
    print("PyINT processing for project %s is done." % projectName)
    ut.print_process_time(start_time, time.time()) 
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
