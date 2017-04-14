#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   March , 2017                                               #
#                                                                                 #
#         Range Split Spectrum for SAR complex data based on GAMMA                #
#                                                                                 #
###################################################################################
#'''
import numpy as np
import os
import pysar._readfile as readfile
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


def usage():
    print '''
******************************************************************************************************
 
         Split Spectrum on range direction to generate high-frequency- and low-frequency- SLCs

   usage:
   
            RSI_SLC_Gamma.py igramDir
      
      e.g.  RSI_SLC_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
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
    workdir    = processDir + '/' + igramDir   
    
    templateContents=read_template(templateFile)
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']

    if INF!='RSI':
        usage();sys.exit(1)

    if not os.path.isdir(workdir):
        call_str = 'mkdir ' + workdir
        os.system(call_str)
        
    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

# input slcs

    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

    MslcImg = MslcDir + "/" + Mdate + ".slc"
    MslcPar = MslcDir + "/" + Mdate + ".slc.par"
    SslcImg = SslcDir + "/" + Sdate + ".slc"
    SslcPar = SslcDir + "/" + Sdate + ".slc.par"

    
    MHslcImg = workdir + '/'+Mdate + '.HF.slc'
    MHslcPar = workdir + '/'+Mdate + '.HF.slc.par'
    call_str = 'cp ' + MslcPar + ' '+ MHslcPar
    os.system(call_str)
    
    SHslcImg = workdir + '/'+Sdate + '.HF.slc'
    SHslcPar = workdir + '/'+Sdate + '.HF.slc.par'
    call_str = 'cp ' + SslcPar + ' '+ SHslcPar
    os.system(call_str)    
    
    MLslcImg = workdir + '/'+Mdate + '.LF.slc'
    MLslcPar = workdir + '/'+Mdate + '.LF.slc.par'
    call_str = 'cp ' + MslcPar + ' '+ MLslcPar
    os.system(call_str)
    
    SLslcImg = workdir + '/'+Sdate + '.LF.slc'
    SLslcPar = workdir + '/'+Sdate + '.LF.slc.par'
    call_str = 'cp ' + SslcPar + ' '+ SLslcPar
    os.system(call_str)
    
    nWidth = UseGamma(MslcPar, 'read','range_samples:')
    
    call_str= 'bpf ' + MslcImg + ' ' + MHslcImg + ' ' + nWidth + ' 0.25 0.5 0 1 0 0 - - 1'
    os.system(call_str)
    
    call_str= 'bpf ' + MslcImg + ' ' + MLslcImg + ' ' + nWidth + ' -0.25 0.5 0 1 0 0 - - 1'   
    os.system(call_str)
    
    nWidth = UseGamma(SslcPar, 'read','range_samples:')
   
    call_str= 'bpf ' + SslcImg + ' ' + SHslcImg + ' ' + nWidth + ' 0.25 0.5 0 1 0 0 - - 1'
    os.system(call_str)
    
    call_str= 'bpf ' + SslcImg + ' ' + SLslcImg + ' ' + nWidth + ' -0.25 0.5 0 1 0 0 - - 1'   
    os.system(call_str)
    
    
    print "Split spectrum for both slave and master date is done!"
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
