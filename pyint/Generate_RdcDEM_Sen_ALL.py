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
        print("Keyword " + keyword + " doesn't exist in " + inFile)
        f.close()
        
def geocode(inFile, outFile, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM):
    if inFile.rsplit('.')[1] == 'int':
        call_str = '$GAMMA_BIN/geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 1'
    else:
        call_str = '$GAMMA_BIN/geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 0'
    os.system(call_str)
    
def createBlankFile(strFile):
    f = open(strFile,'w')
    for i in range (10):
        f.write('\n')
    f.close()    
    

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

def usage():
    print('''
******************************************************************************************************
 
       Generating Radar coordinates-based DEM based on GEO-DEM files.
       If no dem file found, makedem.py will be called.

   usage:
   
            Generate_RdcDEM_Sen_ALL.py projectName
      
      e.g.  Generate_RdcDEM_Sen_ALL.py PacayaT163TsxHhA
      
*******************************************************************************************************
    ''')   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: 
            projectName=sys.argv[1]      
    else:
        usage();sys.exit(1)
      
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    DEMDir = os.getenv('DEMDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC" 
    rslcDir     = scratchDir + '/' + projectName + "/RSLC" 
   

    ListSLC = os.listdir(slcDir)
    Datelist = []

    for kk in range(len(ListSLC)):
        if ( is_number(ListSLC[kk]) and len(ListSLC[kk])==6 ):    #  if SAR date number is 8, 6 should change to 8.
            DD=ListSLC[kk]
            Year=int(DD[0:2])
            Month = int(DD[2:4])
            Day = int(DD[4:6])
            if  ( 0 < Year < 20 and 0 < Month < 13 and 0 < Day < 32 ):            
                Datelist.append(ListSLC[kk])
    
    list(map(int,Datelist))                
    Datelist.sort()
    
    run_GenDEM_rslc_all = processDir + '/DEM/run_GenDEM_rslc_all'
    if os.path.isfile(run_GenDEM_rslc_all):
        os.remove(run_GenDEM_rslc_all)

    
    for kk in Datelist:
        STR = 'echo Generate_RdcDEM_Sen_Gamma.py ' + projectName + ' ' + kk + ' >>' + run_GenDEM_rslc_all
        os.system(STR)
     
    call_str = 'process_loop_runfile.py ' + processDir + '/DEM/run_GenDEM_rslc_all'
    os.system(call_str)
    
    #call_str='$INT_SCR/createBatch.pl ' + run_GenDEM_rslc_all + ' memory=5000 ' + ' walltime= 1:00'
    #os.system(call_str)
    

    print("Create RdcDEM based on rslcs in Radar Coordinates is done!")
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
