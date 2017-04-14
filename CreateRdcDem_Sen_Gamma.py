#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   FMarch, 2017                                               #
#                                                                                 #
#         Create DEM in Radar coordinates for Sentinel-1 date                     #
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
 
              Create DEM in Radar coordinates for Sentinel-1 date

   usage:
   
            CreateRdcDem_Sen_Gamma.py igramDir
      
      e.g.  CreateRdcDem_Sen_Gamma.py IFG_PacayaT163S1A_131021-131101_0011_-0007
      e.g.  CreateRdcDem_Sen_Gamma.py MAI_PacayaT163S1A_131021-131101_0011_-0007          
      e.g.  CreateRdcDem_Sen_Gamma.py RSI_PacayaT163S1A_131021-131101_0011_-0007            
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

    
    if not os.path.isdir(processDir):
        call_str = 'mkdir ' + processDir
        os.system(call_str)

    if not os.path.isdir(workDir):
        call_str = 'mkdir ' + workDir
        os.system(call_str)
    
    simDir = scratchDir + '/' + projectName + "/PROCESS" + "/SIM" 
    if not os.path.isdir(simDir):
        call_str='mkdir ' + simDir  
        os.system(call_str)
        
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate
    if not os.path.isdir(simDir):
        call_str='mkdir ' + simDir  
        os.system(call_str)
    
    dem=templateContents['DEM']
    demPar = dem + ".par"

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
        
    if 'Start_Swath' in templateContents: SW = templateContents['Start_Swath']
    else: SW = '1'    
    if 'End_Swath' in templateContents: EW = templateContents['End_Swath']
    else: EW = '3' 
    if 'Start_Burst' in templateContents: SB = templateContents['Start_Burst']
    else: SB = '1'            
        
#  Definition of file
    MslcDir     = slcDir  + '/' + Mdate
    SslcDir     = slcDir  + '/' + Sdate
        
    MslcTOP1     = MslcDir + '/' + Mdate + '.IW1.slc.TOPS_par'   # bursts number in all of TOPS are same ? If not, should modify
    SslcTOP1     = SslcDir + '/' + Sdate + '.IW1.slc.TOPS_par'

    NB_master = UseGamma(MslcTOP1 , 'read', 'number_of_bursts:')
    NB_slave = UseGamma(SslcTOP1 , 'read', 'number_of_bursts:')    
    
    if 'End_Burst' in templateContents: EB = templateContents['End_Burst']
    else: EB = str(min(int(NB_master),int(NB_slave)))    # using the minmun number as the end of the burst number
 
    MSLC_tab     = MslcDir + '/SLC_Tab2_' + SW + EW + '_' + SB + EB 
    SSLC_tab     = SslcDir + '/SLC_Tab2_' + SW + EW + '_' + SB + EB 

    if not os.path.isfile(MSLC_tab):
        call_str= 'BurstExt_TOPS_Gamma.py ' + projectName + ' ' + Mdate + ' ' + SW + ' ' + EW + ' ' + SB + ' ' + EB
        os.system(call_str)
    
    if not os.path.isfile(SSLC_tab):
        call_str= 'BurstExt_TOPS_Gamma.py ' + projectName + ' ' + Sdate + ' ' + SW + ' ' + EW + ' ' + SB + ' ' + EB
        os.system(call_str) 
        
        
        
    MamprlksImg = MslcDir + '/'+Mdate + '.'+ SW + EW + '_' + SB + EB  + '_' + rlks + 'rlks' + '.amp'
    MamprlksPar = MslcDir + '/'+Mdate + '.'+ SW + EW + '_' + SB + EB  + '_' + rlks + 'rlks' + '.amp.par' 
    
    
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
    BLANK       = workDir + '/' + Mdate + '-' + Sdate + '.blank'

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
    
    call_str = '$GAMMA_BIN/gc_map ' + MamprlksPar + ' ' + '-' + ' ' + demPar + ' ' + dem + ' ' + UTMDEMpar + ' ' + UTMDEM + ' ' + UTM2RDC + ' ' + latovrSimphase + ' ' + lonovrSimphase + ' ' + SIMSARUTM + ' - - - - ' + PIX + ' ' + LSMAP
    os.system(call_str)
        
    createBlankFile(BLANK)

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
