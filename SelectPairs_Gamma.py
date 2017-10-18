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
   
            SelectPairs_Gamma.py ProjectName
      
      e.g.  SelectPairs_Gamma.py PacayaT163TsxHhA
          
            
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
        MaxSB = '100'
        
    if 'Max_Temporal_Baseline'  in templateContents: MaxTB=templateContents['Max_Temporal_Baseline']
    else:
        print "Max_Temporal_Baseline is not found in template!! "
        print "500 days is chosen as the threshold for temporal baseline!"
        MaxTB = '100'
    
    
#  extract available SAR images slc and slc_par    
    ListSLC = os.listdir(slcDir)
    Datelist = []
    SLCfile = []
    SLCParfile = []
    

    for kk in range(len(ListSLC)):
        if ( is_number(ListSLC[kk]) and len(ListSLC[kk])==6 ):    #  if SAR date number is 8, 6 should change to 8.
            DD=ListSLC[kk]
            Year=int(DD[0:2])
            Month = int(DD[2:4])
            Day = int(DD[4:6])
            if  ( 0 < Year < 20 and 0 < Month < 13 and 0 < Day < 32 ):            
                Datelist.append(ListSLC[kk])
    
    map(int,Datelist)                
    Datelist.sort()
    map(str,Datelist)
    
    print "All of the available SAR acquisition datelist is :"      
    for kk in range(len(Datelist)):
        print Datelist[kk]
        str_slc = slcDir + "/" + Datelist[kk] +"/" + Datelist[kk] + ".slc"
        str_slc_par = slcDir + "/" + Datelist[kk] +"/" + Datelist[kk] + ".slc.par"
        SLCfile.append(str_slc)
        SLCParfile.append(str_slc_par)       
    
    if 'masterDate'          in templateContents:
        masterDate0 = templateContents['masterDate']
        if masterDate0 in Datelist:
            masterDate = masterDate0
            print "masterDate : " + masterDate0
        else:
            masterDate=Datelist[0]
            print "The selected masterDate is not included in above datelist !!"
            print "The first date [ %s ] is chosen as the master date! " % Datelist[0] 
            
    else:  
        masterDate=Datelist[0]
        print "masterDate is not found in template!!! "
        print "The first date [ %s ] is chosen as the master date! " % Datelist[0] 

    RefPar=slcDir + "/" + masterDate +"/" + masterDate + ".slc.par"
       
    File= open(SLC_Tab,'w')
    
    for kk in range(len(SLCfile)):
        File.write(str(SLCfile[kk])+ ' '+str(SLCParfile[kk])+'\n')
        
    File.close()
     
    call_str = "base_calc " + SLC_Tab + " " + RefPar + " " + TS_Berp + " " + TS_Itab + " " + '1 0 ' + '- ' + MaxSB + ' - ' + MaxTB
    os.system(call_str)

    TS_Net=np.loadtxt(TS_Berp)
    
#    print TS_Net[:,0]
#    print TS_Net[:,1]
    IFG_Flag=TS_Net[:,0]
    MDatelist=TS_Net[:,1]
    SDatelist=TS_Net[:,2]
    Berplist=TS_Net[:,3]
    TBaselist=TS_Net[:,4]
    
###############################    Add or Remove Date  #############################    

    if 'Add_Date'  in templateContents: AD=templateContents['Add_Date']
    else: 
        AD =''
        
    Addlist = []    
    if len(AD)>0:
        AD= AD.split('[')[1].split(']')[0]
        if ',' in AD:
            LL=AD.split(',')
            for kk in range(len(LL)):
                XX=LL[kk]
                if is_number(XX):
                    if XX in Datelist:
                        Addlist.append(XX)
                    else:
                        print XX + ' is not in the SLC datelist! '
                else:
                    D1=XX.split(':')[0]
                    D2=XX.split(':')[1]
                    map(int,Datelist)
                    for dd in Datelist:
                        if (int(dd) > int(D1)) and (int(dd) < int(D2)) :
                            Addlist.append(dd) 
        else:
            LL = AD
            if is_number(LL):
                if LL in Datelist:
                    Addlist.append(LL)
                else:
                    print LL + ' is not in the SLC date list!'
                                 
            else:
                D1=XX.split(':')[0]
                D2=XX.split(':')[1]
                map(int,Datelist)
                for dd in Datelist:
                    if (int(dd) > int(D1)) and (int(dd) < int(D2)) :
                        Addlist.append(dd) 
    
    Addlist=list(set(Addlist))      # remove possible repeat date
    print Addlist
