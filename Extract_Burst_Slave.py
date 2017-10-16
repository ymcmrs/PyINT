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
import argparse

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

def write_template(File,STR):
    f = open(File, 'a')
    f.writelines(STR)
    f.close()
    
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

def GetDatelist(projectName):
    
    scratchDir = os.getenv('SCRATCHDIR')    
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    ListSLC = os.listdir(slcDir)
    
    Datelist = []
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
    
    return Datelist

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
        
#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyINT v1.0
   
   Check the common bursts for S1 TOPs.
'''

EXAMPLE = '''
    Usage:
            Extract_Burst_Slave.py projectName 170115
            
    Examples:
            Extract_Burst_Slave.py PacayaT163TsxHhA 170115
##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Check common busrts for TOPS data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of project.')
    parser.add_argument('Sdate',help='Slave date.')

    inps = parser.parse_args()

    return inps

################################################################################    
    
    
def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
    Sdate = inps.Sdate
    
    projectName = igramDir.split('_')[1]  
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
           
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    Mdate =  templateContents['masterDate']
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir     = scratchDir + '/' + projectName + "/RSLC"
    MslcDir    = slcDir + '/' + Mdate
    SslcDir    = slcDir + '/' + Sdate
    #MBurst_Par = slcDir + '/' + Mdate + '/' + 
    workDir = rslcDir + '/' + Sdate
    BURST = workDir + '/' + Mdate + '_' + Sdate + '.common_burst_ref'
    
    MslcImg = workDir + '/'+Mdate + '.slc'
    MslcPar = workDir + '/'+Mdate + '.slc.par'    
    
    MamprlksImg = workDir + '/'+Mdate +   '_' + rlks + 'rlks' + '.amp'
    MamprlksPar = workDir + '/'+Mdate +   '_' + rlks +'rlks' + '.amp.par' 
    
    SslcImg = workDir + '/'+ Sdate + '.slc'
    SslcPar = workDir + '/'+ Sdate + '.slc.par'    
    
    SamprlksImg = workDir + '/'+ Sdate +  '_' + rlks + 'rlks' + '.amp'
    SamprlksPar = workDir + '/'+ Sdate +  '_' + rlks + 'rlks' + '.amp.par' 
    
    if not os.path.isfile(BURST):
        call_str = 'Check_Common_Burst_All.py ' + projectName
        os.system(call_str)
        
    if 'Start_Swath' in templateContents: SW = templateContents['Start_Swath']
    else: 
        SW = '1'
        STR = 'Start_Swath      = ' + SW + '\n'
        write_template(templateFile,STR)
        
    if 'End_Swath' in templateContents: EW = templateContents['End_Swath']
    else: 
        EW = '3' 
        STR = 'End_Swath      = ' + EW + '\n'
        write_template(templateFile,STR)
        
    AA = np.loadtxt(BURST)
    
    if 'Start_Burst' in templateContents: SB = templateContents['Start_Burst']
    else: 
        SB = '1'
        STR = 'Start_Burst     = ' + SB + '\n'
        write_template(templateFile,STR)
        
    if 'End_Burst' in templateContents: EB = templateContents['End_Burst']
    else: 
        EB = '20' 
        #STR = 'End_Burst      = ' + EB + '\n'
        #write_template(templateFile,STR)
    
    #SLC1_tab = workDir + '/' + Mdate + '_SLC_Tab0'
    SLC2_tab = workDir + '/' + Sdate + '_SLC_Tab0'
        
    #SLC1_INF_tab = workDir + '/' + Mdate + '_SLC_Tab'
    SLC2_INF_tab = workDir + '/' + Sdate + '_SLC_Tab'
    
    #BURST1_tab = workDir + '/' + Mdate + '_Burst_Tab'
    BURST2_tab = workDir + '/' + Sdate + '_Burst_Tab'
    
    #if os.path.isfile(SLC1_tab):
    #    os.remove(SLC1_tab)
    
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)
        
    #if os.path.isfile(SLC1_INF_tab):
    #    os.remove(SLC1_INF_tab)
    
    if os.path.isfile(SLC2_INF_tab):
        os.remove(SLC2_INF_tab)
        
    #if os.path.isfile(BURST1_tab):
    #    os.remove(BURST1_tab)
    
    if os.path.isfile(BURST2_tab):
        os.remove(BURST2_tab)
    
    for kk in range(int(EW)-int(SW)+1):
        #call_str = 'echo ' + MslcDir + '/' + Mdate+'.IW'+str(int(SW)+kk) + '.slc' + ' ' + MslcDir + '/'+ Mdate + '.IW'+str(int(SW)+kk) +'.slc.par' + ' ' + MslcDir + '/'+ Mdate+'.IW'+str(int(SW)+kk) + '.slc.TOPS_par >>' + SLC1_tab
        #os.system(call_str)
        
        call_str = 'echo ' + SslcDir + '/' + Sdate+'.IW'+str(int(SW)+kk) + '.slc' + ' ' + SslcDir + '/'+ Sdate + '.IW'+str(int(SW)+kk) +'.slc.par' + ' ' + SslcDir + '/'+ Sdate+'.IW'+str(int(SW)+kk) + '.slc.TOPS_par >>' + SLC2_tab
        os.system(call_str)
        
        ii = kk + 1
        SB1=AA[ii-1,0]
        EB1=AA[ii-1,1]
        
        SB2=AA[ii-1,2]
        EB2=AA[ii-1,3]
        
        if not int(SB)==1:
            SB2 = SB2 + int(SB)-1
        if not int(EB)==20:
            EB2 = SB2 + int(EB) - int(SB)
        
        #call_str = 'echo ' + workDir + '/'+ Mdate+ '_'+ str(int(SB1)) + str(int(EB1)) +'.IW'+str(int(SW)+kk)+ '.slc' + ' ' + workDir + '/' + Mdate + '_'+ str(int(SB1)) + str(int(EB1)) +'.IW'+ str(int(SW)+kk)+ '.slc.par' + ' ' + workDir + '/'+ Mdate+'_'+ str(int(SB1)) + str(int(EB1)) + '.IW'+str(int(SW)+kk)+ '.slc.TOPS_par >>' + SLC1_INF_tab
        #os.system(call_str)
        
        
        call_str = 'echo ' + workDir + '/'+ Sdate+ '_'+ str(int(SB2)) + str(int(EB2)) +'.IW'+str(int(SW)+kk)+ '.slc' + ' ' + workDir + '/' + Sdate + '_'+ str(int(SB2)) + str(int(EB2)) +'.IW'+ str(int(SW)+kk)+ '.slc.par' + ' ' + workDir + '/'+ Sdate+'_'+ str(int(SB2)) + str(int(EB2)) + '.IW'+str(int(SW)+kk)+ '.slc.TOPS_par >>' + SLC2_INF_tab
        os.system(call_str)
        
        #call_str = 'echo ' + str(int(SB1)) + ' '  + str(int(EB1)) + ' >>' + BURST1_tab
        #os.system(call_str)
        
        call_str = 'echo ' + str(int(SB2)) + ' ' + str(int(EB2)) + ' >>' + BURST2_tab
        os.system(call_str)

    #call_str = 'SLC_copy_S1_TOPS ' + SLC1_tab + ' ' + SLC1_INF_tab  + ' ' + BURST1_tab 
    #os.system(call_str)
    
    call_str = 'SLC_copy_S1_TOPS ' + SLC2_tab + ' ' + SLC2_INF_tab  + ' ' + BURST2_tab 
    os.system(call_str)
        
    #call_str = 'SLC_mosaic_S1_TOPS ' + SLC1_INF_tab + ' ' + MslcImg + ' ' + MslcPar + ' ' + rlks + ' ' +azlks
    #os.system(call_str)
    
    #call_str = '$GAMMA_BIN/multi_look ' + MslcImg + ' ' + MslcPar + ' ' + MamprlksImg + ' ' + MamprlksPar + ' ' + rlks + ' ' + azlks
    #os.system(call_str) 
    
    #nWidth = UseGamma(MamprlksPar, 'read', 'range_samples')
    #call_str = '$GAMMA_BIN/raspwr ' + MamprlksImg + ' ' + nWidth 
    #os.system(call_str)  
    #ras2jpg(MamprlksImg, MamprlksImg) 
    
    call_str = 'SLC_mosaic_S1_TOPS ' + SLC2_INF_tab + ' ' + SslcImg + ' ' + SslcPar + ' ' + rlks + ' ' +azlks
    os.system(call_str)
    
    call_str = '$GAMMA_BIN/multi_look ' + SslcImg + ' ' + SslcPar + ' ' + SamprlksImg + ' ' + SamprlksPar + ' ' + rlks + ' ' + azlks
    os.system(call_str) 
    
    nWidth = UseGamma(SamprlksPar, 'read', 'range_samples')
    call_str = '$GAMMA_BIN/raspwr ' + SamprlksImg + ' ' + nWidth 
    os.system(call_str)  
    ras2jpg(SamprlksImg, SamprlksImg) 
    
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
