#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ###
###  Purpose: loading PyINT products for mintPy               ###
###  Copy Right (c): 2019, Yunmeng Cao                        ###  
###  Author  : Yunmeng Cao                                    ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################

import numpy as np
import os
import sys  
import subprocess
import time
import argparse
import glob

from pyint import _utils as ut
        

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Loading pyint products for mintPy time-series analysis.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='name of the project.')  
    parser.add_argument('--data-type', dest='dataType', type=str, default='big_endian',choices={'big_endian', 'little_endian'},
                        help='data type, big endian or little endian. [default: big_endian]')
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
--------------------------------------------------------------------------------------
   Loading pyint products for mintPy time-series analysis.
   
'''

EXAMPLE = """Usage:
  
        load_mintpy.py projectName
        load_mintpy.py projectName --data-type little_endian
--------------------------------------------------------------------------------------- 
"""

def main(argv):
    
    inps = cmdLineParse()
    projectName = inps.projectName
    dataType = inps.dataType
    
    projectDir = scratchDir + '/' + projectName 
    demDir    = scratchDir + '/' + projectName  + '/DEM'
    rslcDir   = scratchDir + '/' + projectName + '/RSLC' 
     
    ifgDir = projectDir + '/ifgrams'
    
    date_list = ut.get_project_slcList(projectName)
    amp_par_list = glob.glob(rslcDir + '/*/*rlks.amp.par')
    
    date_list = sorted(date_list)
    amp_par_list = sorted(amp_par_list)
    
    slc_par_list = glob.glob(rslcDir + '/*/*.rslc.par')
    
    unw_list = glob.glob(ifgDir + '/*/*rlks.diff_filt.unw')
    cor_list = glob.glob(ifgDir + '/*/*rlks.diff_filt.cor')
    
    dem_geo  = glob.glob(demDir + '/*rlks.utm.dem')[0]
    geo_par  = glob.glob(demDir + '/*rlks.utm.dem.par')[0]  
    
    dem_rdc  = glob.glob(demDir + '/*rlks.rdc.dem')[0]
    rdc_par  = glob.glob(demDir + '/*rlks.diff_par')[0]       # diff_par
    
    
    
        
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    