###################################################################################


    if len(Addlist)>0:
        igramDir=[]
        run_slc2ifg_gamma = processDir + '/run_slc2ifg_gamma_add'
    
        if os.path.isfile(run_slc2ifg_gamma):
            os.remove(run_slc2ifg_gamma)
    
        print "Start to create interferograms directory:"
    
        f_slc2ifg =open(run_slc2ifg_gamma,'w')
        for kk in range(len(IFG_Flag)):
            str_sb=str(int(abs(Berplist[kk])))
            str_sb=add_zero(str_sb)
            str_tb=str(int(abs(TBaselist[kk])))
            str_tb=add_zero(str_tb)
        
            str_dir=processDir + "/"+ INF + '_' + projectName+"_"+str(int(MDatelist[kk]))[2:]+"-"+str(int(SDatelist[kk]))[2:]+"_"+str_sb+"_"+str_tb
        
            str_igram = INF + '_' + projectName+"_"+str(int(MDatelist[kk]))[2:]+"-"+str(int(SDatelist[kk]))[2:]+"_"+str_sb+"_"+str_tb
            MD=str(int(MDatelist[kk]))
            SD=str(int(SDatelist[kk]))
            if ((str(MD[2:]) in Addlist) or (str(SD[2:]) in Addlist)): 
                igramDir.append(str_dir)
                print 'Add igramDir: ' + str_igram
                str_scrip = 'SLC2Ifg_Gamma.py ' + str_igram + '\n'
                f_slc2ifg.write(str_scrip)
                #if not os.path.isdir(str_dir):
                #   call_str="mkdir " + str_dir
                #  os.system(call_str)
        f_slc2ifg.close()
    
    
########################### Prepare Process directory #############################
    else:
        igramDir=[]
        run_slc2ifg_gamma = processDir + '/run_slc2ifg_gamma'
    
        if os.path.isfile(run_slc2ifg_gamma):
            os.remove(run_slc2ifg_gamma)
    
    
        f_slc2ifg =open(run_slc2ifg_gamma,'w')
        for kk in range(len(IFG_Flag)):
            str_sb=str(int(abs(Berplist[kk])))
            str_sb=add_zero(str_sb)
            str_tb=str(int(abs(TBaselist[kk])))
            str_tb=add_zero(str_tb)
        
            str_dir=processDir + "/"+ INF + '_' + projectName+"_"+str(int(MDatelist[kk]))[2:]+"-"+str(int(SDatelist[kk]))[2:]+"_"+str_sb+"_"+str_tb
            igramDir.append(str_dir)
        
            str_igram = INF + '_' + projectName+"_"+str(int(MDatelist[kk]))[2:]+"-"+str(int(SDatelist[kk]))[2:]+"_"+str_sb+"_"+str_tb
            str_scrip = 'SLC2Ifg_Gamma.py ' + str_igram + '\n'
            f_slc2ifg.write(str_scrip)      
            STR_FLAG = INF + '_' + projectName+"_"+str(int(MDatelist[kk]))[2:]+"-"+str(int(SDatelist[kk]))[2:]
            KK= glob.glob(processDir + '/' + STR_FLAG + '*')
            print len(KK)
            if len(KK)< 1:
                call_str="mkdir " + str_dir
                os.system(call_str)
                print 'Add IFG >>> ' + str_dir
        f_slc2ifg.close()
    
    print "Selection of interferometric pairs is done! "
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])

    
