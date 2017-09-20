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
 
          Coregistrate all SAR or interferograms to one master data

   usage:
   
            Resamp_all_Gamma.py igramDir
      
      e.g.  Resamp_all_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  Resamp_all_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_0007      
      e.g.  Resamp_all_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_0007          
            
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
    rslcDir    = scratchDir + '/' + projectName + "/RSLC"
    workDir    = processDir + '/' + igramDir   
    
    if not os.path.isdir(rslcDir):
        call_str = 'mkdir ' + rslcDir
        os.system(call_str)
        
    templateContents=read_template(templateFile)
    masterDate   =  templateContents['masterDate']    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
 
    Moff = rslcDir +"/"+ masterDate + '-' + Mdate + '.off'
    Soff = rslcDir +"/"+ masterDate + '-' + Sdate + '.off'        
    
    if INF=='IFG' or INF =='IFGRAM':
        Suffix=['']
    elif INF=='MAI':
        Suffix=['.F','.B']
    elif INF=='RSI':
        Suffix=['.HF','.LF']
    else:
        print "The folder name %s cannot be identified !" % igramDir
        usage();sys.exit(1)  
# definition of intermediate and output file variables for slc images and parameters

    BaseslcDir = slcDir + "/" + masterDate
    BaseslcImg = BaseslcDir + '/' + masterDate + '.slc'
    BaseslcPar = BaseslcDir + '/' + masterDate + '.slc.par'
    Baseslc4Par = workDir + '/' + masterDate + '.slc4.par'
    
    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

    MslcImg = MslcDir + "/" + Mdate + ".slc"
    MslcPar = MslcDir + "/" + Mdate + ".slc.par"
    SslcImg = SslcDir + "/" + Sdate + ".slc"
    SslcPar = SslcDir + "/" + Sdate + ".slc.par"
 
    offs = workDir + "/offs"
    snr = workDir + "/snr"
    offsets = workDir + "/offsets"
    coffs = workDir + "/coffs"
    coffsets = workDir + "/coffsets"
    
    MrslcImg = rslcDir + "/" + Mdate + ".rslc"
    MrslcPar = rslcDir + "/" + Mdate + ".rslc.par"
    SrslcImg = rslcDir + "/" + Sdate + ".rslc"
    SrslcPar = rslcDir + "/" + Sdate + ".rslc.par"

    MamprlksImg = rslcDir + "/" + Mdate + '_'+rlks+'rlks' + ".ramp"
    MamprlksPar = rslcDir + "/" + Mdate + '_'+rlks+'rlks' + ".ramp.par"
        
    SamprlksImg = rslcDir + "/" + Sdate + '_'+rlks+'rlks' + ".ramp"
    SamprlksPar = rslcDir + "/" + Sdate + '_'+rlks+'rlks' + ".ramp.par"

##############################################  Resampling #####################################################

    for i in range(len(Suffix)):
        if not INF=='IFG':
            MslcImg = workDir + "/" + Mdate + Suffix[i]+".slc"
            MslcPar = workDir + "/" + Mdate + Suffix[i]+".slc.par"
            SslcImg = workDir + "/" + Sdate + Suffix[i]+".slc"
            SslcPar = workDir + "/" + Sdate + Suffix[i]+".slc.par"
 
        INT      = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.int'
        INTpar   = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.int.par'
        
        rINT     = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.rint'
        rINTpar  = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.rint.par'
        
        MrslcImg0 = workDir + "/" + Mdate + Suffix[i]+".rslc"
        MrslcPar0 = workDir + "/" + Mdate + Suffix[i]+".rslc.par"
        MrslcPar00 = workDir + "/" + Mdate + Suffix[i]+".rslc0.par"
        
        call_str = 'cp ' + MrslcPar0 + ' ' + MrslcPar00
        os.system(call_str)
        
        MrslcImg = rslcDir + "/" + Mdate + Suffix[i]+".rslc"
        MrslcPar = rslcDir + "/" + Mdate + Suffix[i]+".rslc.par"
        SrslcImg = rslcDir + "/" + Sdate + Suffix[i]+".rslc"
        SrslcPar = rslcDir + "/" + Sdate + Suffix[i]+".rslc.par"

        MamprlksImg = rslcDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        MamprlksPar = rslcDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        
        SamprlksImg = rslcDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        SamprlksPar = rslcDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"

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
##################################################

        call_str = 'cp ' + MamprlksImg + ' ' + workDir
        os.system(call_str)
        call_str = 'cp ' + MamprlksPar + ' ' + workDir
        os.system(call_str)
        
        call_str = 'cp ' + SamprlksImg + ' ' + workDir
        os.system(call_str)
        call_str = 'cp ' + SamprlksPar + ' ' + workDir
        os.system(call_str)
        
        call_str = 'cp ' + MrslcPar + ' ' + workDir
        os.system(call_str)
        call_str = 'cp ' + SrslcPar + ' ' + workDir
        os.system(call_str)
        
        call_str = 'cp ' + MrslcImg + ' ' + workDir
        os.system(call_str)
        call_str = 'cp ' + SrslcImg + ' ' + workDir
        os.system(call_str)
        
        
#######################################################        

        if ( masterDate != Mdate):
            call_str = "$GAMMA_BIN/SLC_interp " + INT + " " + Baseslc4Par + " " + INTpar + " " + Moff + " " + rINT + " " + rINTpar
            os.system(call_str)
            os.rename(rINT, INT)

    
    print "Coregistrate "+ igramDir +" to " + masterDate +" is done! "
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
