#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   February, 2017                                            #
#                                                                                #
#         Split beam of SLC: backward and forward SLC image generation           #
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
 
         Split beam of original SLC to generate sub-aperture SLC: backward- and forward-SLCs 

   usage:
   
            MAI_SLC_Gamma.py igramDir
      
      e.g.  MAI_SLC_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_0007
          
            
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

    if INF!='MAI':
        usage();sys.exit(1)
    
    if not os.path.isdir(workDir):
        call_str="mkdir " + workDir
        os.system(call_str)
        
    templateContents=read_template(templateFile)
    coregCoarse = templateContents['Coreg_Coarse']
    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']

    if 'Squint_MAI' in templateContents: Squint = templateContents['Squint_MAI']
    else: Squint = '0.5'
# input slcs

    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

# input slcs

    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

    MslcImg = MslcDir + "/" + Mdate + ".slc"
    MslcPar = MslcDir + "/" + Mdate + ".slc.par"
    SslcImg = SslcDir + "/" + Sdate + ".slc"
    SslcPar = SslcDir + "/" + Sdate + ".slc.par"

# split slcs

    MFslcImg = workDir + "/" + Mdate + ".F.slc"
    MFslcPar = workDir + "/" + Mdate + ".F.slc.par"
    SFslcImg = workDir + "/" + Sdate + ".F.slc"
    SFslcPar = workDir + "/" + Sdate + ".F.slc.par"

    MBslcImg = workDir + "/" + Mdate + ".B.slc"
    MBslcPar = workDir + "/" + Mdate + ".B.slc.par"
    SBslcImg = workDir + "/" + Sdate + ".B.slc"
    SBslcPar = workDir + "/" + Sdate + ".B.slc.par"
    
    print  MFslcImg + " "+ MslcImg
    
# Multi-aperture processing

    call_str = '$GAMMA_BIN/sbi_filt '+ MslcImg + ' ' + MslcPar + ' '+SslcPar + ' ' + MFslcImg + ' '+ MFslcPar + ' ' + MBslcImg + ' ' + MBslcPar + ' ' + Squint
    os.system(call_str)
    print call_str    

    call_str = '$GAMMA_BIN/sbi_filt '+ SslcImg + ' ' + SslcPar + ' '+MslcPar + ' ' + SFslcImg + ' '+ SFslcPar + ' ' + SBslcImg + ' ' + SBslcPar + ' ' + Squint
    os.system(call_str)
    
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
    










    
    
    
