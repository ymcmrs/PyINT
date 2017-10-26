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
 
         Romoving topography phase and flattening phase from original interferogram.

   usage:
   
            diffPhase_gamma.py igramDir
      
      e.g.  diffPhase_gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_-0007
      e.g.  diffPhase_gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_-0007          
      e.g.  diffPhase_gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_-0007
      
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

    if INF=='IFG':
        Suffix=['']
    elif INF=='MAI':
        Suffix=['.F','.B']
    elif INF=='RSI':
        Suffix=['.HF','.LF']
    else:
        print "The folder name %s cannot be identified !" % igramDir
        usage();sys.exit(1)   
    
# subtract simulated interferometric phase process

# Parameter setting for diffPhase
    simDir = scratchDir + '/' + projectName + "/PROCESS" + "/SIM"   
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate
    demDir = scratchDir + '/' + projectName + "/PROCESS" + "/DEM"   
    
    
   
    if 'Igram_Cor_Rwin' in templateContents: rWinCor = templateContents['Igram_Cor_Rwin']
    else: rWinCor = '5'
    if 'Igram_Cor_Awin' in templateContents: aWinCor = templateContents['Igram_Cor_Awin']
    else: aWinCor = '5'
        

    if 'Diff_Flattening'          in templateContents: flatteningDiff = templateContents['Diff_Flattening']                
    else: flatteningDiff = 'orbit'
    if 'Diff_FilterMethod' in templateContents: strFilterMethod = templateContents['Diff_FilterMethod']
    else: strFilterMethod = "adpt_filt"
    strFilterMethodDiff = strFilterMethod
    
    if 'Diff_FilterStrength' in templateContents: 
        strFilterStrengeh = templateContents['Diff_FilterStrength']
        fFiltLengthDiff = strFilterStrengeh.split('/')[0]
        nFiltWindowDiff = strFilterStrengeh.split('/')[1]
    else:
        fFiltLengthDiff = '-'
        nFiltWindowDiff='-'
    if 'Diff_FFTLength' in templateContents: nAzfftDiff = templateContents['Diff_FFTLength']
    else: nAzfftDiff = '512'


########################   Start to process differential Interferometry ########################

    BLANK       = workDir + '/' + Mdate + '-' + Sdate + '.blk'
    createBlankFile(BLANK)
    
    SIMUNW      = simDir + '/sim_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.sim_unw'   
    HGTSIM      = demDir + '/sim_' + Mdate +'_' + rlks + 'rlks.rdc.dem'  
    GCP         = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.gcp'  
    
    for i in range(len(Suffix)):          
        MrslcImg = workDir + "/" + Mdate + Suffix[i]+".rslc"
        MrslcPar = workDir + "/" + Mdate + Suffix[i]+".rslc.par"
        SrslcImg = workDir + "/" + Sdate + Suffix[i]+".rslc"
        SrslcPar = workDir + "/" + Sdate + Suffix[i]+".rslc.par"   
        
        MamprlksImg = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        MamprlksPar = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"        
        SamprlksImg = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        SamprlksPar = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        
        OFF         = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.off'
        INT         = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.int'
        INTlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.int'
        OFFlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.off'
        FLTlks      = workDir + '/flat_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.int'
        FLTFFTlks   = FLTlks.replace('flat_', 'flat_sim_')      

        CORlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.cor'
        CORFILTlks  = workDir + '/filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.cor'

        BASE        = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.base'
        BASE_REF    = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.base_ref'
   
        DIFFpar     = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.diff.par'
    
        DIFFINTlks  = workDir + '/diff_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.int'  
        DIFFINTFFTlks = DIFFINTlks.replace('diff_', 'diff_sim_')

        CORDIFFlks = workDir+'/diff_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' +  Suffix[i] + '.cor'
        CORDIFFFILTlks = workDir+'/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.cor'
    
    
        nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')

        if os.path.isfile(DIFFpar):
            os.remove(DIFFpar)
    
        if os.path.isfile(OFFlks):    
            call_str = '$GAMMA_BIN/create_diff_par ' + OFFlks + ' ' + OFFlks + ' ' + DIFFpar + ' 0 0 '
            os.system(call_str)  
            call_str = '$GAMMA_BIN/extract_gcp ' + HGTSIM + ' ' + OFFlks + ' ' + GCP
            os.system(call_str)             
        else:
            call_str = '$GAMMA_BIN/create_diff_par ' + MamprlksPar + ' ' + MamprlksPar + ' ' + DIFFpar + ' 1 0 '
            os.system(call_str)     
        

        call_str = '$GAMMA_BIN/sub_phase ' + INTlks + ' ' + SIMUNW + ' ' + DIFFpar + ' ' + DIFFINTlks + ' 1'
        os.system(call_str)   

        if not flatteningDiff == 'orbit':
            call_str = '$GAMMA_BIN/base_est_fft ' + DIFFINTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE_REF + ' ' + nAzfftDiff 
            os.system(call_str)   

            call_str = '$GAMMA_BIN/ph_slope_base ' + DIFFINTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE_REF + ' ' + DIFFINTFFTlks 
            os.system(call_str)
            
            DIFFINTlks = DIFFINTFFTlks
            call_str = '$GAMMA_BIN/base_add ' + BASE + ' ' + BASE_REF + ' ' + BASE + '.tmp'
            os.system(call_str)

            os.rename(BASE+'.tmp', BASE)

        call_str = '$GAMMA_BIN/rasmph_pwr ' + DIFFINTlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - 2.0 0.3 - '
        os.system(call_str)
        ras2jpg(DIFFINTlks, DIFFINTlks)

        DIFFINTFILTlks = DIFFINTlks.replace('diff_', 'diff_filt_')
        call_str = '$GAMMA_BIN/adf ' + DIFFINTlks + ' ' + DIFFINTFILTlks + ' ' + CORFILTlks + ' ' + nWidth + ' 0.5'
        os.system(call_str)
      
        if strFilterMethodDiff == 'adapt_filt':
            call_str = '$GAMMA_BIN/adapt_filt ' + DIFFINTlks + ' ' + DIFFINTFILTlks + ' ' + nWidth + ' ' + fFiltLengthDiff + ' ' + nFiltWindowDiff
            os.system(call_str)
        
################ calculate coherence based on differential interferogram ####################################

        call_str = '$GAMMA_BIN/cc_wave '+ DIFFINTlks + ' ' + MamprlksImg + ' ' + SamprlksImg + ' ' + CORDIFFlks + ' ' + nWidth + ' ' + rWinCor + ' ' + aWinCor
        os.system(call_str) 
   
        call_str = '$GAMMA_BIN/rascc ' + CORDIFFlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - - - - - - '  
        os.system(call_str)
        ras2jpg(CORDIFFlks, CORDIFFlks)
      
        call_str = '$GAMMA_BIN/cc_wave '+ DIFFINTFILTlks + ' ' + MamprlksImg + ' ' + SamprlksImg + ' ' + CORDIFFFILTlks + ' ' + nWidth + ' ' + rWinCor + ' ' + aWinCor
        os.system(call_str)
       
        call_str = '$GAMMA_BIN/rascc ' + CORDIFFFILTlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - - - - - - '  
        os.system(call_str)
        ras2jpg(CORDIFFFILTlks, CORDIFFFILTlks)
      
        call_str = '$GAMMA_BIN/rasmph_pwr ' + DIFFINTFILTlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - 2.0 0.3 - ' 
        os.system(call_str)
        ras2jpg(DIFFINTFILTlks, DIFFINTFILTlks)
        
    print "Subtraction of topography and flattening phase is done!"
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
