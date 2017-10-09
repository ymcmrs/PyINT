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
        
        
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def usage():
    print '''
******************************************************************************************************
 
                 Estimating the offsets of two SAR images based on cross-correlation.

   usage:
   
            GenOff_Sen_All.py ProjectName
      
      e.g.  GenOff_Sen_All.py PacayaT163TsxHhA
      
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        projectName = sys.argv[1]
    else:
        usage();sys.exit(1)
         
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    IFGPair    = Mdate + '-' + Sdate
    OFFDir     = scratchDir + '/' + projectName + "/SLC/OFF"
    
    if not os.path.isdir(OFFDIR):
        call_str = 'mkdir ' + OFFDIR
        os.system(call_str);

    KK=os.listdir(slcDir)
    Nm = []
    for ll in KK:
        if is_numer(ll):
            Nm.append(ll)
    os.chdir(SLCPATH)
    
    if 'masterDate'          in templateContents:
        masterDate0 = templateContents['masterDate']
        if masterDate0 in Datelist:
            masterDate = masterDate0
            print "masterDate : " + masterDate0
        else:
            masterDate=Nm[0]
            print "The selected masterDate is not included in above datelist !!"
            print "The first date [ %s ] is chosen as the master date! " % Datelist[0]
           
            
    else:  
        masterDate=Nm[0]
        print "masterDate is not found in template!!! "
        print "The first date [ %s ] is chosen as the master date! " % Datelist[0] 

   
    run_Genoff_Sen = OFFDIR + '/run_Genoff_Sen'
    if os.path.isfile(run_Genoff_Sen):
        call_str = 'rm ' + run_Genoff_Sen
        os.system(call_str)
        
    for dd in Nm:
        if dd != masterDate:
            STR = 'GenOff_Sen_Gamma.py ' + projectName + ' ' + masterDate + ' ' + dd + ' ' + OFFDIR + '>> run_Genoff_Sen'
            call_str = 'echo ' + STR
        
    call_str = 'BatchProcess.py -p ' + run_Genoff_Sen +' -m 3700 -t 1:00'
    os.system(call_str)
    
    
    print "Coregistrating for project %s is done! " % projectName
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    