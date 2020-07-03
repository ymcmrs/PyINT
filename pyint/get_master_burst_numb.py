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
import subprocess
import getopt
import time
import glob
import argparse

from pyint import _utils as ut

        

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Get burst number table of the master date for TOPS SLC.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='project name. e.g., ChangningT55S1A')
       
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  

   Get burst number table of the master date for TOPS SLC.
'''

EXAMPLE = """Usage:
  
  get_master_burst_numb.py projectName 
  
  get_master_burst_numb.py ChangningT55S1A
  
------------------------------------------------------------------- 
"""

def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    projectDir = scratchDir + '/' + projectName 
    
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)  
    
    masterDate = templateDict['masterDate']
    date = masterDate
    
    slc_dir =  projectDir + '/SLC'
    down_dir = projectDir + '/DOWNLOAD'
    opod_dir = projectDir + '/OPOD'
    
    if not os.path.isdir(slc_dir):
        os.mkdir(slc_dir)
    if not os.path.isdir(opod_dir):
        os.mkdir(opod_dir)
        
    work_dir = slc_dir + '/' + date
    if not os.path.isdir(work_dir):
        os.mkdir(work_dir)
    
    work_dir = down_dir
    os.chdir(work_dir)
    
    t_date = down_dir +  '/t_' + date
    t_burst_numb = down_dir + '/t_burst_numb_' + date 
    
    call_str = 'ls ' + down_dir + '/S1*' + date + '*.zip > ' + t_date
    os.system(call_str)
    
    zip_files = ut.read_txt2list(t_date)
    print(zip_files)
    for i in range(len(zip_files)):
        call_str = 'S1_BURST_tab_from_zipfile - ' +  zip_files[i] + ' - '
        os.system(call_str)
    
    
    call_str = 'ls ' + down_dir + '/S1*' + date + '*.burst_number_table > ' + t_burst_numb
    os.system(call_str)
    burst_files = ut.read_txt2list(t_burst_numb)
    
    
    iw1_burst_node = []
    iw2_burst_node = []
    iw3_burst_node = []
    
    print(burst_files)
    for i in range(len(burst_files)):
        print(burst_files[i])
        iw1_first = ut.read_gamma_par(str(burst_files[i]),'read','iw1_first_burst')
        iw1_last = ut.read_gamma_par(str(burst_files[i]),'read','iw1_last_burst')
        iw1_burst_node.append(float(iw1_first))
        iw1_burst_node.append(float(iw1_last))
        
        iw2_first = ut.read_gamma_par(str(burst_files[i]),'read','iw2_first_burst')
        iw2_last = ut.read_gamma_par(str(burst_files[i]),'read','iw2_last_burst')
        iw2_burst_node.append(float(iw2_first))
        iw2_burst_node.append(float(iw2_last))
        
        iw3_first = ut.read_gamma_par(str(burst_files[i]),'read','iw3_first_burst')
        iw3_last = ut.read_gamma_par(str(burst_files[i]),'read','iw3_last_burst')
        iw3_burst_node.append(float(iw3_first))
        iw3_burst_node.append(float(iw3_last))
        
    
    if 'iw1_first_burst' in templateDict: IW1_0 = templateDict['iw1_first_burst']
    else: IW1_0 = '1'
    if 'iw1_last_burst' in templateDict: IW1_1 = templateDict['iw1_last_burst']
    else: IW1_1 = str(round(max(iw1_burst_node) - min(iw1_burst_node) + 1))
    
    if 'iw2_first_burst' in templateDict: IW2_0 = templateDict['iw2_first_burst']
    else: IW2_0 = '1'
    if 'iw2_last_burst' in templateDict: IW2_1 = templateDict['iw2_last_burst']
    else: IW2_1 = str(round(max(iw2_burst_node) - min(iw2_burst_node) + 1))
    
    if 'iw3_first_burst' in templateDict: IW3_0 = templateDict['iw3_first_burst']
    else: IW3_0 = '1'
    if 'iw3_last_burst' in templateDict: IW3_1 = templateDict['iw3_last_burst']
    else: IW3_1 = str(round(max(iw3_burst_node) - min(iw3_burst_node) + 1))
    
    if int(IW1_1) > round(max(iw1_burst_node) - min(iw1_burst_node) + 1):
        IW1_1 = str(round(max(iw1_burst_node) - min(iw1_burst_node) + 1))
    
    if int(IW2_1) > round(max(iw2_burst_node) - min(iw2_burst_node) + 1):
        IW2_1 = str(round(max(iw2_burst_node) - min(iw2_burst_node) + 1))
    
    if int(IW3_1) > round(max(iw3_burst_node) - min(iw3_burst_node) + 1):
        IW3_1 = str(round(max(iw3_burst_node) - min(iw3_burst_node) + 1))
    
    
    D_IW1_first = int(IW1_0) - 1
    DD_IW1_numb = int(IW1_1) - int(IW1_0) + 1
   
    D_IW2_first = int(IW2_0) - 1
    DD_IW2_numb = int(IW2_1) - int(IW2_0) + 1
    
    D_IW3_first = int(IW3_0) - 1
    DD_IW3_numb = int(IW3_1) - int(IW3_0) + 1
    
    master_busrt = down_dir + '/master.burst_numb_table' 
    if os.path.isfile(master_busrt):
        os.remove(master_busrt)
    
    with open(master_busrt, 'a') as f:
        STR0 = 'iw1_number_of_bursts: ' + str(DD_IW1_numb)  + '\n'
        STR00 = 'iw1_number_of_bursts: ' + str(DD_IW1_numb)
        print(STR00)
        f.write(STR0)
    
        STR0 = 'iw1_first_burst:      ' + str(min(iw1_burst_node) + D_IW1_first)  + '\n'
        STR00 = 'iw1_first_burst:      ' + str(min(iw1_burst_node) + D_IW1_first)
        print(STR00)
        f.write(STR0)
        
        STR0 = 'iw1_last_burst:       ' + str(min(iw1_burst_node) + D_IW1_first + DD_IW1_numb - 1)  + '\n'
        STR00 = 'iw1_last_burst:       ' + str(min(iw1_burst_node) + D_IW1_first + DD_IW1_numb - 1)
        print(STR00)
        f.write(STR0)
        
        STR0 = 'iw2_number_of_bursts: ' + str(DD_IW2_numb)  + '\n'
        STR00 = 'iw2_number_of_bursts: ' + str(DD_IW2_numb)
        print(STR00)
        f.write(STR0)
    
        STR0 = 'iw2_first_burst:      ' + str(min(iw2_burst_node) + D_IW2_first)  + '\n'
        STR00 = 'iw2_first_burst:      ' + str(min(iw2_burst_node) + D_IW2_first)
        print(STR00)
        f.write(STR0)
        
        STR0 = 'iw2_last_burst:       ' + str(min(iw2_burst_node) + D_IW2_first + DD_IW2_numb - 1)  + '\n'
        STR00 = 'iw2_last_burst:       ' + str(min(iw2_burst_node) + D_IW2_first + DD_IW2_numb - 1)
        print(STR00)
        f.write(STR0)
        
        
        STR0 = 'iw3_number_of_bursts: ' + str(DD_IW3_numb)  + '\n'
        STR00 = 'iw3_number_of_bursts: ' + str(DD_IW3_numb)
        print(STR00)
        f.write(STR0)
    
        STR0 = 'iw3_first_burst:      ' + str(min(iw3_burst_node) + D_IW3_first)  + '\n'
        STR00 = 'iw3_first_burst:      ' + str(min(iw3_burst_node) + D_IW3_first)
        print(STR00)
        f.write(STR0)
        
        STR0 = 'iw3_last_burst:       ' + str(min(iw3_burst_node) + D_IW3_first + DD_IW3_numb - 1)  + '\n'
        STR00 = 'iw3_last_burst:       ' + str(min(iw3_burst_node) + D_IW3_first + DD_IW3_numb - 1)
        print(STR00)
        f.write(STR0)
    
   
    print("Get burst number table for master date is done! ")
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
