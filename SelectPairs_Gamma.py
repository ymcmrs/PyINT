#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   Mar, 2017                                                  #
#                                                                                 #
#         Select Interferometry-Pairs from time series SAR images                  #
#                                                                                 #
###################################################################################
#'''
import numpy as np
import os
import pysar._readfile as readfile
import sys  
import subprocess
import getopt
import time
import glob


def usage():
    print '''
******************************************************************************************************
 
           Select interferometry pairs from time series SAR images
     
      usage:
   
            SelectPairs_Gamma.py ProjectName
      
      e.g.  SelectPairs_Gamma.py PacayaT163TsxHhA
          
            
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: ProjectName=sys.argv[1]        
    else:
        usage();sys.exit(1)
        
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=readfile.read_template(templateFile)
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    
    SLCfile=glob.glob(slcDir+'/*/*.slc')  
    SLCParfile =glob.glob(slcDir+'/*/*.slc.par')  
    
    print SLCParfile
    
    
    
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])

    
