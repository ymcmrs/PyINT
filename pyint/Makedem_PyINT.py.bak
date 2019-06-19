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

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

#########################################################################

INTRODUCTION = '''
##############################################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyINT v1.0   
   
   Generate dem automatically for GAMMA processing.
   
'''

EXAMPLE = '''
    Usage:
            Makedem_PyINT.py projectName processor
 
    Examples:
            Makedem_PyINT.py ShanghaiT171F96S1A gamma

###################################################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate dem automatically.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of the projection.')
    parser.add_argument('processor',help='Name of the processor. [gamma or roi_pac]')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
    
    inps = cmdLineParse()
    projectName = inps.projectName
    processor = inps.processor
    scratchDir = os.getenv('SCRATCHDIR')
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    KK=os.listdir(slcDir)
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    
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

    SLC_PAR = slcDir + '/' + masterDate + '/'+ masterDate + '.slc.par'
    
    demDir = os.getenv('DEMDIR') 
    os.chdir(demDir)
    call_str = 'mkdir ' + projectName
    os.system(call_str)
    
    demDir2 = demDir + '/' + projectName
    os.chdir(demDir2)
    
    call_str= 'makedem.py ' + '-s ' + SLC_PAR + ' -p ' + processor + ' -o ' + projectName
    os.system(call_str)
    
    print 'Generate DEM for project %s is done.' % projectName
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    