#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Central South University & University of Miami   ###   
#################################################################

import numpy as np
import os
import sys  
import subprocess
import getopt
import time
import glob
import datetime

    
    
def usage():
    print('''
******************************************************************************************************
 
       Process run_files by using a loop

   usage:
   
            process_loop_runfile.py run_file
      
      e.g.  process_loop_runfile.py /SCRATCH/run_down2slc_sen
            process_loop_runfile.py /SCRATCH/run_slc2ifg_sen
           
*******************************************************************************************************
    ''')   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: run_file=sys.argv[1]        
    else:
        usage();sys.exit(1)
        
    starttime = datetime.datetime.now()
    f=open(run_file,'r')
    ll=f.read().splitlines() 
    f.close()
    
    N = len(ll)
    for i in range(N):
        str_print = str(i) + ' ' + ll[i]
        print(str_print)
        call_str=ll[i] + ' >/dev/null'    # don't show output
        os.system(call_str)
        
    endtime = datetime.datetime.now()
    print (endtime - starttime)
    
if __name__ == '__main__':
    main(sys.argv[:])



















