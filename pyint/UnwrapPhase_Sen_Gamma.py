#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   March, 2017                                                #
#                                                                                 #
#          Unwrap and Geocoding for Sentinel-1                                    #
#                                                                                 #
###################################################################################
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
 
              Generating the differential interferograms for Sentinel-1A/B

   usage:
   
            DiffPhase_Sen_Gamma.py igramDir
      
      e.g.  DiffPhase_Sen_Gamma.py IFG_PacayaT163S1A_131021-131101_0011_-0007
      e.g.  DiffPhase_Sen_Gamma.py MAI_PacayaT163S1A_131021-131101_0011_-0007          
      e.g.  DiffPhase_Sen_Gamma.py RSI_PacayaT163S1A_131021-131101_0011_-0007            
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
    
    templateContents=read_template(templateFile)
    masterDate   =  templateContents['masterDate']
    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']

    if 'Igram_Cor_Rwin' in templateContents: rWinCor = templateContents['Igram_Cor_Rwin']
    else: rWinCor = '5'
    if 'Igram_Cor_Awin' in templateContents: aWinCor = templateContents['Igram_Cor_Awin']
    else: aWinCor = '5'

    if 'Unwrap_Flattening'          in templateContents: flatteningUnwrap = templateContents['Unwrap_Flattening']                
    else: flatteningUnwrap = 'N'

    if 'UnwrappedThreshold' in templateContents: unwrappedThreshold = templateContents['UnwrappedThreshold']
    else: unwrappedThreshold = '0.3'
    if 'Unwrap_patr' in templateContents: unwrappatrDiff = templateContents['Unwrap_patr']
    else: unwrappatrDiff = '1'
    if 'Unwrap_pataz' in templateContents: unwrappatazDiff = templateContents['Unwrap_pataz']
    else: unwrappatazDiff = '1'
        
    if 'Start_Swath' in templateContents: SW = templateContents['Start_Swath']
    else: SW = '1'    
    if 'End_Swath' in templateContents: EW = templateContents['End_Swath']
    else: EW = '3' 
    if 'Start_Burst' in templateContents: SB = templateContents['Start_Burst']
    else: SB = '1'
        
    if 'Resamp_All' in templateContents: Resamp_All = templateContents['Resamp_All']
    else: Resamp_All = '1'      
        
#  Definition of file
    MslcDir     = rslcDir  + '/' + Mdate
    SslcDir     = rslcDir  + '/' + Sdate
    masterDir     = rslcDir  + '/' + masterDate
    
    
    MamprlksImg = MslcDir  + '/' + Mdate + '_' + rlks +'rlks.amp'
    MamprlksPar = MslcDir + '/' + Mdate + '_' + rlks +'rlks.amp.par'
    
    if Resamp_All =='1':
        MamprlksImg = masterDir  + '/' + masterDate + '_' + rlks +'rlks.amp'
        MamprlksPar = masterDir + '/' + masterDate + '_' + rlks +'rlks.amp.par'
        

    SamprlksImg = workDir + '/' + Sdate  + '_' + rlks +'rlks.amp'
    SamprlksPar = workDir + '/' + Sdate + '_' + rlks +'rlks.amp.par'

    DIFF0     = workDir + '/' + Mdate + '_' + Sdate +'.diff'
    DIFFlks     = workDir + '/diff_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.int'
    DIFFFILTlks = workDir + '/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.int'
    UNWlks  =  workDir + '/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.unw'
    UNWINTERPlks = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.unw_interp'
    DIFFpar = workDir + '/' + Mdate + '-' + Sdate +'.diff_par'
    QUADFIT = workDir + '/' + Mdate + '-' + Sdate +'.quad_fit'

    CORDIFFFILTlks = workDir + '/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    MASKTHINDIFFlks  = CORDIFFFILTlks + 'maskt.bmp'

    call_str = 'cp ' + DIFF0 + ' ' + DIFFlks
    os.system(call_str)
       
         
 ###################### Filtering ####################  

    if 'Diff_FilterStrength' in templateContents: 
        strFilterStrengeh = templateContents['Diff_FilterStrength']
        fFiltLengthDiff = strFilterStrengeh.split('/')[0]
        nFiltWindowDiff = strFilterStrengeh.split('/')[1]
    else:
        fFiltLengthDiff = '-'
        nFiltWindowDiff='-'

    nWidth = UseGamma( MamprlksPar, 'read', 'range_samples:')
    nLine = UseGamma(MamprlksPar, 'read', 'azimuth_lines:')
    
    nCenterWidth = str(int(nWidth) / 2)
    nCenterLine = str(int(nLine) / 2)
    
    if 'Ref_Range' in templateContents: Ref_Range = templateContents['Ref_Range']
    else: Ref_Range = nCenterWidth
    if 'Ref_Azimuth' in templateContents: Ref_Azimuth = templateContents['Ref_Azimuth']
    else: Ref_Azimuth = nCenterLine


    call_str = '$GAMMA_BIN/adapt_filt ' + DIFFlks + ' ' + DIFFFILTlks +  ' ' + nWidth + ' ' +  fFiltLengthDiff + ' ' + nFiltWindowDiff
    os.system(call_str)

