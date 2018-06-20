#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   February, 2017                                             #
#                                                                                 #
#   Coregistration of SAR images based on cross-correlation with DEM assisstance  #
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
 
       Coregistration of SAR images based on cross-correlation by using GAMMA.
       With or without DEM assisstance can be chosen.

   usage:
   
            CreateRdcDem_Gamma.py igramDir
      
      e.g.  CreateRdcDem_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_-0007
      e.g.  CreateRdcDem_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_-0007          
      e.g.  CreateRdcDem_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_-0007            
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
  
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate
    if not os.path.isdir(simDir):
        call_str='mkdir ' + simDir  
    
    dem=templateContents['DEM']
    demPar = dem + ".par"
    
    if INF=='IFG':
        Suffix=['']
    elif INF=='MAI':
        Suffix=['.F','.B']
    elif INF=='RSI':
        Suffix=['.HF','.LF']
    else:
        print "The folder name %s cannot be identified !" % igramDir
        usage();sys.exit(1)


# Parameter setting for simPhase



    if 'Simphase_Lat_Ovr'          in templateContents: latovrSimphase = templateContents['Simphase_Lat_Ovr']                
    else: latovrSimphase = '2'
    if 'Simphase_Lon_Ovr'          in templateContents: lonovrSimphase = templateContents['Simphase_Lon_Ovr']                
    else: lonovrSimphase = '2'

    if 'Simphase_rlks'          in templateContents: rlksSimphase = templateContents['Simphase_rlks']                
    else: rlksSimphase = '2'
    if 'Simphase_azlks'          in templateContents: azlksSimphase = templateContents['Simphase_azlks']                
    else: azlksSimphase = '2'
    if 'Simphase_rpos'          in templateContents: rposSimphase = templateContents['Simphase_rpos']                
    else: rposSimphase = '-'
    if 'Simphase_azpos'          in templateContents: azposSimphase = templateContents['Simphase_azpos']                
    else: azposSimphase = '-'
    if 'Simphase_patch'          in templateContents: patchSimphase = templateContents['Simphase_patch']                
    else: patchSimphase = '512'
    if 'Simphase_rwin'          in templateContents: rwinSimphase = templateContents['Simphase_rwin']                
    else: rwinSimphase = '512'
    if 'Simphase_azwin'          in templateContents: azwinSimphase = templateContents['Simphase_azwin']                
    else: azwinSimphase = '512'
    if 'Simphase_thresh'          in templateContents: threshSimphase = templateContents['Simphase_thresh']                
    else: threshSimphase = '-'

    if 'Igram_Flag_TDM' in templateContents: flagTDM = templateContents['Igram_Flag_TDM']
    else: flagTDM = 'N'

#  Definition of file
    MslcDir     = slcDir  + '/' + Mdate
    SslcDir     = slcDir  + '/' + Sdate
       
    MslcImg     = MslcDir + '/' + Mdate + '.slc'
    MslcPar     = MslcDir + '/' + Mdate + '.slc.par'
    SslcImg     = SslcDir + '/' + Sdate + '.slc'
    SslcPar     = SslcDir + '/' + Sdate + '.slc.par'
    
    MrslcImg     = workDir + '/' + Mdate + '.rslc'
    MrslcPar     = workDir + '/' + Mdate + '.rslc.par'
    SrslcImg     = workDir + '/' + Sdate + '.rslc'
    SrslcPar     = workDir + '/' + Sdate + '.rslc.par'


    BLANK       = workDir + '/' + Mdate + '-' + Sdate + '.blk'

    MamprlksImg  = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MamprlksPar  = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    SamprlksImg  = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SamprlksPar  = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    
    BASE        = workDir + '/' + Mdate + '-' + Sdate + '.bas'
    BASE_REF    = workDir + '/' + Mdate + '-' + Sdate + '.bas_ref'

    UTMDEMpar   = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.utm.dem.par'
    UTMDEM      = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.utm.dem'
    UTM2RDC     = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.utm_to_rdc'
    SIMSARUTM   = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.sim_sar_utm'
    PIX         = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.pix'
    LSMAP       = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.ls_map'
    SIMSARRDC   = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.sim_sar_rdc'
    SIMDIFFpar  = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.diff_par'
    SIMOFFS     = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.offs'
    SIMSNR      = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.snr'
    SIMOFFSET   = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.offset'
    SIMCOFF     = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.coff'
    SIMCOFFSETS = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.coffsets'
    UTMTORDC    = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.UTM_TO_RDC'
    HGTSIM      = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.rdc.dem'
    SIMUNW      = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+ rlks + 'rlks.sim_unw'


    
    if not (os.path.isdir(simDir)):
        os.makedirs(simDir)
        
    createBlankFile(BLANK)


