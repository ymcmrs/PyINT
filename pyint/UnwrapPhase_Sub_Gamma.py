#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   February, 2017                                             #
#                                                                                 #
#         Unwrap interferograms based on Rounding box                             #
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
    if ( inFile.rsplit('.')[1] == 'int' or inFile.rsplit('.')[1] == 'diff'):
        call_str = '$GAMMA_BIN/geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 1'
    else:
        call_str = '$GAMMA_BIN/geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 0'
    os.system(call_str)
    
def createBlankFile(strFile):
    f = open(strFile,'w')
    for i in range (10):
        f.write('\n')
    f.close()    
    
def GetSubset(Subset):
    KK = Subset.split('[')[1].split(']')[0]
    if ':' in KK:    
        Dx = Subset.split('[')[1].split(']')[0].split(',')[0]
        Dy = Subset.split('[')[1].split(']')[0].split(',')[1]
    
        x1 = Dx.split(':')[0]
        x2 = Dx.split(':')[1]
    
        y1 = Dy.split(':')[0]
        y2 = Dy.split(':')[1]
    else:
        x1 = '-'
        x2 = '-'
        y1 = '-'
        y2 = '-'
        
    return x1,x2,y1,y2      

def usage():
    print '''
******************************************************************************************************
 
          Unwrap interferograms based on GAMMA.
       

   usage:
   
            UnwrapPhase_Gamma.py igramDir
      
      e.g.  UnwrapPhase_Sub_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  UnwrapPhase_Sub_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  UnwrapPhase_Sub_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_0007          
            
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
    simDir = scratchDir + '/' + projectName + "/PROCESS" + "/SIM" 
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate
    
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
    

    if 'Igram_Flattening' in templateContents: flatteningIgram = templateContents['Igram_Flattening']
    else: flatteningIgram = 'orbit'
    if 'Topo_Flag'          in templateContents: flagTopo = templateContents['Topo_Flag']           
    else: flagTopo = 'N'
    if 'Diff_Flattening'          in templateContents: flatteningDiff = templateContents['Diff_Flattening']                
    else: flatteningDiff = 'orbit'        
    if 'Unwrap_Flattening'          in templateContents: flatteningUnwrap = templateContents['Unwrap_Flattening']                
    else: flatteningUnwrap = 'N'
    if 'UnwrappedThreshold' in templateContents: unwrappedThreshold = templateContents['UnwrappedThreshold']
    else: unwrappedThreshold = '0.3'
    if 'Unwrap_patr' in templateContents: unwrappatrDiff = templateContents['Unwrap_patr']
    else: unwrappatrDiff = '1'
    if 'Unwrap_pataz' in templateContents: unwrappatazDiff = templateContents['Unwrap_pataz']
    else: unwrappatazDiff = '1'
    
    if 'Subset_Rdc' in templateContents: 
        Subset = templateContents['Subset_Rdc']
        XX = GetSubset(Subset)
        if not XX[3] == '-':
            SRU = XX[0]
            NR = str(int(XX[1])-int(XX[0]))
            SAU= XX[2]
            NA = str(int(XX[3])-int(XX[2]))
        else:
            SRU = '-'
            NR = '-'
            SAU = '-'
            NA = '-'   
    else:
        SRU = '-'
        NR = '-'
        SAU = '-'
        NA = '-' 

#  Definition of file

    for i in range(len(Suffix)):          
        MrslcImg = workDir + "/" + Mdate + Suffix[i]+".rslc"
        MrslcPar = workDir + "/" + Mdate + Suffix[i]+".rslc.par"
        SrslcImg = workDir + "/" + Sdate + Suffix[i]+".rslc"
        SrslcPar = workDir + "/" + Sdate + Suffix[i]+".rslc.par"   
        
        MamprlksImg = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        MamprlksImg_Sub = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".sub.ramp"
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
        
        MASKTHINlks  = CORFILTlks + 'maskt.bmp'
        MASKTHINDIFFlks  = CORDIFFFILTlks + 'maskt.bmp'
    
    
        nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')
        nLine = UseGamma(OFFlks, 'read', 'interferogram_azimuth_lines')
    
        nCenterWidth = str(int(nWidth) / 2)
        nCenterLine = str(int(nLine) / 2)
    
        if 'Ref_Range' in templateContents: Ref_Range = templateContents['Ref_Range']
        else: Ref_Range = nCenterWidth
        if 'Ref_Azimuth' in templateContents: Ref_Azimuth = templateContents['Ref_Azimuth']
        else: Ref_Azimuth = nCenterLine ####  unwrapping differential interferogram ####
### if topo case, it calls FLTFILTlks
### else if diff case, it calls DIFFINTFILTlks

        if flagTopo == 'Y':
            if flatteningIgram == 'orbit':
                FLTFILTlks = FLTlks.replace('flat_', 'filt_')
            else :
                FLTFILTlks = FLTFFTlks.replace('flat_', 'filt_')
            WRAPlks = FLTFILTlks
            MASKTHIN = MASKTHINlks
            CORMASK = CORFILTlks           # using the un-filtered image as mask file
        else:
            if flatteningDiff == 'orbit':
                DIFFINTFILTlks = DIFFINTlks.replace('diff_', 'diff_filt_')    
            else:
                DIFFINTFILTlks = DIFFINTFFTlks.replace('diff_', 'diff_filt_')  
            WRAPlks = DIFFINTFILTlks
            MASKTHIN = MASKTHINDIFFlks
            CORMASK = CORDIFFFILTlks       # using the un-filtered image as mask file
            
        UWNTHINlks   = WRAPlks.replace('.int', '.sub.unw_thinned.bmp')
        UNWINTERPlks = WRAPlks.replace('.int', '.sub.unw_interp')
        UNWlks       = WRAPlks.replace('.int', '.sub.unw')
        
        if os.path.isfile(UNWlks):
            os.remove(UNWlks)

 
        # using the un-filtered image as mask file
###########################  Start to Mask   ##########################    
    
        CORMASKbmp = CORMASK + '.sub_mask.bmp'
        if os.path.isfile(CORMASKbmp):
            os.remove(CORMASKbmp)
    
        if os.path.isfile(CORMASKbmp):
            os.remove(CORMASKbmp)
            
        call_str = '$GAMMA_BIN/rascc_mask ' + CORMASK + ' ' + MamprlksImg + ' ' + nWidth + ' 1 1 0 1 1 ' + unwrappedThreshold + ' 0.0 0.1 0.9 1. .35 1 ' + CORMASKbmp   # based on int coherence
        os.system(call_str)
    

        call_str = '$GAMMA_BIN/mcf ' + WRAPlks + ' ' + CORMASK + ' ' + CORMASKbmp + ' ' + UNWlks + ' ' + nWidth + ' 1 ' + SRU + ' ' + SAU + ' ' + NR + ' ' + NA + ' ' + unwrappatrDiff + ' ' + unwrappatazDiff + ' - ' + Ref_Range + ' ' + Ref_Azimuth   #choose the reference point center
        os.system(call_str)
        

        data = np.fromfile(UNWlks, '>f4', int(nLine)*int(nWidth)).reshape(int(nLine),int(nWidth))
        data_sub = data[int(SAU):(int(SAU)+int(NA)),int(SRU):(int(SRU)+int(NR))]
        
#        if not sys.byteorder == 'big':
#            data_sub.byteswap(True)       
        data_sub.tofile(UNWlks)   
        
        
        data = np.fromfile(MamprlksImg, '>f4', int(nLine)*int(nWidth)).reshape(int(nLine),int(nWidth))
        data_sub = data[int(SAU):(int(SAU)+int(NA)),int(SRU):(int(SRU)+int(NR))]
                 
        data_sub.tofile(MamprlksImg_Sub)          

        data = np.fromfile(CORMASKbmp, '>u1', int(nLine)*int(nWidth)).reshape(int(nLine),int(nWidth))
        data_sub = data[int(SAU):(int(SAU)+int(NA)),int(SRU):(int(SRU)+int(NR))]           
        data_sub.tofile(CORMASKbmp)  
    
        
        WIDTH = NR 
#        call_str = '$GAMMA_BIN/interp_ad ' + UNWlks + ' ' + UNWINTERPlks + ' ' + nWidth
#        os.system(call_str)

#        call_str = '$GAMMA_BIN/unw_model ' + WRAPlks + ' ' + UNWINTERPlks + ' ' + UNWlks + ' ' + nWidth
#        os.system(call_str)

        call_str = '$GAMMA_BIN/rasrmg ' + UNWlks + ' ' + MamprlksImg_Sub + ' ' + WIDTH + ' - - - - - - - - - - ' 
        os.system(call_str)

        ras2jpg(UNWlks, UNWlks)
        
        
        
        
        if flatteningUnwrap == 'Y':
            if os.path.isfile(DIFFpar):
                os.remove(DIFFpar)
            
            QUADFIT       = WRAPlks.replace('.int', '.quad_fit')
            OUTUNWQUAD    = UNWlks.replace('.unw','.quad_fit.unw')
            call_str = '$GAMMA_BIN/create_diff_par ' + OFFlks + ' ' + OFFlks + ' ' + DIFFpar + ' - 0'
            os.system(call_str)

            call_str = '$GAMMA_BIN/quad_fit ' + UNWlks + ' ' + DIFFpar + ' 32 32 - ' + QUADFIT + ' 0'
            os.system(call_str)

            call_str = '$GAMMA_BIN/quad_sub ' + UNWlks + ' ' + DIFFpar + ' ' + OUTUNWQUAD + ' 0 0'
            os.system(call_str)

        
        

    print "Uwrapping interferometric phase is done!"
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
