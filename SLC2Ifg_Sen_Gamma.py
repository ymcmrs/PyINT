
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

def check_variable_name(path):
    s=path.split("/")[0]
    if len(s)>0 and s[0]=="$":
        p0=os.getenv(s[1:])
        path=path.replace(path.split("/")[0],p0)
    return path

def read_template(File, delimiter='='):
    '''Reads the template file into a python dictionary structure.
    Input : string, full path to the template file
    Output: dictionary, pysar template content
    Example:
        tmpl = read_template(KyushuT424F610_640AlosA.template)
        tmpl = read_template(R1_54014_ST5_L0_F898.000.pi, ':')
    '''
    template_dict = {}
    for line in open(File):
        line = line.strip()
        c = [i.strip() for i in line.split(delimiter, 1)]  #split on the 1st occurrence of delimiter
        if len(c) < 2 or line.startswith('%') or line.startswith('#'):
            next #ignore commented lines or those without variables
        else:
            atrName  = c[0]
            atrValue = str.replace(c[1],'\n','').split("#")[0].strip()
            atrValue = check_variable_name(atrValue)
            template_dict[atrName] = atrValue
    return template_dict


def ras2jpg(input, strTitle):
    call_str = "convert " + input + ".ras " + input + ".jpg"
    os.system(call_str)
    call_str = "convert " + input + ".jpg -resize 250 " + input + ".thumb.jpg"
    os.system(call_str)
    call_str = "convert " + input + ".jpg -resize 500 " + input + ".bthumb.jpg"
    os.system(call_str)
    call_str = "$INT_SCR/addtitle2jpg.pl " + input + ".thumb.jpg 14 " + strTitle
    os.system(call_str)
    call_str = "$INT_SCR/addtitle2jpg.pl " + input + ".bthumb.jpg 24 " + strTitle
    os.system(call_str)

def UseGamma(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[1].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()

def usage():
    print '''
******************************************************************************************************
 
       Coregistration of SAR images based on cross-correlation by using GAMMA.
       Be suitable for conventional InSAR, MAI, Range Split-Spectrum InSAR.

   usage:
   
            SLC2Ifg_Sen_Gamma.py igramDir
      
      e.g.  SLC2Ifg_Sen_Gamma.py IFG_PacayaT163S1A_131021-131101_0011_0007
      e.g.  SLC2Ifg_Sen_Gamma.py MAI_PacayaT163S1A_131021-131101_0011_0007
      e.g.  SLC2Ifg_Sen_Gamma.py RSI_PacayaT163S1A_131021-131101_0011_0007
          
            
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: igramDir=sys.argv[1]        
    else:
        usage();sys.exit(1)
       
    INF = igramDir.split('_')[0]
    projectName = igramDir.split('_')[1]
    IFGPair = igramDir.split(projectName+'_')[1].split('_')[0]
    Mdate = IFGPair.split('-')[0]
    Sdate = IFGPair.split('-')[1]
    
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    workDir    = processDir + '/' + igramDir   

########################################################################

    #call_str = 'Check_Common_Burst.py ' + igramDir
    #os.system(call_str)
    
    #call_str = 'Extract_Common_Burst.py ' + igramDir
    #os.system(call_str)

    #call_str = 'CreateRdcDem_Sen_Gamma.py ' + igramDir
    #os.system(call_str)
    
    if 'DiffPhase' in templateContents :  DiffPhase =  templateContents['DiffPhase']
    else: DiffPhase = '1'
        
    if 'UnwrapPhase' in templateContents :  UnwrapPhase =  templateContents['UnwrapPhase']
    else: UnwrapPhase = '1'
        
    if 'GeoPhase' in templateContents :  GeoPhase =  templateContents['GeoPhase']
    else: GeoPhase = '1'
    
    if DiffPhase == '1':
        call_str = 'DiffPhase_Sen_Gamma.py ' + igramDir
        os.system(call_str)
        
        call_str ='GenerateRSC_Sen_Gamma.py ' + igramDir
        os.system(call_str)
    
    if UnwrapPhase =='1':
        call_str = 'UnwrapPhase_Sen_Gamma.py ' + igramDir
        os.system(call_str)
    
    if GeoPhase =='1':
        call_str = 'Geocode_Sen_Gamma.py ' + igramDir
        os.system(call_str)   

    print "Interferometry process for Sentinel-1 is done !" 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
