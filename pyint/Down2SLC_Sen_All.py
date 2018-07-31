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
 
                 Downloading Sentinel-1A/B data based on ssara

   usage:
   
            Down2SLC_Sen_All.py ProjectName
      
      e.g.  Down2SLC_Sen_All.py CotopaxiT120SenVVA
      
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        projectName = sys.argv[1]
    else:
        usage();sys.exit(1)
         
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    
    projectDir = scratchDir + '/' + projectName 
    downDir    = scratchDir + '/' + projectName + "/DOWNLOAD"

    os.chdir(downDir)
    
    call_str = 'ls  > ttt0'
    os.system(call_str)
    
    
    call_str = 'grep .zip ttt0 > ttt'
    os.system(call_str)
    ZIP = np.loadtxt('ttt',dtype = np.str)
    N = ZIP.size
    DATE = []
    
    if N>1:
        for i in range(N):
            RAWNAME = ZIP[i]
            Date = RAWNAME[19:25]
            if (not (Date in DATE)) and len(Date)>0:
                DATE.append(Date) 
                
    call_str = 'grep SAFE ttt0 > ttt'
    os.system(call_str)
    SAFE = np.loadtxt('ttt',dtype = np.str)
    N = SAFE.size
    
    if N >1:
        for i in range(N):
            RAWNAME = SAFE[i]
            Date = RAWNAME[19:25]
            if (not (Date in DATE)) and len(Date)>0:
                DATE.append(Date) 
    
    N = len(DATE)
    
    run_down2slc_sen = downDir + '/run_down2slc_sen'
    f_down2slc =open(run_down2slc_sen,'w')
    
    for i in range(N):
        str_script = 'Down2SLC_Sen_Gamma.py ' + projectName + ' ' + DATE[i] + '\n'
        f_down2slc.write(str_script)
        print 'Add download raw S1 data: ' + DATE[i]
    f_down2slc.close()
    
    print ''
    print 'Start processing down2sl for project: ' + projectName
    
    call_str='$INT_SCR/createBatch.pl ' + run_down2slc_sen + ' memory=3700  walltime=0:30'
    os.system(call_str)
    
    print "Down to SLC for project %s is done! " % projectName
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
