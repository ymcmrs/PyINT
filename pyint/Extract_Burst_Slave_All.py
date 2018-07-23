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

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


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
        
def write_template(File, Str):
    f = open(File,'a')
    f.write(Str)
    f.close()

def write_run_extract_burst_all(projectName,datelist):
    scratchDir = os.getenv('SCRATCHDIR')    
    projectDir = scratchDir + '/' + projectName   
    run_extract_burst_all  = projectDir + "/run_extract_burst_all"
    f_extract = open(run_extract_burst_all,'w')
    
    for kk in range(len(datelist)):
        str_extract = "Extract_Burst_Slave.py " + projectName + ' ' + datelist[kk] + '\n'
        f_extract.write(str_extract)
    f_extract.close()

#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyINT v1.0
   
   Extract common TOPS burst (Sentinel-1) for the whole project based on one master date.
   ps: Before using Extract_Burst_Slave_All.py, you should run Check_Common_Burst_All.py.
   
'''

EXAMPLE = '''
    Usage:
            Extract_Burst_Slave_All.py projectName
            
    Examples:
            Extract_Burst_Slave_All.py PacayaT163TsxHhA
##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Batch processing pegasus jobs.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('project',help='Project name of coregistration.')
    
    inps = parser.parse_args()

    return inps

################################################################################    
    
    
def main(argv):
    
    inps = cmdLineParse() 
    
    projectName = inps.project   
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    DEMDIR = os.getenv('DEMDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    projectDir = scratchDir + '/' + projectName
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir    = scratchDir + '/' + projectName + "/RSLC"
    
    if not os.path.isdir(rslcDir):
        call_str = 'mkdir ' + rslcDir
        os.system(call_str)
    
    if not os.path.isdir(processDir):
        call_str = 'mkdir ' + processDir
        os.system(call_str)

    templateContents = read_template(templateFile)
    if 'memory_Extract' in templateContents :  memory_Extract =  templateContents['memory_Extract']
    else: memory_Extract = '3700'
    if 'walltime_Extract' in templateContents :  walltime_Extract =  templateContents['walltime_Extract']
    else: walltime_Extract = '0:30'
    
#####################  Extract SLC Date #################################  

    ListSLC = os.listdir(slcDir)
    Datelist = []
    SLCfile = []
    SLCParfile = []
    
    print "All of the available SAR acquisition datelist is :"  
    for kk in range(len(ListSLC)):
        if ( is_number(ListSLC[kk]) and len(ListSLC[kk])==6 ):
            DD=ListSLC[kk]
            Year=int(DD[0:2])
            Month = int(DD[2:4])
            Day = int(DD[4:6])
            if  ( 0 < Year < 20 and 0 < Month < 13 and 0 < Day < 32 ):            
                Datelist.append(ListSLC[kk])
                print ListSLC[kk]
                str_slc = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc"
                str_slc_par = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc.par"
                SLCfile.append(str_slc)
                SLCParfile.append(str_slc_par)

        
    #SLAVElist = Datelist
    #del SLAVElist[Datelist.index(masterDate)]
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']

    

    write_run_extract_burst_all(projectName,Datelist)    
    call_str='$INT_SCR/createBatch.pl ' + projectDir+'/run_extract_burst_all memory=' +memory_Extract + ' walltime=' + walltime_Extract 
    os.system(call_str)

    
if __name__ == '__main__':
    main(sys.argv[:])
