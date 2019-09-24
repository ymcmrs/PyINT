#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact : ymcmrs@gmail.com                               ### 
#################################################################
import numpy as np
import os
import sys  
import argparse

from pyint import _utils as ut

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate radar-coordinates based DEM.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='Name of project.')
    inps = parser.parse_args()
    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  

   Generate radar-coordinates based DEM.
   [Geo-coordinates DEM can be downloaded automatically if not provided.]
'''

EXAMPLE = """Usage:
  
  generate_rdc_dem.py projectName
  
------------------------------------------------------------------- 
"""
    
def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName

    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)

    Mdate =  templateDict['masterDate']

    DEMDir = os.getenv('DEMDIR')
    
    processDir = scratchDir + '/' + projectName + "/ifgrams"
    slcDir     = scratchDir + '/' + projectName + "/SLC" 
    
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']

    if not os.path.isdir(processDir):
        call_str = 'mkdir ' + processDir
        os.system(call_str)
        
    simDir = scratchDir + '/' + projectName + "/DEM" 
    if not os.path.isdir(simDir):
        call_str='mkdir ' + simDir  
  
       
    workDir = simDir
    
    if 'DEM' in templateDict: 
        dem = templateDict['DEM'] 
        if not os.path.isfile(dem):
            dem = DEMDir + '/' + projectName + '/' + projectName + '.dem' 
            call_str = 'echo DEM= ' + dem + ' >> ' + templateFile
            os.system(call_str)
            templateDict['DEM'] = dem
    else: 
        dem = DEMDir + '/' + projectName + '/' + projectName + '.dem'
        call_str = 'echo DEM = ' + dem + ' >> ' + templateFile
        os.system(call_str)
    
    demPar = dem + ".par"
    
    if not os.path.isfile(dem):
        call_str = 'makedem_pyint.py ' + projectName
        os.system(call_str)
    
# Parameter setting for simPhase
    latovrSimphase = templateDict['dem_lat_ovr']
    lonovrSimphase = templateDict['dem_lon_ovr']
    
    rposSimphase = templateDict['Simphase_rpos']   
    azposSimphase = templateDict['Simphase_azpos']  
    rwinSimphase = templateDict['Simphase_rwin'] 
    azwinSimphase = templateDict['Simphase_azwin'] 
    #rwinSimphase = '128'
    #azwinSimphase = '128'

    threshSimphase = templateDict['Simphase_thresh']

#  Definition of file
    MslcDir     = slcDir  + '/' + Mdate     
    MslcImg     = MslcDir + '/' + Mdate + '.slc'
    MslcPar     = MslcDir + '/' + Mdate + '.slc.par'
    OFFSTD = workDir + '/' + Mdate + '_dem.off_std'
    

    BLANK       = workDir + '/' + Mdate + '.blk'
    MamprlksImg  = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MamprlksPar  = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp.par'


    UTMDEMpar   = simDir + '/'+ Mdate + '_'+ rlks + 'rlks.utm.dem.par'
    UTMDEM      = simDir + '/' + Mdate + '_'+ rlks + 'rlks.utm.dem'
    UTM2RDC     = simDir + '/' + Mdate + '_'+ rlks + 'rlks.utm_to_rdc0'
    SIMSARUTM   = simDir + '/' + Mdate + '_'+ rlks + 'rlks.sim_sar_utm'
    PIX         = simDir + '/' + Mdate + '_'+ rlks + 'rlks.pix'
    LSMAP       = simDir + '/' + Mdate + '_'+ rlks + 'rlks.ls_map'
    SIMSARRDC   = simDir + '/' + Mdate + '_'+ rlks + 'rlks.sim_sar_rdc'
    SIMDIFFpar  = simDir + '/' + Mdate + '_'+ rlks + 'rlks.diff_par'
    SIMOFFS     = simDir + '/' + Mdate + '_'+ rlks + 'rlks.offs'
    SIMSNR      = simDir + '/' + Mdate + '_'+ rlks + 'rlks.snr'
    SIMOFFSET   = simDir + '/' + Mdate + '_'+ rlks + 'rlks.offset'
    SIMCOFF     = simDir + '/' + Mdate + '_'+ rlks + 'rlks.coff'
    SIMCOFFSETS = simDir + '/' + Mdate + '_'+ rlks + 'rlks.coffsets'
    UTMTORDC    = simDir + '/' + Mdate + '_'+ rlks + 'rlks.UTM_TO_RDC'
    HGTSIM      = simDir + '/' + Mdate + '_'+ rlks + 'rlks.rdc.dem'
      
    if not (os.path.isdir(simDir)):
        os.makedirs(simDir)
        
    ut.createBlankFile(BLANK)

### remove DEM look up table if it existed for considering gamma overlapping

    if os.path.isfile(UTMDEM):   
        os.remove(UTMDEM)
    if os.path.isfile(UTMDEMpar):   
        os.remove(UTMDEMpar)
    if os.path.isfile(UTM2RDC):   
        os.remove(UTM2RDC)

    nWidthUTMDEM0 = ut.read_gamma_par(demPar, 'read', 'width')
    DateFormat = ut.read_gamma_par(demPar, 'read', 'data_format:')
    
    if DateFormat == 'INTEGER*2':
        DF_type = '4'
    else:
        DF_type = '2'
    
        
    tmp_dem = dem + '_tmp'
    
    if not os.path.isfile(tmp_dem):
        call_str = 'replace_values ' + dem + ' -10000 0 ' + tmp_dem + ' ' + nWidthUTMDEM0 + ' 2 ' + DF_type
        os.system(call_str)
        call_str = 'cp ' + tmp_dem + ' ' + dem
        os.system(call_str)

    call_str = "multi_look " + MslcImg + " " + MslcPar + " " + MamprlksImg + " " + MamprlksPar + " " + rlks + " " + azlks
    os.system(call_str)
        
    #call_str = 'gc_map ' + MamprlksPar + ' ' + '-' + ' ' + demPar + ' ' + dem + ' ' + UTMDEMpar + ' ' + UTMDEM + ' ' + UTM2RDC + ' ' + latovrSimphase + ' ' + lonovrSimphase + ' ' + SIMSARUTM + ' - - - - ' + PIX + ' ' + LSMAP + ' - 3 128' 
    call_str = 'gc_map ' + MamprlksPar + ' ' + '-' + ' ' + demPar + ' ' + dem + ' ' + UTMDEMpar + ' ' + UTMDEM + ' ' + UTM2RDC + ' ' + latovrSimphase + ' ' + lonovrSimphase + ' ' + SIMSARUTM + ' - - - - ' + PIX + ' ' + LSMAP + ' - 3 128' 
    os.system(call_str)

    nWidthUTMDEM = ut.read_gamma_par(UTMDEMpar, 'read', 'width')
    nLinePWR1 = ut.read_gamma_par(MamprlksPar, 'read', 'azimuth_lines')
    nWidth = ut.read_gamma_par(MamprlksPar, 'read', 'range_samples')
   
    call_str = 'geocode ' + UTM2RDC + ' ' + SIMSARUTM + ' ' + nWidthUTMDEM + ' ' + SIMSARRDC + ' ' + nWidth + ' ' + nLinePWR1 + ' 0 0'
    os.system(call_str)

    call_str = 'create_diff_par ' + MamprlksPar + ' ' + MamprlksPar + ' ' + SIMDIFFpar + ' 1 < ' + BLANK
    os.system(call_str)

    call_str = 'init_offsetm ' + SIMSARRDC + ' ' + MamprlksImg + ' ' + SIMDIFFpar + ' 2 2 ' + rposSimphase + ' ' + azposSimphase #+ ' - - - 512'
    os.system(call_str)

    call_str = 'offset_pwrm ' + SIMSARRDC + ' ' + MamprlksImg + ' ' + SIMDIFFpar + ' ' + SIMOFFS + ' ' + SIMSNR + ' ' + rwinSimphase + ' ' + azwinSimphase + ' ' + SIMOFFSET #+ ' - 128 128 ' + threshSimphase 
    os.system(call_str)

    call_str = 'offset_fitm ' + SIMOFFS + ' ' + SIMSNR + ' ' + SIMDIFFpar + ' ' + SIMCOFF + ' ' + SIMCOFFSETS + ' - > ' + OFFSTD
    os.system(call_str)

    call_str = 'gc_map_fine ' + UTM2RDC + ' ' + nWidthUTMDEM + ' ' + SIMDIFFpar + ' ' + UTMTORDC + ' 1'
    #print(call_str)
    os.system(call_str)

    call_str = 'geocode ' + UTMTORDC + ' ' + UTMDEM + ' ' + nWidthUTMDEM + ' ' + HGTSIM + ' ' + nWidth + ' ' + nLinePWR1 + ' 0 0 - - 1 1 1'
    os.system(call_str)


    print("Create DEM in Radar Coordinates is done!")

    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
