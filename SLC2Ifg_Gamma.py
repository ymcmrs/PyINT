#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   Mar, 2017                                                  #
#                                                                                 #
#         SLC images to interferograms processing based on GAMMA                  #
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
 
           SLC images to interferograms processing based on GAMMA
     
      usage:
   
            SLC2Ifg_Gamma.py igramDir
      
      e.g.  SLC2Ifg_Gamma.py IFGRAM_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: igramDir=sys.argv[1]        
    else:
        usage();sys.exit(1)
        
    projectName = igramDir.split('_')[1]
    IFGPair = igramDir.split(projectName+'_')[1].split('_')[0]
    Mdate = IFGPair.split('-')[0]
    Sdate = IFGPair.split('-')[1]
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=readfile.read_template(templateFile)
    
    if 'COREG_Flag'          in templateContents: COREG_Flag = templateContents['COREG_Flag']                
    else: COREG_Flag = '1'
    
    if 'INT_Flag'          in templateContents: INT_Flag = templateContents['INT_Flag']                
    else: INT_Flag = '1'
        
    if 'DIFF_Flag'          in templateContents: DIFF_Flag = templateContents['DIFF_Flag']                
    else: DIFF_Flag = '1'
        
    if 'UNW_Flag'          in templateContents: UNW_Flag = templateContents['UNW_Flag']                
    else: UNW_Flag = '1'
        
    if 'GEO_Flag'          in templateContents: UNW_Flag = templateContents['GEO_Flag']                
    else: GEO_Flag = '1'    
    
    if 'coregMethod'          in templateContents: coregMethod = templateContents['coregMethod']                
    else: coregMethod = 'Init'

        
        
##############################################################

    if COREG_Flag == '1' :
        if coregMethod == "DEM":
            call_str = "CoregistSLC_DEM_Gamma.py " + igramDir
            os.system(call_str)
        else:
            call_str = "CoregistSLC_init_Gamma.py " + igramDir
            os.system(call_str)
    
    if INT_Flag == '1' :
        call_str = "GenIgram_Gamma.py " + igramDir
        os.system(call_str)        
    
    if DIFF_Flag == '1':
        call_str = "SimPhase_Gamma.py " + igramDir
        os.system(call_str)        
        call_str = "DiffPhase_Gamma.py " + igramDir
        os.system(call_str)
    
    if UNW_Flag == '1':
        call_str = "UnwPhase_Gamma.py " + igramDir
        os.system(call_str)    
    
    if GEO_Flag == '1':
        call_str = "Geocode_Gamma.py " + igramDir
        os.system(call_str)      
    
    print "SLC to interferogram done!"
    
    sys.exit(1)

#################################################################    
    
if __name__ == '__main__':
    main(sys.argv[:])

    
    
    
    
    
    
    
    
    
    
    
    