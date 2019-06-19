#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Central South University & University of Miami   ###   
#################################################################


import os
import sys
import glob
import time
import argparse

import h5py
import numpy as np

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
        
def UseGamma2(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[2].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()
        
def usage():
    print '''
******************************************************************************************************
 
          Get co-registration standard deviation of SLCs for one project

   usage:
   
            GenerateRSC_Gamma.py projectName
      
      e.g.  Get_off_std.py GalapagosT061EnvA

*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: projectName=sys.argv[1]        
    else:
        usage();sys.exit(1)
       
    scratchDir = os.getenv('SCRATCHDIR')
    OFFDir = scratchDir + '/' + projectName + '/RSLC'
    OFFSTR = OFFDir + '/*.off_std'
    OFFFile = glob.glob(OFFSTR)
    STD_TXT ='COREG_STD_ALL' 
    os.chdir(OFFDir)
    if os.path.isfile(STD_TXT):
        os.remove(STD_TXT)
    
    for ff in OFFFile:
        OFF_STD = ff
        NM = os.path.basename(ff).split('.')[0]
        RR = UseGamma(OFF_STD,'read','final range offset poly. coeff.:')
        cor_rg = RR.split(' ')[0]
        
        AA = UseGamma(OFF_STD,'read','final azimuth offset poly. coeff.:')
        cor_az = AA.split(' ')[0]
        
        STDRR = UseGamma(OFF_STD,'read','final model fit std. dev. (samples) range:')
        std_rg=STDRR.split(' ')[0]
    
        std_az = UseGamma2(OFF_STD,'read','final model fit std. dev. (samples) range:')  

        STR = NM + ' ' + cor_rg + ' ' + cor_az + ' ' + std_rg + ' ' + std_az
        call_str ='echo ' + STR + ' >> ' + STD_TXT
        os.system(call_str)
        
        
    sys.exit(1)
    
    
if __name__ == '__main__':
    main(sys.argv[1:])  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    