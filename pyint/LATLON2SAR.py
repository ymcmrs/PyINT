#! /usr/bin/env python

#'''
##################################################################################
###         Author:   Yun-Meng Cao                                             ### 
###         Date  :   March, 2017                                              ###  
###         Email :   ymcmrs@gmail.com                                         ###   
### Transform LAT/LON coordinates into SAR coordinates based on lookup table   ###    
##################################################################################
#'''


import os
import sys
import glob
import time
import argparse

import h5py
import numpy as np

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

def read_data(inFile, dtype, nWidth, nLength):
    data = np.fromfile(inFile, dtype, int(nLength)*int(nWidth)).reshape(int(nLength),int(nWidth)) 
    
    return data

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
        f.close()
       
        
def usage():
    print('''
******************************************************************************************************
 
           Transform LAT/LON coordinates into SAR coordinates based on lookup table

           usage:
   
                 LATLON2SAR.py Latitude Longitude LookupTableFile UTMDEMpar
      
           e.g.  LATLON2SAR.py 0.324 -78.213 /Yunmeng/20201230.utm_to_rdc /Yunmeng/20201230.dem.utm.par
          
            
*******************************************************************************************************
    ''')   

def main(argv):
    
    if len(sys.argv)==5:
        LAT  = sys.argv[1]
        LON  = sys.argv[2]
        LtFile  = sys.argv[3]
        UTMPAR  = sys.argv[4]
    else:
        usage();sys.exit(1)
    
    nWidthUTM = UseGamma(UTMPAR, 'read', 'width:')
    nLineUTM  = UseGamma(UTMPAR, 'read', 'nlines:')
   
    Corner_LAT = UseGamma(UTMPAR, 'read', 'corner_lat:') 
    Corner_LON = UseGamma(UTMPAR, 'read', 'corner_lon:')

    Corner_LAT =Corner_LAT.split(' ')[0]
    Corner_LON =Corner_LON.split(' ')[0]

    post_Lat = UseGamma(UTMPAR, 'read', 'post_lat:')
    post_Lon = UseGamma(UTMPAR, 'read', 'post_lon:')

    post_Lat =post_Lat.split(' ')[0]
    post_Lon =post_Lon.split(' ')[0] 
    data = read_data(LtFile,'>c8',nWidthUTM,nLineUTM)   # real: range     imaginary: azimuth
    
    XX = int (( float(LAT) - float(Corner_LAT) ) / float(post_Lat))  # latitude   width   range
    YY = int (( float(LON) - float(Corner_LON) ) / float(post_Lon))  # longitude   nline  azimuth
     
    CPX_OUT = data[XX][YY]    
    Range = int(CPX_OUT.real)
    Azimuth = int(CPX_OUT.imag)
    
    print(' Latitude: ' + LAT + '    ' + 'Longitude: ' + LON)    
    print(' Range: ' + str(Range) + '    ' + 'Azimuth: ' + str(Azimuth))    
##############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
