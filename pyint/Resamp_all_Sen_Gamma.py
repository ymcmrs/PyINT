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
import re

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
 
          Resampling all Sentinel-1 based intferograms into one master date coordinates.

   usage:
   
            Resamp_all_Sen_Gamma.py igramDir
      
      e.g.  Resamp_all_Sen_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  Resamp_all_Sen_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_0007      
      e.g.  Resamp_all_Sen_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_0007          
            
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
    demDir = scratchDir + '/' + projectName + "/PROCESS/DEM"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir    = scratchDir + '/' + projectName + "/RSLC"
    workDir    = processDir + '/' + igramDir   
    simDir = scratchDir + '/' + projectName + "/PROCESS/SIM"
    
    if not os.path.isdir(simDir):
        call_str= 'mkdir ' + simDir
        os.system(call_str)
    
    if not os.path.isdir(rslcDir):
        call_str = 'mkdir ' + rslcDir
        os.system(call_str)
        
    templateContents=read_template(templateFile)
    masterDate   =  templateContents['masterDate']    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
 
    M_off = rslcDir +'/' + Mdate + '/' + masterDate + '-' + Mdate + '.off'
    M_lt = rslcDir +'/' + Mdate + '/' + masterDate + '-' + Mdate + '.lt   '      
    
  
# definition of intermediate and output file variables for slc images and parameters

    BaseslcDir = rslcDir + "/" + masterDate 
    BaseslcImg = BaseslcDir + '/' + masterDate + '.slc'
    BaseslcPar = BaseslcDir + '/' + masterDate + '.slc.par'
    Baseslc4Par = workDir + '/' + masterDate + '.slc4.par'
    
    SslcDir = rslcDir + "/" + Sdate
    MslcDir = rslcDir + "/" + Mdate
    
    MLI1PAR = rslcDir +'/' + masterDate + '/' + masterDate + '_' + rlks + 'rlks.amp.par'
    MLI2PAR = rslcDir +'/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    
    HGTSIM = demDir + '/sim_' + masterDate + '_' + rlks +'rlks' + '.rdc.dem'
    SIMUNW      = simDir + '/sim_' + Mdate + '-' + Sdate + '_' + rlks +'rlks' + '.sim_unw'
    

    MrslcPar = MslcDir + "/" + Mdate + ".rslc.par"
    SrslcPar = SslcDir + "/" + Sdate + ".rslc.par"
    
    MrslcPar0 = workDir + "/" + Mdate + ".rslc.par"
    SrslcPar0 = workDir + "/" + Sdate + ".rslc.par"
    MrslcImg0 = workDir + "/" + Mdate + ".rslc"
    SrslcImg0 = workDir + "/" + Sdate + ".rslc"

    OFF = workDir + '/' + Mdate+ '-' + Sdate  + '.roff'
    OFFlks = workDir + '/' + Mdate+ '-' + Sdate + '_' + rlks + 'rlks.roff'
    DIFFpar = workDir + '/' + Mdate+ '-' + Sdate  + '.diff_par'
    
    int_off = workDir + '/off0'
    INT = workDir + '/' + Mdate + '-' + Sdate + '.int'
    INTpar = workDir + '/' + Mdate + '-' + Sdate + '.int.par'
    rINT =  workDir + '/' + Mdate + '-' + Sdate + '.rint'
    rINTpar =  workDir + '/' + Mdate + '-' + Sdate + '.rint.par'
    INTlks = workDir + '/' + Mdate + '-' + Sdate +  '_' + rlks + 'rlks.int' 
    DIFFINTlks = workDir + '/' + Mdate + '_' + Sdate + '.diff' 
    DIFFFILTlks = workDir + '/diff_filt_' + Mdate + '-' + Sdate +  '_' + rlks + 'rlks.int' 
    
    if os.path.isfile(OFFlks):
        os.remove(OFFlks)
        
    if os.path.isfile(int_off):
        os.remove(int_off)
        
    if os.path.isfile(DIFFpar):
        os.remove(DIFFpar)

##############################################  Resampling #####################################################

####   detect the choice for resampling #######      
        
        
### post coregistration for interferogram 

    fin = open(BaseslcPar,"r")
    fout = open(Baseslc4Par,"w")
    txt = fin.read()
    txtout = re.subn("SCOMPLEX","FCOMPLEX",txt)[0]
    fout.write(txtout)
    fin.close()
    fout.close()

    fin = open(MrslcPar0,"r")
    fout = open(INTpar,"w")
    txt = fin.read()
    txtout = re.subn("SCOMPLEX","FCOMPLEX",txt)[0]
    fout.write(txtout)
    fin.close()
    fout.close()

    if not Mdate==masterDate:
        call_str = 'create_offset ' + MrslcPar0 + ' ' + MrslcPar0 + ' ' + int_off + ' 1 - - 0'
        os.system(call_str)
    
        call_str = '$GAMMA_BIN/SLC_intf ' + MrslcImg0 + ' ' + SrslcImg0 + ' ' + MrslcPar0 + ' ' + SrslcPar0 + ' ' + int_off + ' ' + INT + ' 1 1 - - - - - -'
        os.system(call_str)
    
        call_str = "$GAMMA_BIN/SLC_interp_lt " + INT + " " + Baseslc4Par + " " + INTpar  + " " + M_lt + " " + MLI1PAR + " " + MLI2PAR + " " + M_off + " " + rINT + " " + rINTpar
        os.system(call_str)
        os.rename(rINT, INT)
    
    if os.path.isfile(OFF):
        os.remove(OFF)
    call_str = 'create_offset ' + MrslcPar + ' ' + MrslcPar + ' ' + OFF + ' 1 - - 0'
    os.system(call_str)
    call_str = '$GAMMA_BIN/multi_cpx '+ INT + ' ' + OFF + ' ' + INTlks + ' ' + OFFlks + ' ' + rlks + ' ' + azlks
    os.system(call_str)
    
    #call_str = 'create_offset ' +  MrslcPar + ' ' + SrslcPar + ' ' + OFFlks + ' 1 ' + rlks + ' ' + azlks + ' 0'
    #os.system(call_str)
    
    call_str = '$GAMMA_BIN/phase_sim_orb ' + MrslcPar + ' ' + SrslcPar + ' ' + OFFlks + ' ' + HGTSIM + ' ' + SIMUNW
    os.system(call_str)
    
    if os.path.isfile(DIFFpar):
        os.remove(DIFFpar)
    call_str = '$GAMMA_BIN/create_diff_par ' + MLI1PAR + ' ' + MLI1PAR + ' ' + DIFFpar + ' 1 0 '
    os.system(call_str)     
        
    call_str = '$GAMMA_BIN/sub_phase ' + INTlks + ' ' + SIMUNW + ' ' + DIFFpar + ' ' + DIFFINTlks + ' 1 0'
    os.system(call_str)   
    
    #os.remove(INT)
    
     #call_str = '$GAMMA_BIN/adapt_filt ' + DIFFINTlks + ' ' + DIFFINTFILTlks + ' ' + nWidth + ' ' + fFiltLengthDiff + ' ' + nFiltWindowDiff
     #os.system(call_str)
        
    print "Coregistrate "+ igramDir +" to " + masterDate +" is done! "
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
