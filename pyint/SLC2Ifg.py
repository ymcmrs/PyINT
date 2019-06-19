#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
###  Copy Right (c): 2018, Yunmeng Cao                        ###  
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

    
    
def usage():
    print('''
******************************************************************************************************
 
       Coregistration of SAR images based on cross-correlation by using GAMMA.
       Be suitable for conventional InSAR, MAI, Range Split-Spectrum InSAR.

   usage:
   
            SLC2Ifg.py IfgramDir
      
      e.g.  SLC2Ifg.py IFG_MexicoCityT143F529S1D_20180506-20180518_034_048
           
*******************************************************************************************************
    ''')   
    
        
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: igramDir=sys.argv[1]        
    else:
        usage();sys.exit(1)
    
    projectName = igramDir.split('_')[1]
    
    if 'S1' in projectName:
        call_str='SLC2Ifg_Sen_Gamma.py ' + ifgramDir
    else:
        call_str='SLC2Ifg_Gamma.py ' + ifgramDir
        
    os.system(call_str)
            
if __name__ == '__main__':
    main(sys.argv[:])
