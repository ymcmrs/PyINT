#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   June, 2019                                                #
#                                                                                #
#           Generate SLC from SAR_IMS_P1 data                                    #
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
 
                 Generate SLC and SLC_par file for ERS/ENVISAT  (SAR_IMS_1P format)

   usage:
   
            Down2SLC_ERS.py ProjectName DownName 
      
      e.g.  Down2SLC_ERS.py CotopaxiT120ERSA 910101
      
*******************************************************************************************************
    ''')   
    
def main(argv):
    
    if len(sys.argv)==3:
        projectName = sys.argv[1]
        Date  = sys.argv[2]
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
    
    t0 = 't0_' + Date
    call_str = 'ls  >' + t0
    os.system(call_str)

    tt = 'tt_' + Date
    call_str = "grep " + Date + ' ' + t0 + '> ' + tt
    os.system(call_str)
    
    te = 'te_' + Date
    call_str = "grep SAR_IMS_1P " + tt + " > " + te 
    os.system(call_str)
    
    AA= np.loadtxt(te,dtype=np.str)
    Na = AA.size
    
    if Na > 0:
        downName = str(AA[0])    
        FileDir = downDir + '/' + downName
        call_str = 'par_ASAR '+ FileDir + ' ' + Date
        os.system(call_str)
    else:
        print('No data is found for date:' + Date)
        sys.exit(1)
        
    call_str ="rename 's/VV.SLC/slc/g' *"
    os.system(call_str)
    
    Date0 = Date
    if len(Date)==6:
        Date0 = Date
    elif len(Date)==8:
        Date0 = Date[2:8]
    else:
        print('The input Date is invalid.')
        sys.exit(1)
    
    dataDir = slcDir + '/' + Date0
    if not os.path.isdir(dataDir):
        call_str = 'mkdir ' + dataDir
        print('Generate SLC dir for date: ' + Date0)
        os.system(call_str)
    call_str = 'mv ' + Date + '.slc* ' + dataDir
    os.system(call_str)
        
    print("Down to SLC for %s is done! " % Date)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
