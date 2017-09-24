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
 
          Simulating Topography phase and flattening phase based on radar-coordinates' DEM

   usage:
   
            SimPhase_Gamma.py igramDir
      
      e.g.  SimPhase_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_-0007
      e.g.  SimPhase_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_-0007
      e.g.  SimPhase_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_-0007          
            
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
    
    templateContents=read_template(templateFile)
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']

    simDir = scratchDir + '/' + projectName + "/PROCESS" + "/SIM" 
    if not os.path.isdir(simDir):
        call_str='mkdir ' + simDir 
        os.system(call_str)
  
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate
    if not os.path.isdir(simDir):
        call_str='mkdir ' + simDir 
        os.system(call_str)
    
    demDir = scratchDir + '/' + projectName + "/PROCESS" + "/DEM" 

    if INF=='IFG':
        Suffix=['']
    elif INF=='MAI':
        Suffix=['.F','.B']
    elif INF=='RSI':
        Suffix=['.HF','.LF']
    else:
        print "The folder name %s cannot be identified !" % igramDir
        usage();sys.exit(1)

#  Definition of file
    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

    MslcImg = MslcDir + "/" + Mdate + ".slc"
    MslcPar = MslcDir + "/" + Mdate + ".slc.par"
    SslcImg = SslcDir + "/" + Sdate + ".slc"
    SslcPar = SslcDir + "/" + Sdate + ".slc.par"
    
    MrslcImg = workDir + "/" + Mdate + ".rslc"
    MrslcPar = workDir + "/" + Mdate + ".rslc.par"
    SrslcImg = workDir + "/" + Sdate + ".rslc"
    SrslcPar = workDir + "/" + Sdate + ".rslc.par"
    
    MamprlksImg = workDir + "/" + Mdate + '_'+rlks+'rlks' + ".ramp"
    MamprlksPar = workDir + "/" + Mdate + '_'+rlks+'rlks' + ".ramp.par"   
    OFFlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.off'

    #if 'masterDate'          in templateContents: 
    #    masterDate = templateContents['masterDate']   
    #    HGTSIM      = demDir + '/sim_' + masterDate + '_' + rlks +'rlks' + '.rdc.dem'          
    #    if not os.path.isfile(HGTSIM):
    #        HGTSIM      = demDir + '/sim_' + Mdate + '_' + rlks +'rlks' + '.rdc.dem'
    #else:
    #    HGTSIM = demDir + '/sim_' + Mdate + '_' + rlks +'rlks' + '.rdc.dem'
        
    #if not os.path.isfile(HGTSIM):       
    #   call_str = 'Generate_RdcDEM_Gamma.py ' + projectName + ' ' + Mdate
    #    os.system(call_str)
  
    HGTSIM = demDir + '/sim_' + Mdate + '_' + rlks +'rlks' + '.rdc.dem'
    if not os.path.isfile(HGTSIM):       
        call_str = 'Generate_RdcDEM_Rslc_Gamma.py ' + projectName + ' ' + Mdate
        os.system(call_str)
    
    SIMUNW      = simDir + '/sim_' + Mdate + '-' + Sdate + '_' + rlks +'rlks' + '.sim_unw'

        
###################################  Phase Simulation  ###########################################
    
    if os.path.isfile(OFFlks):
        nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')
    else:
        nWidth = UseGamma(MamprlksPar, 'read', 'range_samples:')
    
    if 'Igram_Flag_TDM' in templateContents: flagTDM = templateContents['Igram_Flag_TDM']
    else: flagTDM = 'N'

    if flagTDM == 'N':
        call_str = '$GAMMA_BIN/phase_sim_orb ' + MrslcPar + ' ' + SrslcPar + ' ' + OFFlks + ' ' + HGTSIM + ' ' + SIMUNW 
    else:
        call_str = '$GAMMA_BIN/phase_sim_orb ' + MrslcPar + ' ' + SrslcPar + ' ' + OFFlks + ' ' + HGTSIM + ' ' + SIMUNW + ' - - - 0' 
    os.system(call_str)


    print "Simulation interferometric phas with DEM is done!"
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