### remove DEM look up table if it existed for considering gamma overlapping

    if os.path.isfile(UTMDEM):   
        os.remove(UTMDEM)
    if os.path.isfile(UTMDEMpar):   
        os.remove(UTMDEMpar)
    if os.path.isfile(UTM2RDC):   
        os.remove(UTM2RDC)

    nWidthUTMDEM0 = UseGamma(demPar, 'read', 'width')
    DateFormat = UseGamma(demPar, 'read', 'data_format:')
    
    if DateFormat == 'INTEGER*2':
        DF_type = '4'
    else:
        DF_type = '2'
    
        
    tmp_dem = dem + '_tmp' 
    if not os.path.isfile(tmp_dem):
        call_str = '$GAMMA_BIN/replace_values ' + dem + ' -10000 0 ' + tmp_dem + ' ' + nWidthUTMDEM0 + ' 2 ' + DF_type
        os.system(call_str)
        call_str = 'cp ' + tmp_dem + ' ' + dem
        os.system(call_str)

    if os.path.isfile(MrslcImg):
        call_str = "$GAMMA_BIN/multi_look " + MrslcImg + " " + MrslcPar + " " + MamprlksImg + " " + MamprlksPar + " " + rlks + " " + azlks
        os.system(call_str)
    else:
        call_str = "$GAMMA_BIN/multi_look " + MslcImg + " " + MslcPar + " " + MamprlksImg + " " + MamprlksPar + " " + rlks + " " + azlks
        os.system(call_str)
        

    call_str = '$GAMMA_BIN/gc_map ' + MamprlksPar + ' ' + '-' + ' ' + demPar + ' ' + dem + ' ' + UTMDEMpar + ' ' + UTMDEM + ' ' + UTM2RDC + ' ' + latovrSimphase + ' ' + lonovrSimphase + ' ' + SIMSARUTM + ' - - - - ' + PIX + ' ' + LSMAP + ' - 3 128' 
    os.system(call_str)

    nWidthUTMDEM = UseGamma(UTMDEMpar, 'read', 'width')
    nLinePWR1 = UseGamma(MamprlksPar, 'read', 'azimuth_lines')
    nWidth = UseGamma(MamprlksPar, 'read', 'range_samples')
   
    call_str = '$GAMMA_BIN/geocode ' + UTM2RDC + ' ' + SIMSARUTM + ' ' + nWidthUTMDEM + ' ' + SIMSARRDC + ' ' + nWidth + ' ' + nLinePWR1 + ' 0 0'
    os.system(call_str)

    call_str = '$GAMMA_BIN/create_diff_par ' + MamprlksPar + ' ' + MamprlksPar + ' ' + SIMDIFFpar + ' 1 < ' + BLANK
    os.system(call_str)

    call_str = '$GAMMA_BIN/init_offsetm ' + SIMSARRDC + ' ' + MamprlksImg + ' ' + SIMDIFFpar + ' ' + rlksSimphase + ' ' + azlksSimphase + ' ' + rposSimphase + ' ' + azposSimphase + ' - - - ' + patchSimphase
    os.system(call_str)

    call_str = '$GAMMA_BIN/offset_pwrm ' + SIMSARRDC + ' ' + MamprlksImg + ' ' + SIMDIFFpar + ' ' + SIMOFFS + ' ' + SIMSNR + ' ' + rwinSimphase + ' ' + azwinSimphase + ' ' + SIMOFFSET # + ' 1 - - ' + threshSimphase 
    os.system(call_str)

    call_str = '$GAMMA_BIN/offset_fitm ' + SIMOFFS + ' ' + SIMSNR + ' ' + SIMDIFFpar + ' ' + SIMCOFF + ' ' + SIMCOFFSETS + ' 0.5'
    os.system(call_str)

    call_str = '$GAMMA_BIN/gc_map_fine ' + UTM2RDC + ' ' + nWidthUTMDEM + ' ' + SIMDIFFpar + ' ' + UTMTORDC + ' 1'
    os.system(call_str)

    call_str = '$GAMMA_BIN/geocode ' + UTMTORDC + ' ' + UTMDEM + ' ' + nWidthUTMDEM + ' ' + HGTSIM + ' ' + nWidth + ' ' + nLinePWR1 + ' 0 0 - - 1 1 1'
    os.system(call_str)



    print "Create DEM in Radar Coordinates is done!"
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
