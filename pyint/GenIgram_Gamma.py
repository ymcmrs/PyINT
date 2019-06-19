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
        call_str = 'geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 1'
    else:
        call_str = 'geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 0'
    os.system(call_str)
    

def createBlankFile(strFile):
    f = open(strFile,'w')
    for i in range (10):
        f.write('\n')
    f.close()


def usage():
    print('''
******************************************************************************************************
 
          Generateing Interferograms based on GAMMA

   usage:
   
            GenIgram_Gamma.py igramDir
      
      e.g.  GenIgram_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_-0007
      e.g.  GenIgram_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_-0007          
      e.g.  GenIgram_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_-0007
      
*******************************************************************************************************
    ''')   
    
    
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
    rslcDir     = scratchDir + '/' + projectName + "/RSLC"
    
    if INF=='IFG' or INF=='IFGRAM':
        Suffix=['']
    elif INF=='MAI':
        Suffix=['.F','.B']
    elif INF=='RSI':
        Suffix=['.HF','.LF']
    else:
        print("The folder name %s cannot be identified !" % igramDir)
        usage();sys.exit(1)

#################################  Define Interferometry parameters ##########################
    templateContents=read_template(templateFile)
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    
# Parameter setting for Igram

    if 'Igram_Rlooks'          in templateContents: rLooksIgram = templateContents['Igram_Rlooks']                
    else: rLooksIgram = '4'
    if 'Igram_Alooks'          in templateContents: aLooksIgram = templateContents['Igram_Alooks']                
    else: aLooksIgram = '4'
    if 'Unify_master '          in templateContents: Unify_master  = templateContents['Unify_master']                
    else: Unify_master  = '0'
    
    if 'Igram_Spsflg'       in templateContents: spsflgIgram = templateContents['Igram_Spsflg']
    else: spsflgIgram = '1'
    if 'Igram_Azfflg'       in templateContents: azfflgIgram = templateContents['Igram_Azfflg']
    else: azfflgIgram = '1'
    if 'Igram_Rp1flg'       in templateContents: rp1flgIgram = templateContents['Igram_Rp1flg']
    else: rp1flgIgram = '1'
    if 'Igram_Rp2flg'       in templateContents: rp2flgIgram = templateContents['Igram_Rp2flg']
    else: rp2flgIgram = '1'
    if 'Igram_Flag_TDM' in templateContents: flagTDM = templateContents['Igram_Flag_TDM']
    else: flagTDM = 'N'
    if 'Igram_Cor_Rwin' in templateContents: rWinCor = templateContents['Igram_Cor_Rwin']
    else: rWinCor = '5'
    if 'Igram_Cor_Awin' in templateContents: aWinCor = templateContents['Igram_Cor_Awin']
    else: aWinCor = '5'
    if 'Igram_Flattening' in templateContents: flatteningIgram = templateContents['Igram_Flattening']
    else: flatteningIgram = 'orbit'
    if 'Igram_FilterMethod' in templateContents: strFilterMethod = templateContents['Igram_FilterMethod']
    else: strFilterMethod = 'adapt_filt'
    if 'Igram_FilterStrength' in templateContents: strFilterStrengeh = templateContents['Igram_FilterStrength']
    else: strFilterStrengeh = '0.8/4'
    fFiltLength = strFilterStrengeh.split('/')[0]
    nFiltWindow = strFilterStrengeh.split('/')[1]
    if 'Igram_FFTLength' in templateContents: nAzfft = templateContents['Igram_FFTLength']
    else: nAzfft = '512'
        
    if 'Coreg_int'          in templateContents: Coreg_int = templateContents['Coreg_int']                
    else: Coreg_int = '1'

