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
import argparse

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
        print("Keyword " + keyword + " doesn't exist in " + inFile)
        f.close()

def common_burst_Ref(La_M,La_S):
    Min = max(min(La_M),min(La_S))
    Max = min(max(La_M),max(La_S))
    
    M_min = []
    M_max = []
    for xm in La_M:
        k0_min = float(xm) - float(Min)
        k0_max = float(xm) - float(Max)
        M_min.append(abs(k0_min))
        M_max.append(abs(k0_max))
    
    M_Index_min = M_min.index(min(M_min)) + 1
    M_Index_max = M_max.index(min(M_max)) + 1
    Mindex =[M_Index_min,M_Index_max]
    
    S_min = []
    S_max = []
    for xs in La_S:
        k0_min = float(xs) - float(Min)
        k0_max = float(xs) - float(Max)
        S_min.append(abs(k0_min))
        S_max.append(abs(k0_max))
    
    S_Index_min = S_min.index(min(S_min)) + 1 
    S_Index_max = S_max.index(min(S_max)) + 1
    Sindex =[S_Index_min,S_Index_max]
    #print La_M
    #print La_S
    #print min(M_min),min(M_max),min(S_min),min(S_max)
    M1 = min(Mindex)
    M2 = max(Mindex)
    
    S1 = min(Sindex)
    S2 = max(Sindex)
    
    if M1==1: S1 = S1
    else: 
        S1=1-M1+1
        M1=1
        
    
    if M2 ==len(La_M): S2 = S2
    else: 
        S2 = S2 + len(La_M) - M2 
        M2 = len(La_M)
        
    
    return M1 , M2, S1, S2

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def add_zero(s):
    if len(s)==1:
        s="000"+s
    elif len(s)==2:
        s="00"+s
    elif len(s)==3:
        s="0"+s
    return s
    
    
#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyINT v1.0
   
   Generate parameter file for the whole project.
'''

EXAMPLE = '''
    Usage:
            GenerateRSC_Sen_Gamma_All.py projectName
            
    Examples:
            GenerateRSC_Sen_Gamma_All.py PacayaT163TsxHhA
##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Check common busrts for TOPS data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of project.')

    inps = parser.parse_args()

    return inps

################################################################################    
    
    
def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
           
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC" 
    rslcDir = scratchDir + '/' + projectName + "/RSLC"
    IFGLIST = glob.glob(processDir+'/IFG*'+ projectName + '*') 
    
    TT = 'out.txt'
    if os.path.isfile(TT):
        os.remove(TT)
    for kk in IFGLIST:
        print('>>> Process ' + os.path.basename(kk))
        call_str = 'GenerateRSC_Sen_Gamma.py  ' + os.path.basename(kk) + ' >> ' + TT
        os.system(call_str)
   
        
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
