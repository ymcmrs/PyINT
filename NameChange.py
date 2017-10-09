#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   Mar, 2017                                                  #
#                                                                                 #
#         Select Interferometry-Pairs from time series SAR images                  #
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


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def add_zero(s):
    if len(s)==1:
        s="000"+s
    elif len(s)==2:
        s="00"+s
    elif len(s)==3:
        s="0"+s
    return s


def usage():
    print '''
******************************************************************************************************
 
           Select interferometry pairs from time series SAR images
     
      usage:
   
            NameChange.py ProjectName
      
      e.g.  NameChange.py PacayaT163TsxHhA
          
            
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: projectName=sys.argv[1]        
    else:
        usage();sys.exit(1)
        
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    
    if not os.path.isdir(processDir):
        call_str = 'mkdir ' + processDir
        os.system(call_str)
    
    
    if 'JOB'  in templateContents: JOB = templateContents['JOB']                
    else: JOB = 'IFG' 
    
    INF=JOB    
    if INF=='IFG':
        Suffix=['']
        print "Time series interferograms will be processed!"
    elif INF=='MAI':
        Suffix=['.F','.B']
        print "Time series multi-aperture interferograms will be processed!"
    elif INF=='RSI':
        Suffix=['.HF','.LF']
        print "Time series range split-spectrum interferograms will be processed!"
    else:
        print "The folder name %s cannot be identified !" % igramDir
        usage();sys.exit(1)

# define files    
    
    SLC_Tab = processDir + "/SLC_Tab"
    TS_Berp = processDir + "/TS_Berp"
    TS_Itab = processDir + "/TS_Itab"
    itab_type = '1'
    pltflg = '0'
    
    if 'Max_Spacial_Baseline'  in templateContents: MaxSB=templateContents['Max_Spacial_Baseline']
    else:
        print "Max_Spacial_Baseline is not found in template!! "
        print "500m is chosen as the threshold for spatial baseline!"
        MaxSB = '500'
        
    if 'Max_Temporal_Baseline'  in templateContents: MaxTB=templateContents['Max_Temporal_Baseline']
    else:
        print "Max_Temporal_Baseline is not found in template!! "
        print "500 days is chosen as the threshold for temporal baseline!"
        MaxTB = '500'
    
    
#  extract available SAR images slc and slc_par    
    ListSLC = os.listdir(slcDir)
    Datelist = []
    SLCfile = []
    SLCParfile = []
    
    print "All of the available SAR acquisition datelist is :"  
    for kk in range(len(ListSLC)):
        if ( is_number(ListSLC[kk]) and len(ListSLC[kk])==6 ):    #  if SAR date number is 8, 6 should change to 8.
            DD=ListSLC[kk]
            Year=int(DD[0:2])
            Month = int(DD[2:4])
            Day = int(DD[4:6])
            if  ( 0 < Year < 20 and 0 < Month < 13 and 0 < Day < 32 ):            
                Datelist.append(ListSLC[kk])
                print ListSLC[kk]
                DateDir = slcDir+'/'+ListSLC[kk]
                SLC0 = glob.glob(DateDir+'/*slc')[0]
                SLCPar0 = glob.glob(DateDir+'/*slc.par')[0]
                
                str_slc = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc"
                str_slc_par = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc.par"
                
                call_str = 'mv ' + SLC0 + ' ' + str_slc
                os.system(call_str)
                
                call_str = 'mv ' + SLCPar0 + ' ' + str_slc_par
                os.system(call_str)
                                
                SLCfile.append(str_slc)
                SLCParfile.append(str_slc_par)
    

    print "Change name of SLC file is done! "
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])

    