###############################  Interferometry Processing ####################################################
    BLANK       = workDir + '/' + Mdate + '-' + Sdate + '.blk'
    
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
### start generation of interferogram with coregistered master and slave in each pair


        if os.path.isfile(OFF):
            os.remove(OFF)

        if not Coreg_int=='1':
            MrslcImg = rslcDir + "/" + Mdate + Suffix[i]+".rslc"
            MrslcPar = rslcDir + "/" + Mdate + Suffix[i]+".rslc.par"
            SrslcImg = rslcDir + "/" + Sdate + Suffix[i]+".rslc"
            SrslcPar = rslcDir + "/" + Sdate + Suffix[i]+".rslc.par" 
        
        call_str = 'create_offset '+ MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' 1 - - 0'
        os.system(call_str)

        call_str = 'SLC_intf '+ MrslcImg + ' ' + SrslcImg + ' ' + MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' ' + INT + ' 1 1 - - ' + spsflgIgram + ' ' + azfflgIgram + ' ' + rp1flgIgram + ' ' + rp2flgIgram
        os.system(call_str)

### start co-registartion of raw interferogram w.r.t. master scene  

        #if Unify_master  == '1':
        #    call_str = "Resamp_all_Gamma.py " + igramDir     ## after this step, all based on rslc
        #    os.system(call_str)

### continue interferometric process with re-coregistered slc parameter w.r.t. master scene

        #if os.path.isfile(OFF):
        #    os.remove(OFF)
            
        #call_str = 'create_offset '+ MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' 1 - - 0'
        #os.system(call_str)    ## update the OFF file, if do the last step "COREG_all_Flag"

        call_str = 'base_orbit '+ MrslcPar + ' ' + SrslcPar + ' ' + BASE
        os.system(call_str)

#    if flagTDM == 'Y':    ### flag for TanDEM-X bistatic mode case to conside half length of baseline
#        call_str = '$INT_SCR/halfbase.pl ' + BASE;
#        os.system(call_str)

        call_str = 'multi_cpx '+ INT + ' ' + OFF + ' ' + INTlks + ' ' + OFFlks + ' ' + rlks + ' ' + azlks
        os.system(call_str)
########################    flatten phase remove ################################
   
        call_str = 'ph_slope_base '+ INTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE + ' ' + FLTlks
        os.system(call_str)

        nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')

        call_str = 'cc_wave '+ INTlks + ' ' + MamprlksImg + ' ' + SamprlksImg + ' ' + CORlks + ' ' + nWidth + ' ' + rWinCor + ' ' + aWinCor
        os.system(call_str)
        
        call_str = 'rascc ' + CORlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - - - - - - '  
        os.system(call_str)
        ras2jpg(CORlks, CORlks)

        #if flatteningIgram == 'fft':
        #    call_str = 'base_est_fft ' + FLTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE_REF + ' ' + nAzfft 
        #    os.system(call_str)

        #    call_str = 'ph_slope_base ' + FLTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE_REF + ' ' + FLTFFTlks  
        #    os.system(call_str)

        #   FLTlks = FLTFFTlks
        #   call_str = 'base_add ' + BASE + ' ' + BASE_REF + ' ' + BASE + '.tmp'
        #   os.system(call_str)     
        #    os.rename(BASE+'.tmp', BASE)
          
        # FLTFILTlks = FLTlks.replace('flat_', 'filt_')
        
########################    filtering  ################################
        #call_str = 'rasmph_pwr ' + FLTlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - 2.0 0.3 - ' 
        #os.system(call_str)
        #ras2jpg(FLTlks, FLTlks)

        #call_str = 'adf ' + FLTlks + ' ' + FLTFILTlks + ' ' + CORFILTlks + ' ' + nWidth + ' 0.5'
        #os.system(call_str)

        #if strFilterMethod == 'adapt_filt':    
        #    call_str = 'adapt_filt ' + FLTlks + ' ' + FLTFILTlks + ' ' + nWidth + ' ' + fFiltLength + ' ' + nFiltWindow
        #    os.system(call_str)
        
        #call_str = 'cc_wave '+ FLTFILTlks + ' ' + MamprlksImg + ' ' + SamprlksImg + ' ' + CORFILTlks + ' ' + nWidth + ' ' + rWinCor + ' ' + aWinCor
        #os.system(call_str)
             
        #call_str = 'rasmph_pwr ' + FLTFILTlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - 2.0 0.3 - ' 
        #os.system(call_str)
        #ras2jpg(FLTFILTlks, FLTFILTlks)
        
        #call_str = 'rascc ' + CORFILTlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - - - - - - '  
        #os.system(call_str)
        #ras2jpg(CORFILTlks, CORFILTlks)

    print("Interferogram generation is done!")
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
