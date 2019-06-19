#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   June, 2019                                                #
#                                                                                #
#           Generate SLC from SAR_IMS_P1 data                                    #
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
        f.close
        
def rm(TXT):
    call_str = 'rm ' + TXT
    os.system(call_str)        

def usage():
    print('''
******************************************************************************************************
 
                 Generate SLC and SLC_par file for ERS/ENVISAT  (SAR_IMS_1P format)

   usage:
   
            Down2SLC_ERS.py ProjectName DownName 
      
      e.g.  Down2SLC_ERS.py CotopaxiT120ERSA 910101
      
*******************************************************************************************************
    ''')   
    
def main(argv):
    
    if len(sys.argv)==3:
        projectName = sys.argv[1]
        Date  = sys.argv[2]
    else:
        usage();sys.exit(1)
         
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + '/' + projectName + '.template'
    templateContents=read_template(templateFile)

    if 'rlks4cor'          in templateContents: rlks4cor = templateContents['rlks4cor']                
    else: rlks4cor = '4'
    if 'azlks4cor'          in templateContents: azlks4cor = templateContents['azlks4cor']                
    else: azlks4cor = '4'  
    
    if 'rwin4cor'          in templateContents: rwin4cor = templateContents['rwin4cor']                
    else: rwin4cor = '128'  
    if 'azwin4cor'          in templateContents: azwin4cor = templateContents['azwin4cor']                
    else: azwin4cor = '128'      
    if 'rsample4cor'          in templateContents: rsample4cor = templateContents['rsample4cor']                
    else: rsample4cor = '64'  
    if 'azsample4cor'          in templateContents: azsample4cor = templateContents['azsample4cor']                
    else: azsample4cor = '64'  
        
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
    else: thresh4cor = ' 0.2 ' 
    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    
    
    projectDir = scratchDir + '/' + projectName 
    downDir    = scratchDir + '/' + projectName + "/DOWNLOAD"
    slcDir     = scratchDir + '/' + projectName + '/SLC'
    
    if not os.path.isdir(slcDir):
        call_str= 'mkdir ' +slcDir
        os.system(call_str)
    os.chdir(downDir)
    
    t0 = 't0_' + Date
    call_str = 'ls  >' + t0
    os.system(call_str)

    tt = 'tt_' + Date
    call_str = "grep " + Date + ' ' + t0 + '> ' + tt
    os.system(call_str)
    
    te = 'te_' + Date
    call_str = "grep SAR_IMS_1P " + tt + " > " + te 
    os.system(call_str)
    
    AA= np.loadtxt(te,dtype=np.str)
    Na = AA.size
    AA=AA.reshape(Na,)
    
    for i in range(Na):
        Date0 = Date+'_' + str(i)
        downName = str(AA[i]) 
        FileDir = downDir + '/' + downName
        call_str = 'par_ASAR '+ FileDir + ' ' + Date0
        os.system(call_str)
        
        call_str ="rename 's/VV.SLC/slc/g' *"
        os.system(call_str)
        
        slcpar = Date0 + '.slc.par'
        call_str = 'ERS_orb_cor_par.py ' + slcpar
        os.system(call_str)
 
    Date0 = Date
    if len(Date)==6:
        Date6 = Date
        Date0 = Date
    elif len(Date)==8:
        Date0 = Date[2:8]
        Date6 = Date[2:8]
    else:
        print('The input Date is invalid.')
        sys.exit(1)
    
    dataDir = slcDir + '/' + Date0
    if not os.path.isdir(dataDir):
        call_str = 'mkdir ' + dataDir
        print('Generate SLC dir for date: ' + Date0)
        os.system(call_str)
    call_str = 'mv ' + Date + '*.slc* ' + dataDir
    os.system(call_str)
    
    os.chdir(dataDir)
    for i in range(Na):
        Date0 = Date+'_' + str(i)
        downName = str(AA[i]) 
        
        SLCm = Date0 +  '.slc'
        SLCm_par = Date0 +  '.slc.par'
        MamprlksImg = Date0 + '.amp'
        MamprlksPar = Date0 + '.amp.par'
       
        call_str = 'multi_look ' + SLCm + ' ' + SLCm_par + ' ' + MamprlksImg + ' ' + MamprlksPar + ' ' + rlks + ' ' + azlks
        os.system(call_str)
        nWidth = UseGamma(MamprlksPar, 'read', 'range_samples')
        call_str = 'raspwr ' + MamprlksImg + ' ' + nWidth 
        os.system(call_str)  
    
    SLC = Date6+'.slc'
    SLCPAR = Date6 + '.slc.par'
    AMP = Date6+'.amp'
    AMPPAR = Date6+'.amp.par'
    if Na==1:
        os.rename(SLCm,SLC)
        os.rename(SLCm_par,SLCPAR)
        os.rename(MamprlksImg,AMP)
        os.rename(MamprlksPar,AMPPAR)
    
    for i in range(Na-1):
        if i==0:
            DateA = Date + '_0'
        else:
            DateA = Date + '_' + str(i-1) + str(i)
        
        SLCA = DateA + '.slc'
        SLCA_par = DateA + '.slc.par'
        
        
        DateB = Date + '_' +str(i+1)
        SLCB  = DateB + '.slc'
        SLCB_par = DateB + '.slc.par'
        
        DateC = Date + '_' + str(i) + str(i+1)
        SLCC  = DateC + '.slc'
        SLCC_par = DateC + '.slc.par'
        
        #####################################################################################
        MamprlksImg = Date + '.amp'
        MamprlksPar = Date + '.amp.par'
        
        off = DateC + '.off'
        offs = DateC + '.offs'
        offsets = DateC + '.offsets'
        coffs = DateC + '.coffs'
        coffsets = DateC + '.coffsets'
        snr = DateC + '.snr'
        off_std = DateC + '.off_std'
        
        ########################## Generate off file #############################
        
        call_str = "create_offset " + SLCA_par + " " + SLCB_par + " " + off + " 1 - - 0"
        os.system(call_str)
        call_str = 'init_offset_orbit '+ SLCA_par + " " + SLCB_par + ' ' + off
        os.system(call_str)
        
        
        call_str = 'init_offset '+ SLCA + ' ' + SLCB + ' ' + SLCA_par + ' ' + SLCB_par + ' ' + off + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
        os.system(call_str)

        call_str = 'init_offset '+ SLCA + ' ' + SLCB + ' ' + SLCA_par + ' ' + SLCB_par + ' ' + off + ' 1 1 - - '
        os.system(call_str)

        call_str = "offset_pwr " + SLCA + " " + SLCB + " " + SLCA_par + " " + SLCB_par + " " + off + " " + offs + " " + snr + " " + rwin4cor + " " + azwin4cor + " " + offsets + " 2 "+ rsample4cor + " " + azsample4cor
        os.system(call_str)

        call_str = "offset_fit " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " " + thresh4cor +" 3"
        os.system(call_str)

        call_str = "offset_pwr " +SLCA + " " + SLCB + " " + SLCA_par + " " + SLCB_par + " " + off + " " + offs + " " + snr + " " + rfwin4cor + " " + azfwin4cor + " " + offsets + " 2 " + rfsample4cor + " " + azfsample4cor
        os.system(call_str)

        call_str = "offset_fit " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " " + thresh4cor + " 4 >" + off_std
        os.system(call_str)

       ########################################################################################      
        
        call_str = 'SLC_cat ' + SLCA + ' ' + SLCB + ' ' + SLCA_par + ' ' + SLCB_par + ' ' + off + ' ' + SLCC + ' ' + SLCC_par
        os.system(call_str)
        
        if i==(Na-2):
            if len(Date)==6:
                DD = Date
            else:
                DD = Date[2:8]
            SLCm = DD + '.slc'
            SLCm_par = DD + '.slc.par'
            
            
            call_str = 'cp ' + SLCC + ' ' + SLCm
            os.system(call_str)
            
            call_str = 'cp ' + SLCC_par + ' ' + SLCm_par
            os.system(call_str)
            
            call_str = 'multi_look ' + SLCm + ' ' + SLCm_par + ' ' + MamprlksImg + ' ' + MamprlksPar + ' ' + rlks + ' ' + azlks
            os.system(call_str)
            nWidth = UseGamma(MamprlksPar, 'read', 'range_samples')
            call_str = 'raspwr ' + MamprlksImg + ' ' + nWidth 
            os.system(call_str)  

    call_str = 'rm *.amp'
    os.system(call_str)
    
    call_str = 'rm *_*.slc'
    os.system(call_str)
    
    print("Down to SLC for %s is done! " % Date)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
