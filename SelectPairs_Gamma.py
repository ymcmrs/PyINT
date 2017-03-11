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

# define files    
    
    SLC_Tab = processDir + "/SLC_Tab"
    TS_Berp = processDir + "/TS_Berp"
    TS_Itab = processDir + "/TS_Itab"
    itab_type = '1'
    pltflg = '0'
    
    if 'Max_Spacial_Baseline'  in templateContents: MaxSB=templateContents['Max_Spacial_Baseline']
    else:
        print "Max_Spacial_Baseline is not found in template!! "
        print "500m is chosen as the threshold for spatial baseline!"
        MaxSB = '500'
        
    if 'Max_Temporal_Baseline'  in templateContents: MaxTB=templateContents['Max_Temporal_Baseline']
    else:
        print "Max_Temporal_Baseline is not found in template!! "
        print "500 days is chosen as the threshold for temporal baseline!"
        MaxTB = '500'
    
    
#  extract available SAR images slc and slc_par    
    ListSLC = os.listdir(slcDir)
    Datelist = []
    SLCfile = []
    SLCParfile = []
    
    print "All of the available SAR acquisition datelist is :"  
    for kk in range(len(ListSLC)):
        if is_number(ListSLC[kk]):
            Datelist.append(ListSLC[kk])
            print ListSLC[kk]
            str_slc = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc"
            str_slc_par = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc.par"
            SLCfile.append(str_slc)
            SLCParfile.append(str_slc_par)
    
    if 'masterDate'          in templateContents:
        masterDate0 = templateContents['masterDate']
        if masterDate0 in Datelist:
            masterDate = masterDate0
            print "masterDate : " + masterDate0
        else:
            masterDate=Datelist[0]
            print "The selected masterDate is not included in above datelist !!"
            print "The first date [ %s ] is chosen as the master date! " % Datelist[0] 
            
    else:  
        masterDate=Datelist[0]
        print "masterDate is not found in template!!! "
        print "The first date [ %s ] is chosen as the master date! " % Datelist[0] 

    RefPar=slcDir + "/" + masterDate +"/" + masterDate + ".slc.par"
       
    File= open(SLC_tab,'w')
    
    for kk in range(len(SLCfile)):
        File.write(str(SLCfile[kk])+ ' '+str(SLCParfile[kk])+'\n')
        
    File.close()
     
    call_str = "$GAMMA_BIN/base_calc " + SLC_tab + " " + RefPar + " " + TS_Berp + " " + TS_Itab + " " + '1 0 ' + '- ' + MaxSB + ' - ' + MaxTB
    os.system(call_str)

      
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])

    
