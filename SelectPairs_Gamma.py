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


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
    

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
        else: projectName=sys.argv[1]        
    else:
        usage();sys.exit(1)
        
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=readfile.read_template(templateFile)
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    
    ListSLC = os.listdir(slcDir)
    Datelist = []
    SLCfile = []
    
    print "All of the available SAR acquisition date is :"  
    for kk in range(len(ListSLC)):
        if is_number(ListSLC[kk]):
            Datelist.append(ListSLC[kk])
            print ListSLC[kk]
            str_slc = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc"
            str_slc_par = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc.par"
            SLCfile.append(str_slc)
            SLCParfile.append(str_slc_par)
    

    File= open('base_calc_txt','w')
    
    for kk in range(len(SLCfile)):
        File.write(str(SLCfile[kk])+ ' '+str(SLCParfile[kk])+'\n')
        
        
    print SLCfile[1]
    print SLCParfile[1]
    
    
    
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])

    
