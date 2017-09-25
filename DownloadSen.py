#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   March, 2017                                               #
#                                                                                #
#           Download Sentinel-1A/B data based on ssara                           #
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
   
            DownloadSen.py ProjectName
      
      e.g.  DownloadSen.py PacayaT163TsxHhA
      
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
    
    projectDir = scratchDir + '/' + projectName
    downDir     = scratchDir + '/' + projectName + "/DOWNLOAD"

    if not os.path.isdir(projectDir):
        call_str = 'mkdir ' + projectDir
        os.system(call_str)

    if not os.path.isdir(downDir):
        call_str = 'mkdir ' + downDir
        os.system(call_str)
        
    os.chdir(downDir)
    
#################################  Define coregistration parameters ##########################
    templateContents=read_template(templateFile)
    Track = templateContents['Track']
    Frame = templateContents['Frame']
    
    if 'Startdate' in templateContents: 
        Startdate = templateContents['Startdate'] 
        STARTSTR = ' -s ' + Startdate
    else:
        STARTSTR = ''
        
        
    if 'Enddate' in templateContents: 
        Enddate = templateContents['Enddate']  
        ENDSTR = ' -e ' + Enddate
    else:
        ENDSTR = ''

    
    
    SSARA_STRA = 'ssara_federated_query.py -p Sentinel-1A -r ' + Track + ' -f '+ Frame + STARTSTR + ENDSTR + ' --print --download --parallel=2'  
    print SSARA_STRA
    os.system(SSARA_STRA)
    
    
    SSARA_STRB ='ssara_federated_query.py -p Sentinel-1B -r ' + Track + ' -f '+ Frame + STARTSTR + ENDSTR  + ' --print --download --parallel=2'  
    print SSARA_STRB
    os.system(SSARA_STRB)   
    
    
    print "Downloading Sentinel-1A/B during %s and %s is done " % ( Startdate, Enddate )
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
