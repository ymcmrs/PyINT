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

def usage():
    print '''
******************************************************************************************************
 
       Coregistration of SAR images based on cross-correlation by using GAMMA.
       Be suitable for conventional InSAR, MAI, Range Split-Spectrum InSAR.

   usage:
   
            CoregistSLC_init_Gamma.py igramDir
      
      e.g.  CoregistSLC_init_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_-0007
      e.g.  CoregistSLC_init_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_-0007
      e.g.  CoregistSLC_init_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
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
    rslcDir     = scratchDir + '/' + projectName + "/RSLC"
    workDir    = processDir + '/' + igramDir   

    if INF=='IFG' or INF =='IFGRAM':
        Suffix=['']
    elif INF=='MAI':
        Suffix=['.F','.B']
    elif INF=='RSI':
        Suffix=['.HF','.LF']
    else:
        print "The folder name %s cannot be identified !" % igramDir
        usage();sys.exit(1)

#################################  Define coregistration parameters ##########################
    templateContents=read_template(templateFile)

    if 'Coreg_Coarse'          in templateContents: coregCoarse = templateContents['Coreg_Coarse']                
    else: coregCoarse = 'both' 
        
    if 'rlks4cor'          in templateContents: rlks4cor = templateContents['rlks4cor']                
    else: rlks4cor = '4'
    if 'azlks4cor'          in templateContents: azlks4cor = templateContents['azlks4cor']                
    else: azlks4cor = '4'  
        
    if 'rwin4cor'          in templateContents: rwin4cor = templateContents['rwin4cor']                
    else: rwin4cor = '256'  
    if 'azwin4cor'          in templateContents: azwin4cor = templateContents['azwin4cor']                
    else: azwin4cor = '256'      
    if 'rsample4cor'          in templateContents: rsample4cor = templateContents['rsample4cor']                
    else: rsample4cor = '16'  
    if 'azsample4cor'          in templateContents: azsample4cor = templateContents['azsample4cor']                
    else: azsample4cor = '32'  
        
    if ' rpos4cor'          in templateContents:  rpos4cor = templateContents[' rpos4cor']                
    else:  rpos4cor = ' - '  
    if 'azpos4cor'          in templateContents: azpos4cor = templateContents['azpos4cor']                
    else: azpos4cor = ' - '  
        

        
    if 'rfwin4cor'          in templateContents: rfwin4cor = templateContents['rfwin4cor']                
    else: rfwin4cor = str(int(int(rwin4cor)/2))
    if 'azfwin4cor'          in templateContents: azfwin4cor = templateContents['azfwin4cor']                
    else: azfwin4cor = str(int(int(azwin4cor)/2))  
    if 'rfsample4cor'          in templateContents: rfsample4cor = templateContents['rfsample4cor']                
    else: rfsample4cor = str(2*int(rsample4cor))  
    if 'azfsample4cor'          in templateContents: azfsample4cor = templateContents['azfsample4cor']                
    else: azfsample4cor = str(2*int(azsample4cor))  
        
    if 'thresh4cor'          in templateContents: thresh4cor = templateContents['thresh4cor']                
    else: thresh4cor = ' - ' 
   
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    
# input files definition
    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

    MslcImg = rslcDir +'/'+ Mdate + ".rslc"
    MslcPar = rslcDir +'/'+ Mdate + ".rslc.par"
    SslcImg = rslcDir +'/'+ Sdate + ".rslc"
    SslcPar = rslcDir +'/'+ Sdate + ".rslc.par"
    
    
# output files of coregistration

    off = workDir + "/" + IFGPair + ".init_off"
    offs = workDir + "/" + IFGPair +".offs"
    snr = workDir + "/" + IFGPair +".snr"
    offsets = workDir + "/" + IFGPair + ".offsets"
    coffs = workDir + "/" + IFGPair + ".coffs"
    coffsets = workDir + "/" + IFGPair + ".coffsets"
    off_std = workDir + "/" + IFGPair + ".off_std"

###################################  start to coregistrate ##########################################
    if os.path.isfile(off):
        os.remove(off)
 


    call_str = "$GAMMA_BIN/create_offset " + MslcPar + " " + SslcPar + " " + off + " 1 - - 0"
    os.system(call_str)

    if coregCoarse == 'both':
        print 'init offset estimation by both orbit and ampcor'
        call_str = '$GAMMA_BIN/init_offset_orbit '+ MslcPar + ' ' + SslcPar + ' ' + off
        os.system(call_str)

        call_str = '$GAMMA_BIN/init_offset '+ MslcImg + ' ' + SslcImg + ' ' + MslcPar + ' ' + SslcPar + ' ' + off + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
        os.system(call_str)
        
        call_str = '$GAMMA_BIN/init_offset '+ MslcImg + ' ' + SslcImg + ' ' + MslcPar + ' ' + SslcPar + ' ' + off + ' 1 1 - - '
        os.system(call_str)

    elif coregCoarse == 'orbit':
        print 'init offset estimation by orbit only'
        
        call_str = '$GAMMA_BIN/init_offset_orbit '+ MslcPar + ' ' + SslcPar + ' ' + off
        os.system(call_str)
    
    elif coregCoarse == 'ampcor':
        print 'init offset estimation by ampcor only'
        
        call_str = '$GAMMA_BIN/init_offset '+ MslcImg + ' ' + SslcImg + ' ' + MslcPar + ' ' + SslcPar + ' ' + off + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
        os.system(call_str)
        
        call_str = '$GAMMA_BIN/init_offset '+ MslcImg + ' ' + SslcImg + ' ' + MslcPar + ' ' + SslcPar + ' ' + off + ' 1 1 - - '
        os.system(call_str)
        
######################## 1st time  ############################

    call_str = "$GAMMA_BIN/offset_pwr " + MslcImg + " " + SslcImg + " " + MslcPar + " " + SslcPar + " " + off + " " + offs + " " + snr + " " + rwin4cor + " " + azwin4cor + " " + offsets + " 2 "+ rsample4cor + " " + azsample4cor
    os.system(call_str)

    call_str = "$GAMMA_BIN/offset_fit " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " " + thresh4cor +" 3" 
    os.system(call_str)
    
########################  2nd time  #############################

    call_str = "$GAMMA_BIN/offset_pwr " + MslcImg + " " + SslcImg + " " + MslcPar + " " + SslcPar + " " + off + " " + offs + " " + snr + " " + rfwin4cor + " " + azfwin4cor + " " + offsets + " 2 " + rfsample4cor + " " + azfsample4cor   
    os.system(call_str)
    
    call_str = "$GAMMA_BIN/offset_fit " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " " + thresh4cor +" 4 >" + off_std 
    os.system(call_str)

    os.remove(offs)
    os.remove(snr)
    os.remove(offsets)
    os.remove(coffs)
    os.remove(coffsets)   
    
    
###############################################   Resampling      ####################################
     
    for i in range(len(Suffix)):
        if not INF=='IFG':
            MslcImg = workDir + "/" + Mdate + Suffix[i]+".slc"
            MslcPar = workDir + "/" + Mdate + Suffix[i]+".slc.par"
            SslcImg = workDir + "/" + Sdate + Suffix[i]+".slc"
            SslcPar = workDir + "/" + Sdate + Suffix[i]+".slc.par"
        
            if not ( os.path.isfile(MslcImg) and os.path.isfile(MslcPar) and os.path.isfile(SslcImg) and os.path.isfile(SslcPar) ):
                call_str = INF + '_SLC_Gamma.py ' + igramDir
                os.system(call_str)
                
        MrslcImg = workDir + "/" + Mdate + Suffix[i]+".rslc"
        MrslcPar = workDir + "/" + Mdate + Suffix[i]+".rslc.par"
        SrslcImg = workDir + "/" + Sdate + Suffix[i]+".rslc"
        SrslcPar = workDir + "/" + Sdate + Suffix[i]+".rslc.par"

        MamprlksImg = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        MamprlksPar = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        
        SamprlksImg = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        SamprlksPar = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        
######################## Resampling Slave Image ####################

        
    
        call_str = "$GAMMA_BIN/SLC_interp " + SslcImg + " " + MslcPar + " " + SslcPar + " " + off + " " + SrslcImg + " " + SrslcPar
        os.system(call_str)

        call_str = "cp " + MslcImg + " " + MrslcImg
        os.system(call_str)

        call_str = "cp " + MslcPar + " " + MrslcPar
        os.system(call_str)


####################  multi-looking for RSLC #########################################

        call_str = '$GAMMA_BIN/multi_look ' + MrslcImg + ' ' + MrslcPar + ' ' + MamprlksImg + ' ' + MamprlksPar + ' ' + rlks + ' ' + azlks
        os.system(call_str)

        call_str = '$GAMMA_BIN/multi_look ' + SrslcImg + ' ' + SrslcPar + ' ' + SamprlksImg + ' ' + SamprlksPar + ' ' + rlks + ' ' + azlks
        os.system(call_str)

        nWidth = UseGamma(MamprlksPar, 'read', 'range_samples')

        call_str = '$GAMMA_BIN/raspwr ' + MamprlksImg + ' ' + nWidth 
        os.system(call_str)  
        ras2jpg(MamprlksImg, MamprlksImg) 
        
        call_str = '$GAMMA_BIN/raspwr ' + SamprlksImg + ' ' + nWidth 
        os.system(call_str)
        ras2jpg(SamprlksImg, SamprlksImg)

    

    print "Coregistration without DEM is done!" 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
