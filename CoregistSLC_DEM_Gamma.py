#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   March, 2017                                               #
#                                                                                #
#           Coregistration of SAR images based on DEM.                           #
#         Be suitable for conventional InSAR, MAI, Split-Spectrum InSAR          # 
#                                                                                #
##################################################################################
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

def usage():
    print '''
******************************************************************************************************
 
       Coregistration of SAR images based on DEM by using GAMMA.
       Be suitable for conventional InSAR, MAI, Range Split-Spectrum InSAR.

   usage:
   
            CoregistSLC_DEM_Gamma.py igramDir
      
      e.g.  CoregistSLC_DEM_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_-0007
      e.g.  CoregistSLC_DEM_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_-0007
      e.g.  CoregistSLC_DEM_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
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

    if INF=='IFG':
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

    if 'thresh4cor'          in templateContents: thresh4cor = templateContents['thresh4cor']                
    else: thresh4cor = ' - '      
    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    
# input slcs

    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

    MslcImg = MslcDir + "/" + Mdate + ".slc"
    MslcPar = MslcDir + "/" + Mdate + ".slc.par"
    SslcImg = SslcDir + "/" + Sdate + ".slc"
    SslcPar = SslcDir + "/" + Sdate + ".slc.par"

# output slcs

    MrslcImg = workDir + "/" + Mdate + ".rslc"
    MrslcPar = workDir + "/" + Mdate + ".rslc.par"
    SrslcImg = workDir + "/" + Sdate + ".rslc"
    SrslcPar = workDir + "/" + Sdate + ".rslc.par"
    Srslc0Img = workDir + "/" + Sdate + ".rslc0"
    Srslc0Par = workDir + "/" + Sdate + ".rslc0.par"
# output multi-looked amplitude

    MamprlksImg = workDir + "/" + Mdate + "_" + rlks+"rlks.amp"	
    MamprlksPar = workDir + "/" + Mdate + "_" + rlks+"rlks.amp.par"
    SamprlksImg = workDir + "/" + Sdate + "_" + rlks+"rlks.amp"
    SamprlksPar = workDir + "/" + Sdate + "_" + rlks+"rlks.amp.par"
    
    simDir = scratchDir + '/' + projectName + "/PROCESS" + "/SIM" 
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate

    HGTSIM      = simDir + '/sim_' + Mdate + '-' + Sdate + '_'+rlks+'rlks.rdc.dem'
    
    if not os.path.isfile(HGTSIM):
        call_str= "CreateRdcDem_Gamma.py " + igramDir
        os.system(call_str)

    lt0 = workDir + "/lt0" 
    lt1 = workDir + "/lt1"
    mli0 = workDir + "/mli0" 
    diff0 = workDir + "/diff0" 
    offs0 = workDir + "/offs0"
    snr0 = workDir + "/snr0"
    offsets0 = workDir + "/offsets0"
    coffs0 = workDir + "/coffs0"
    coffsets0 = workDir + "/coffsets0"
    off = workDir + "/" + IFGPair + ".off"
    offs = workDir + "/offs"
    snr = workDir + "/snr"
    offsets = workDir + "/offsets"
    coffs = workDir + "/coffs"
    coffsets = workDir + "/coffsets"

    if os.path.isfile(diff0):
        os.remove(diff0)
    if os.path.isfile(off):
        os.remove(off)

# real processing

    call_str = "$GAMMA_BIN/multi_look " + MslcImg + " " + MslcPar + " " + MamprlksImg + " " + MamprlksPar + " " + rlks + " " + azlks
    os.system(call_str)

    call_str = "$GAMMA_BIN/multi_look " + SslcImg + " " + SslcPar + " " + SamprlksImg + " " + SamprlksPar + " " + rlks + " " + azlks
    os.system(call_str)

    
    call_str = "$GAMMA_BIN/rdc_trans " + MamprlksPar + " " + HGTSIM + " " + SamprlksPar + " " + lt0
    os.system(call_str)

    width_Mamp = UseGamma(MamprlksPar, 'read', 'range_samples')
    width_Samp = UseGamma(SamprlksPar, 'read', 'range_samples')
    line_Samp = UseGamma(SamprlksPar, 'read', 'azimuth_lines')

    call_str = "$GAMMA_BIN/geocode " + lt0 + " " + MamprlksImg + " " + width_Mamp + " " + mli0 + " " + width_Samp + " " + line_Samp + " 2 0"
    os.system(call_str)

    call_str = "$GAMMA_BIN/create_diff_par " + SamprlksPar + " - " + diff0 + " 1 0"
    os.system(call_str)

    call_str = "$GAMMA_BIN/init_offsetm " + mli0 + " " + SamprlksImg + " " + diff0 + " 1 1"
    os.system(call_str)

    call_str = "$GAMMA_BIN/offset_pwrm " + mli0 + " " + SamprlksImg + " " + diff0 + " " + offs0 + " " + snr0 + " 256 256 " + offsets0 + " 2 16 16"
    os.system(call_str)
  
    call_str = "$GAMMA_BIN/offset_fitm " + offs0 + " " + snr0 + " " + diff0 + " " + coffs0 + " " + coffsets0 + " - 4"
    os.system(call_str)

    call_str = "$GAMMA_BIN/gc_map_fine " + lt0 + " " + width_Mamp + " " + diff0 + " " + lt1
    os.system(call_str)
    
    
    call_str = "$GAMMA_BIN/SLC_interp_lt " + SslcImg + " " + MslcPar + " " + SslcPar + " " + lt1 + " " + MamprlksPar + " " + SamprlksPar + " - " + Srslc0Img + " " + Srslc0Par
    os.system(call_str)


# further refinement processing for resampled SLC

    call_str = "$GAMMA_BIN/create_offset " + MslcPar + " " + Srslc0Par + " " + off + " 1 - - 0"
    os.system(call_str)

    call_str = "$GAMMA_BIN/offset_pwr " + MslcImg + " " + Srslc0Img + " " + MslcPar + " " + Srslc0Par + " " + off + " " + offs + " " + snr + " 128 128 " + offsets + " 2 32 64"
    os.system(call_str)

    call_str = "$GAMMA_BIN/offset_fit "  + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 3" 
    os.system(call_str)
    
############################################     Resampling     ############################################    
    
    
    for i in range(len(Suffix)):
        if not INF=='IFG':
            MslcImg = workDir + "/" + Mdate + Suffix[i]+".slc"
            MslcPar = workDir + "/" + Mdate + Suffix[i]+".slc.par"
            SslcImg = workDir + "/" + Sdate + Suffix[i]+".slc"
            SslcPar = workDir + "/" + Sdate + Suffix[i]+".slc.par"
        
        MrslcImg = workDir + "/" + Mdate + Suffix[i]+".rslc"
        MrslcPar = workDir + "/" + Mdate + Suffix[i]+".rslc.par"
        SrslcImg = workDir + "/" + Sdate + Suffix[i]+".rslc"
        SrslcPar = workDir + "/" + Sdate + Suffix[i]+".rslc.par"

        
######################## Resampling Slave Image ####################

        call_str = "$GAMMA_BIN/SLC_interp_lt " + SslcImg + " " + MslcPar + " " + SslcPar + " " + lt1 + " " + MamprlksPar + " " + SamprlksPar + " " + off + " " + SrslcImg + " " + SrslcPar
        os.system(call_str)


        call_str = "cp " + MslcImg + " " + MrslcImg
        os.system(call_str)

        call_str = "cp " + MslcPar + " " + MrslcPar
        os.system(call_str)


####################  multi-looking for RSLC #########################################

        MamprlksImg = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        MamprlksPar = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        
        SamprlksImg = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        SamprlksPar = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        

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


    os.remove(lt0)
    os.remove(lt1)
    os.remove(mli0)
    os.remove(diff0)
    os.remove(offs0)
    os.remove(snr0)
    os.remove(offsets0)
    os.remove(coffs0)
    os.remove(coffsets0)
    os.remove(off)
    os.remove(offs)
    os.remove(snr)
    os.remove(offsets)
    os.remove(coffs)
    os.remove(coffsets)
    os.remove(Srslc0Img)
    os.remove(Srslc0Par)

    print "Coregistration with DEM is done!"
 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
