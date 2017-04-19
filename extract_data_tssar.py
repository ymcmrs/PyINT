#! /usr/bin/env python
############################################################                                                     
# Program is part of PySAR   v1.2                          #
# Copyright(c) 2017, Yunmeng Cao                           #
# Author :  Yunmeng Cao                                    # 
# Company:  Central South University                       #                                                       
############################################################


import os
import sys
import glob
import time
import argparse

import h5py
import numpy as np

def print_progress(iteration, total, prefix='calculating:', suffix='complete', decimals=1, barLength=50, elapsed_time=None):
    """Print iterations progress - Greenstick from Stack Overflow
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int) 
        barLength   - Optional  : character length of bar (Int) 
        elapsed_time- Optional  : elapsed time in seconds (Int/Float)
    
    Reference: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    if elapsed_time:
        sys.stdout.write('%s [%s] %s%s    %s    %s secs\r' % (prefix, bar, percents, '%', suffix, int(elapsed_time)))
    else:
        sys.stdout.write('%s [%s] %s%s    %s\r' % (prefix, bar, percents, '%', suffix))
    sys.stdout.flush()
    if iteration == total:
        print("\n")

    '''
    Sample Useage:
    for i in range(len(dateList)):
        print_progress(i+1,len(dateList))
    '''
    return

def read_data(inFile, dtype, nWidth, nLength):
    data = np.fromfile(inFile, dtype, int(nLength)*int(nWidth)).reshape(int(nLength),int(nWidth))  
    return data

def GetSubset(Subset):
    Dx = Subset.split('[')[1].split(']')[0].split(',')[0]
    Dy = Subset.split('[')[1].split(']')[0].split(',')[1]
    
    x1 = Dx.split(':')[0]
    x2 = Dx.split(':')[1]
    
    y1 = Dy.split(':')[0]
    y2 = Dy.split(':')[1]
    
    return x1,x2,y1,y2

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


def generate_TS_maskfile(H5FILE,Remove_Flag,X1,X2,Y1,Y2,OUTFILE):
    MASK = np.ones([int(X2)-int(X1),int(Y2)-int(Y1)])
    print 'Generating mask file >>> ' + OUTFILE
    
    f = h5py.File(H5FILE,'r')
    k1 = f.keys()[0]
    TSK = f[k1].keys()
    fileNum = len(TSK)
    for i in range(len(TSK)):
        S = TSK[i]
        print_progress(i+1, fileNum, prefix='Extracting ', suffix=os.path.basename(S))
        if str(i) not in Remove_Flag:
            data = f[k1][S].get(S)
            data = data[int(X1):int(X2),int(Y1):int(Y2)]     #  x: line --azimuth    y: width --range,  
            MASK = MASK*data
        
    MASK[MASK!=0]=1 

    f1 = h5py.File(OUTFILE,'w')
    group=f1.create_group('mask')
    dset = group.create_dataset('mask', data=MASK, compression='gzip')
    group.attrs['WIDTH'] = str(int(Y2)-int(Y1))
    group.attrs['FILE_LENGTH'] = str(int(X2)-int(X1))
    group.attrs['X_MIN'] = Y1   # width -- range / longitude
    group.attrs['X_MAX'] = Y2 
    group.attrs['Y_MIN'] = X1   # line -- azimuth / latitude
    group.attrs['Y_MAX'] = X2 
    f.close()
    f1.close() 
    
def Get_Datelist_H5(TSH5FILE):   
    f = h5py.File(TSH5FILE,'r')
    k1 = f.keys()[0]
    TSK = f[k1].keys()
    f.close()
    Datelist = []
    for i in range(len(TSK)):
        S = TSK[i]
        PAIR = S.split('_')[2]
        MD = PAIR.split('-')[0]
        SD = PAIR.split('-')[1]
        if MD not in Datelist:
            Datelist.append(MD)
        if SD not in Datelist:
            Datelist.append(SD)
    return Datelist
    
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def Get_Inflist_H5(TSH5FILE):
    f = h5py.File(TSH5FILE,'r')
    k1 = f.keys()[0]
    TSK = f[k1].keys()
    f.close()
    Pairlist = []
    for i in range(len(TSK)):
        S = TSK[i]
        PAIR = S.split('_')[2]
        Pairlist.append(PAIR)
    
    return Pairlist

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
        
def UseGamma2(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[2].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()

def Change_Date_list(RemovedateStr,Datelist):
    AD=RemovedateStr
    Addlist = []
    if len(AD)>0:
        AD= AD.split('[')[1].split(']')[0]
        if ',' in AD:
            LL=AD.split(',')
            for kk in range(len(LL)):
                XX=LL[kk]
                if is_number(XX):
                    if len(XX)==8:
                        XX=XX[2:]
                    if XX in Datelist:
                        Addlist.append(XX)
                    else:
                        print XX + ' is not in the SLC datelist! '
                else:
                    D1=XX.split(':')[0]
                    D2=XX.split(':')[1]
                    if len(D1)==8:
                        D1=D1[2:]
                        D2=D2[2:]
                    Datelist = map(int,Datelist)
                    for dd in Datelist:
                        if (int(dd) >= int(D1)) and (int(dd) <= int(D2)) :
                            Addlist.append(dd) 
        else:
            LL = AD
            if is_number(LL):
                if LL in Datelist:
                    if len(LL)==8:
                        LL=LL[2:]
                    Addlist.append(LL)
                else:
                    print LL + ' is not in the SLC date list!'
                                 
            else:
                D1=LL.split(':')[0]
                D2=LL.split(':')[1]
                if len(D1)==8:
                    D1=D1[2:]
                    D2=D2[2:]
                Datelist = map(int,Datelist)
                for dd in Datelist:
                    if (int(dd) >= int(D1)) and (int(dd) <= int(D2)) :
                        Addlist.append(dd)
    Addlist = map(str,Addlist)                    
    return Addlist
        
def Remove_Inf_List(RemoveNumberStr):
    AD=RemoveNumberStr
    Addlist = []
    if len(AD)>0:
        AD= AD.split('[')[1].split(']')[0]
        if ',' in AD:
            LL=AD.split(',')
            for kk in range(len(LL)):
                XX=LL[kk]
                if is_number(XX):
                        Addlist.append(XX)

                else:
                    D1=XX.split(':')[0]
                    D2=XX.split(':')[1]
                    for jj in range(int(D1),int(D2)+1):
                        Addlist.append(str(jj))
        else:
            LL = AD
            if is_number(LL):
                    Addlist.append(LL)                                 
            else:
                D1=LL.split(':')[0]
                D2=LL.split(':')[1]
                for jj in range(int(D1),int(D2)+1):
                    Addlist.append(str(jj))
    for ii in range(len(Addlist)):
        Addlist[ii]=int(Addlist[ii])-1      
    Addlist = map(str,Addlist)    
    return Addlist

def RemoveDate_Inf_List(PAIR_Name,ReDateList):
    RemoveInfList=[]
    for i in range(len(PAIR_Name)):
        MD = PAIR_Name[i].split('-')[0]
        SD = PAIR_Name[i].split('-')[1]
        if ((MD in ReDateList) or (SD in ReDateList)):
            RemoveInfList.append(str(i))
    return RemoveInfList
    
def Get_Remove_Flag_Final(TSH5FILE,RemoveDateStr,RemoveNumberStr):
    Datelist = Get_Datelist_H5(TSH5FILE)
    ReDateList = Change_Date_list(RemoveDateStr,Datelist)
    ReInfList = Remove_Inf_List(RemoveNumberStr)
    PAIR_Name = Get_Inflist_H5(TSH5FILE)
    ReInfList2=RemoveDate_Inf_List(PAIR_Name,ReDateList)
    ReInfFinal=list(set().union(ReInfList,ReInfList2))
    ReInfFinal = map(int,ReInfFinal)
    ReInfFinal.sort()
    ReInfFinal = map(str,ReInfFinal)
    return ReInfFinal
    
def read_roipac_rsc(File):
    '''Read ROI_PAC .rsc file into a python dictionary structure.'''
    rsc_dict = dict(np.loadtxt(File, dtype=str, usecols=(0,1)))
    return rsc_dict

def GeoCoord2RdcCoord(LTH5, LAT, LON):
    f = h5py.File(LTH5, 'r')
    LT = f['lt'].get('lt')[()]
    Corner_LAT = f['lt'].attrs['Y_FIRST']
    Corner_LON = f['lt'].attrs['X_FIRST']
    post_Lat = f['lt'].attrs['Y_STEP']
    post_Lon = f['lt'].attrs['X_STEP']
    f.close()
    
    XX = int (( float(LAT) - float(Corner_LAT) ) / float(post_Lat))  # latitude   width   range
    YY = int (( float(LON) - float(Corner_LON) ) / float(post_Lon))  # longitude   nline  azimuth
     
    CPX_OUT = LT[XX][YY]    
    Range = str(int(CPX_OUT.real))
    Azimuth = str(int(CPX_OUT.imag))
      
    return Range, Azimuth
    
def RdcCoord2GeoCoord(LTH5, Ra, Az):
    f = h5py.File(LTH5, 'r')
    LT = f['lt'].get('lt')[()]
    Corner_LAT = f['lt'].attrs['Y_FIRST']
    Corner_LON = f['lt'].attrs['X_FIRST']
    post_Lat = f['lt'].attrs['Y_STEP']
    post_Lon = f['lt'].attrs['X_STEP']
    f.close()
    
    Range_LT = LT.real
    Azimuth_LT = LT.imag
    
    CPX_input =complex(Ra + '+' + Az+'j')   
    DD = abs(CPX_input - LT)   
    LL= abs(DD)
    IDX= np.where(LL == LL.min())
    Lat_out = float(Corner_LAT) + IDX[0]*float(post_Lat)       
    Lon_out = float(Corner_LON) + IDX[1]*float(post_Lon)
    
    return Lat_out, Lon_out
    

def GeoSub2RdcSub(LTH5,GeoSubStr):
    LL = GetSubset(GeoSubStr)
    Lat1 = LL[0]
    Lat2 = LL[1]
    Lon1 = LL[2]
    Lon2 = LL[3]
    
    Ra = np.zeros([1,4])
    Az = np.zeros([1,4])
    
    Ra[0][0],Az[0][0] = GeoCoord2RdcCoord(LTH5,Lat1,Lon1)
    Ra[0][1],Az[0][1] = GeoCoord2RdcCoord(LTH5,Lat1,Lon2)
    Ra[0][2],Az[0][2] = GeoCoord2RdcCoord(LTH5,Lat2,Lon1)
    Ra[0][3],Az[0][3] = GeoCoord2RdcCoord(LTH5,Lat2,Lon2)
    
    Range_Min = str(int(min(Ra[0][:])))
    Range_Max = str(int(max(Ra[0][:])))
    
    Azimuth_Min = str(int(min(Az[0][:])))
    Azimuth_Max = str(int(max(Az[0][:])))
    
    return Range_Min, Range_Max, Azimuth_Min, Azimuth_Max

def RdcSub2GeoSub(LTH5,RdcSubStr):
    LL = GetSubset(RdcSubStr)
    Ra1 = LL[0]
    Ra2 = LL[1]
    Az1 = LL[2]
    Az2 = LL[3]
    
    La = np.zeros([1,4])
    Lo = np.zeros([1,4])
    
    La[0][0],Lo[0][0] = RdcCoord2GeoCoord(LTH5,Ra1,Az1)
    La[0][1],Lo[0][1] = RdcCoord2GeoCoord(LTH5,Ra1,Az2)
    La[0][2],Lo[0][2] = RdcCoord2GeoCoord(LTH5,Ra2,Az1)
    La[0][3],Lo[0][3] = RdcCoord2GeoCoord(LTH5,Ra2,Az2)
    
    Lat_Min = str(min(La[0][:]))
    Lat_Max = str(max(La[0][:]))
    
    Lon_Min = str(min(Lo[0][:]))
    Lon_Max = str(max(Lo[0][:]))
    
    return Lat_Min, Lat_Max, Lon_Min, Lon_Max
    
def extract_tsh5(H5FILE,REMOVE_FLAG,OUTFILE,X1,X2,Y1,Y2):
    f = h5py.File(H5FILE,'r')
    k1 = f.keys()[0]
    TSK = f[k1].keys()
    
    f1 = h5py.File(OUTFILE,'w')
    group = f1.create_group(k1)
    fileNum = len(TSK)
    for i in range(len(TSK)):
        S = TSK[i]
        print_progress(i+1, fileNum, prefix='Extracting ', suffix=os.path.basename(S))
        if str(i) not in REMOVE_FLAG:
            gg = group.create_group(S)
            data = f[k1][S].get(S)
            data = data[int(X1):int(X2),int(Y1):int(Y2)]     #  x: line --azimuth    y: width --range,  
            dset  = gg.create_dataset(S, data = data, compression='gzip')
            atr = f[k1][S].attrs         
            for key,value in atr.iteritems():   gg.attrs[key] = value
            gg.attrs['WIDTH'] = str(int(Y2)-int(Y1))
            gg.attrs['FILE_LENGTH'] = str(int(X2)-int(X1))
            group.attrs['X_MIN'] = Y1   # width -- range / longitude
            group.attrs['X_MAX'] = Y2 
            group.attrs['Y_MIN'] = X1   # line -- azimuth / latitude
            group.attrs['Y_MAX'] = X2            
    f.close()
    f1.close()       

def usage():
    print '''
******************************************************************************************************
 
           Extract data for further time series processing

           usage:
   
                 extract_data_tssar.py projectName
      
           e.g.  extract_data_tssar.py PacayaT163TsxHhA
          
            
*******************************************************************************************************
    '''   

def main(argv):
    
    total = time.time()
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
    masterDate = templateContents['masterDate']
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    tsDir    = processDir + '/TSSAR/TSH5'          # all data loaded into TSH5
       
    if 'Remove_Date'  in templateContents: RemoveDateStr = templateContents['Remove_Date']                
    else: RemoveDateStr = ''     
     
    if 'Remove_Inf'  in templateContents: RemoveInfStr = templateContents['Remove_Inf']                
    else: RemoveInfStr = '' 
        
    SubRdc=''
    SubGeo=''
    
    if 'Subset_Rdc' in templateContents: SubRdc = templateContents['Subset_Rdc']
    if 'Subset_Geo' in templateContents: SubGeo = templateContents['Subset_Geo']

    UNWH5 = tsDir + '/unwrapIfgram.h5'
    INFH5 = tsDir + '/wrapIfgram.h5'
    CORH5 = tsDir + '/coherence.h5'
    MASKH5 = tsDir + '/unwrapIfgram.h5'
    RDCDEM = tsDir + '/demRdc.h5'
    GEODEM = tsDir + '/demGeo.h5'
    GEOTRANS = tsDir + '/geo2rdc.h5'
    

    f =h5py.File(GEODEM)
    k1 = f.keys()[0]
    nWidthUTM = f[k1].attrs['WIDTH']
    nLineUTM = f[k1].attrs['FILE_LENGTH']
    Corner_LAT = f[k1].attrs['Y_FIRST']
    Corner_LON = f[k1].attrs['X_FIRST']
    post_Lat = f[k1].attrs['Y_STEP']
    post_Lon = f[k1].attrs['X_STEP']   
    f.close()
    
    
    LAT_MIN = Corner_LAT
    LAT_MAX = str(float(Corner_LAT) + int(nLineUTM)*float(post_Lat))
    
    LON_MIN = Corner_LON
    LON_MAX = str(float(Corner_LON) + int(nWidthUTM)*float(post_Lon))
    
    f =h5py.File(UNWH5)
    k1 = f.keys()[0]
    k2 = f[k1].keys()[0]
    N_Inf0 = len(f[k1].keys())
    nWidth = f[k1][k2].attrs['WIDTH']
    nLine = f[k1][k2].attrs['FILE_LENGTH']
    f.close()
      
    print ''
    print 'Start to extract time series processing data sets from existed h5 file >>> '
    print ''
    if len(SubRdc)>0:
        print 'Subset information based on radar coordinates ...'
        SubRA = GetSubset(SubRdc)
        SubGE = RdcSub2GeoSub(GEOTRANS, SubRdc)
    else:
        if len(SubGeo)>0:
            print 'Subset information based on geo coordinates ...'
            SubRA = GeoSub2RdcSub(GEOTRANS,SubGeo)
            SubGE = GetSubset(SubGeo)
        else:
            print 'No subset information is found in template file, whole image will be used for further processing ...'
            SubRA = ['0',nWidth,'0', nLine]
            SubGE = [LAT_MIN,LAT_MAX,LON_MIN,LON_MAX]
            
    la1 = SubGE[0]
    la2 = SubGE[1]
    lo1 = SubGE[2]
    lo2 = SubGE[3]
    

    
    x1 = SubRA[2]
    x2 = SubRA[3]
    y1 = SubRA[0]
    y2 = SubRA[1]
        
    workDir = processDir + '/TSSAR' + '/SUB_' + y1 + '_' + y2 + '_' + x1 + '_' + x2    
    if not os.path.isdir(workDir):
        call_str = 'mkdir ' + workDir
        os.system(call_str)
    
    TSUNWH5 = workDir + '/unwrapIfgram_proc.h5'
    TSINFH5 = workDir + '/wrapIfgram_proc.h5'
    TSCORH5 = workDir + '/coherence_proc.h5'
    TSMASKH5 = workDir + '/mask.h5'
    TSRDCDEM = workDir + '/demRdc_proc.h5'
    
    TSRDCDEM0 = workDir + '/demRdc.h5'
    TSGEODEM0 = workDir + '/demGeo.h5'
    TSGEOTRANS = workDir + '/geo2rdc.h5'
    
    
    print ''
    print 'Extracting data for timeseries processing >>>'
    print 'Change process Dir to :' + workDir
    os.chdir(workDir)
    
    print 'Subset in geo coordinates: '
    print 'minimum latitude : ' + la1 + '    maximum latitude : ' + la2
    print 'minimum longitude: ' + lo1 + '    maximum longitude: ' + lo2
    print ''
    
    
    print 'Subset in radar coordinates: '
    print 'minimum range  :  ' + y1 + '    maximum range  : ' + y2
    print 'minimum azimuth:  ' + x1 + '    maximum azimuth: ' + x2
    print ''
    
    Remove_Flag= Get_Remove_Flag_Final(UNWH5,RemoveDateStr,RemoveInfStr)
    N_Inf = str(N_Inf0-len(Remove_Flag))
    
    
    print ''
    print 'Start to extract wrapIfgram >>> ' + N_Inf + ' files will be extracted. '
    extract_tsh5(INFH5,Remove_Flag,TSINFH5,x1,x2,y1,y2)  
    
    print ''
    print 'Start to extract unwrapIfgram >>> ' + N_Inf + ' files will be extracted. '
    extract_tsh5(UNWH5,Remove_Flag,TSUNWH5,x1,x2,y1,y2)
    
    
    print ''
    print 'Start to extract coherence >>> ' + N_Inf + ' files will be extracted. '
    extract_tsh5(CORH5,Remove_Flag,TSCORH5,x1,x2,y1,y2) 
    
    print ''
    print 'Start to exrtact RDC-DEM >>> ' + RDCDEM
    
    f = h5py.File(RDCDEM,'r')
    attrs = f['dem'].attrs
    data = f['dem'].get('dem')
    data = data[int(x1):int(x2),int(y1):int(y2)]

    f1 = h5py.File(TSRDCDEM,'w')
    group = f1.create_group('dem')
    dset  = group.create_dataset('dem', data = data, compression='gzip')
    atr = f['dem'].attrs         
    for key,value in atr.iteritems():   group.attrs[key] = value
    group.attrs['X_MIN'] = y1   # width -- range / longitude
    group.attrs['X_MAX'] = y2 
    group.attrs['Y_MIN'] = x1   # line -- azimuth / latitude
    group.attrs['Y_MAX'] = x2 
    
    f.close()
    f1.close()
    
    print ''
    generate_TS_maskfile(UNWH5,Remove_Flag,x1,x2,y1,y2,TSMASKH5)
    
    print ''
    print 'Start to copy RDC-DEM and GEO-DEM and Lookup Table into work directory >>> '
    call_str = 'cp ' + RDCDEM + ' ' + TSRDCDEM0
    os.system(call_str)
    
    call_str = 'cp ' + GEODEM + ' ' + TSGEODEM0
    os.system(call_str)
    
    call_str = 'cp ' + GEOTRANS + ' ' + TSGEOTRANS
    os.system(call_str)
    
    print ''
    print 'Done.\nExtracting data spend ' + str(time.time()-total) +' secs'
    sys.exit(1)

##############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
