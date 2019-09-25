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
import argparse

from pyint import _utils as ut
        

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate unwrapped differential Ifg from SLC-raw data using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='name of the project.')
    parser.add_argument('Mdate',help='master date for interferometry.')
    parser.add_argument('Sdate',help='slave date for interferometry.')
       
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
--------------------------------------------------------------------------------------
   Generate unwrapped differential Ifg from SLC-raw data using GAMMA. 
   
   Note: 1) Precise orbit data will be downloaded and processed automatically
         2) SRTM-1 will be downloaded and processed automatically if not provided 
            in the template file.

'''

EXAMPLE = """Usage:
  
        raw2ifg.py projectName Mdate Sdate
--------------------------------------------------------------------------------------- 
"""

def main(argv):
    
    inps = cmdLineParse()
    Mdate = inps.Mdate
    Sdate = inps.Sdate
    
    projectName = inps.projectName
    
    if 'S1' in projectName:
        call_str = 'raw2ifg_s1.py ' + projectName + ' ' + ut.yyyymmdd(Mdate) + ' ' + ut.yyyymmdd(Sdate)
        os.system(call_str)
        
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