####################  Unwrap ##########################

    call_str= '$GAMMA_BIN/cc_wave ' + DIFFFILTlks + ' ' + MamprlksImg + ' - ' + CORDIFFFILTlks + ' ' + nWidth + ' ' + rWinCor + ' ' + aWinCor
    os.system(call_str)

    call_str = '$GAMMA_BIN/rascc ' + CORDIFFFILTlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - - - - - - '  
    os.system(call_str)
    ras2jpg(CORDIFFFILTlks, CORDIFFFILTlks)


    CORDIFFFILTlksbmp = CORDIFFFILTlks + '_mask.bmp'
    call_str = '$GAMMA_BIN/rascc_mask ' + CORDIFFFILTlks + ' ' + MamprlksImg + ' ' + nWidth + ' 1 1 0 1 1 ' + unwrappedThreshold + ' 0.0 0.1 0.9 1. .35 1 ' + CORDIFFFILTlksbmp   # based on diff coherence
    os.system(call_str)
    
    #call_str = '$GAMMA_BIN/rascc_mask_thinning ' + CORDIFFFILTlksbmp + ' ' + CORDIFFFILTlks + ' ' + nWidth + ' ' + MASKTHINDIFFlks + ' 5 0.3 0.4 0.5 0.6 0.7'
    #os.system(call_str)

    call_str = '$GAMMA_BIN/mcf ' + DIFFFILTlks + ' ' + CORDIFFFILTlks + ' ' + CORDIFFFILTlksbmp + ' ' + UNWlks + ' ' + nWidth + ' 1 0 0 - - ' + unwrappatrDiff + ' ' + unwrappatazDiff + ' - ' + Ref_Range + ' ' + Ref_Azimuth   #choose the reference point center
    os.system(call_str)

    #call_str = '$GAMMA_BIN/interp_ad ' + UNWlks + ' ' + UNWINTERPlks + ' ' + nWidth
    #os.system(call_str)

    #call_str = '$GAMMA_BIN/unw_model ' + DIFFFILTlks + ' ' + UNWINTERPlks + ' ' + UNWlks + ' ' + nWidth
    #os.system(call_str)

    call_str = '$GAMMA_BIN/rasrmg ' + UNWlks + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - - - - - - ' 
    os.system(call_str)

    ras2jpg(UNWlks, UNWlks)

    if flatteningUnwrap == 'Y':
        if os.path.isfile(DIFFpar):
            os.remove(DIFFpar)
            
        OUTUNWQUAD    = UNWlks.replace('.unw','.quad_fit.unw')
        call_str = '$GAMMA_BIN/create_diff_par ' + MamprlksPar + ' ' + MamprlksPar + ' ' + DIFFpar + ' 1 0'
        os.system(call_str)

        call_str = '$GAMMA_BIN/quad_fit ' + UNWlks + ' ' + DIFFpar + ' 32 32 ' + CORDIFFFILTlks + '_mask.bmp ' + QUADFIT + ' 0'
        os.system(call_str)

        call_str = '$GAMMA_BIN/quad_sub ' + UNWlks + ' ' + DIFFpar + ' ' + OUTUNWQUAD + ' 0 0'
        os.system(call_str)

        call_str = '$GAMMA_BIN/rasrmg ' + OUTUNWQUAD + ' ' + MamprlksImg + ' ' + nWidth + ' - - - - - - - - - - ' 
        os.system(call_str)

        ras2jpg(OUTUNWQUAD, OUTUNWQUAD)


    print "Unwrapping for S1 interferogram is done !"
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
