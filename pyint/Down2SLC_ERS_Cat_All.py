#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   March, 2017                                               #
#                                                                                #
#           Generate Sentinel SLC from the downloaded data                       #
#                                                                                #
##################################################################################
#'''
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
        print("Keyword " + keyword + " doesn't exist in " + inFile)
        f.close
        
def rm(TXT):
    call_str = 'rm ' + TXT
    os.system(call_str)        

def usage():
    print('''
******************************************************************************************************
 
                 Downloading Sentinel-1A/B data based on ssara

   usage:
   
            Down2SLC_ERS_Cat_All.py ProjectName
      
      e.g.  Down2SLC_ERS_Cat_All.py CotopaxiT120ERSA
      
*******************************************************************************************************
    ''')   
    
def main(argv):
    
    if len(sys.argv)==2:
        projectName = sys.argv[1]
    else:
        usage();sys.exit(1)
         
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    
    projectDir = scratchDir + '/' + projectName 
    downDir    = scratchDir + '/' + projectName + "/DOWNLOAD"
    slcDir     = scratchDir + '/' + projectName + '/SLC'
    
    if not os.path.isdir(slcDir):
        call_str= 'mkdir ' +slcDir
        os.system(call_str)
    
    os.chdir(downDir)
    
    call_str = 'ls > tt0'
    os.system(call_str)
    
    call_str = 'grep SAR_IMS_1P tt0 >tt1'
    os.system(call_str)
    
    call_str = "awk -F_ '{print $3}' tt1 > tt2 " 
    os.system(call_str)
    
    call_str = "awk -FSA '{print $2}' tt2  > ttt"
    os.system(call_str)
    
    call_str = 'sort ttt | uniq > ttm'
    os.system(call_str)
    
    AA= np.loadtxt('ttm',dtype=np.str)
    Na = AA.size
    
    for i in range(Na):
        call_str = 'Down2SLC_ERS_Cat.py ' + projectName + ' ' + AA[i]
        print(call_str)
        call_str = 'Down2SLC_ERS_Cat.py ' + projectName + ' ' + AA[i] + ' >/dev/null'
        os.system(call_str)
        

    print("Down to SLC for %s is done! " % projectName)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
