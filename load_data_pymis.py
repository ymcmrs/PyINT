#! /usr/bin/env python
#################################################################
###  This program is part of PyMIS  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Central South University & University of Miami   ###   
#################################################################

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

def read_list(ListName):
    List=glob.glob(ListName)
    return List

def read_list_except(ListName,ExString):
    List=glob.glob(ListName)
    List_New = []
    for S in List:
        if ExString not in os.path.basename(S):
            List_New.append(S)
    return List_New

            
def load_gamma2multi_group_h5(fileType, fileName, fileList, RSCList, datatype):
    
    RSC =RSCList[0]
    rsc_dic = read_roipac_rsc(RSC)
    nWidth = rsc_dic['WIDTH']
    nLine  = rsc_dic['FILE_LENGTH']
    
    H5FILE = fileName + '.h5'  
    fileNum = len(fileList)  
    print 'Start to load ' + fileName + ' >>> %s %s files will be loaded for further process' % ( str(fileNum), fileType) 
    f = h5py.File(H5FILE,'w')
    gg=f.create_group(fileType)
    
    for i in range(len(fileList)):
        S=fileList[i]
        RSC =RSCList[i]
        rsc_dic = read_roipac_rsc(RSC)
        print_progress(i+1, fileNum, prefix='loading', suffix=os.path.basename(S))
        data = read_data(S,datatype,nWidth,nLine)
        File = os.path.basename(S)
        group = gg.create_group(File)
        dset  = group.create_dataset(File, data = data, compression='gzip')
        for key,value in rsc_dic.iteritems():
            group.attrs[key] = value
        group.attrs['X_MIN'] = '0'
        group.attrs['X_MAX'] = str(int(nWidth)-1)
        group.attrs['Y_MIN'] = '0'
        group.attrs['Y_MAX'] = str(int(nLine)-1)
        group.attrs['DATE12']=File.split('_')[2]
        group.attrs['DATATYPE'] = datatype
        group.attrs['PROCCESSOR'] = 'gamma'
        
    f.close()    

    
def Get_Datelist(projectName):   
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    rslcDir    = scratchDir + '/' + projectName + "/RSLC"
    slcDir    = scratchDir + '/' + projectName + "/SLC"    

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
    Datelist = map(int,Datelist)                
    Datelist.sort()
    Datelist = map(str,Datelist)         
    return Datelist
 
def Get_Inflist(projectName):
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    IFGRAM    = scratchDir + '/' + projectName + "/PROCESS/IFG*"
    IFGList = glob.glob(IFGRAM)    

    ListSLC = os.listdir(slcDir)
    Datelist = []


def Get_PairName(projectName):
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    IFGRAM    = scratchDir + '/' + projectName + "/PROCESS/IFG*"
    IFGList = glob.glob(IFGRAM)    
    
    PAIR_Name = []
    for kk in range(len(IFGList)):
        SS = IFGList[kk]
        IFGName = os.path.basename(SS)
        PAIR=IFGName.split('_')[2]
        PAIR_Name.append(PAIR)

    return PAIR_Name    
    
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

    
def read_roipac_rsc(File):
    '''Read ROI_PAC .rsc file into a python dictionary structure.'''
    rsc_dict = dict(np.loadtxt(File, dtype=str, usecols=(0,1)))
    return rsc_dict


#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyMIS v1.0   
   
   Loading data for PyMIS processing.
   
'''

EXAMPLE = '''
    Usage:
            load_data_pymis.py projectName 
            load_data_pymis.py projectName --demRdc 
            load_data_pymis.py projectName --wrapIfgram
            
    Examples:
            load_data_pymis.py PacayaT163TsxHhA
            load_data_pymis.py PacayaT163TsxHhA --demRdc
            load_data_pymis.py PacayaT163TsxHhA --coherence

##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Loading data for PyMIS processing.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='project name of PyMIS.')
    parser.add_argument('--coherence',action="store_true", default=False, help='Loading coherence file.')
    parser.add_argument('--wrapIfgram',action="store_true", default=False, help='Loading wrapped interferograms.')
    parser.add_argument('--unwrapIfgram',action="store_true", default=False, help='Loading unwrapped interferograms.')
    parser.add_argument('--demRdc',action="store_true", default=False, help='Loading radar coordinates DEM.')
    parser.add_argument('--demGeo',action="store_true", default=False, help='Loading GEO coordinates DEM.')
    parser.add_argument('--geo2rdc',action="store_true", default=False, help='Loading geocoding lookup table.')
    
    inps = parser.parse_args()
    


    return inps

################################################################################

def main(argv):
    
    
    total = time.time()
    inps = cmdLineParse()
    projectName = inps.projectName
         
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir    = scratchDir + '/' + projectName + "/RSLC"
    simDir     = scratchDir + '/' + projectName + "/PROCESS/DEM"
    
    
    masterDate = templateContents['masterDate']
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
        
    workDir    = scratchDir + '/' + projectName + '/PYMIS'
    if not os.path.isdir(workDir):
        call_str='mkdir ' + workDir
        os.system(call_str)
            
    if not os.path.isdir(workDir):
        call_str='mkdir ' + workDir
        os.system(call_str)
    
    print 'Project : ' + projectName
    print 'Loading data for timeseries processing >>>'
    print 'Change process Dir to :' + workDir
    os.chdir(workDir)
       

################# DEM Define ############
    
    

    
    UTM2RDC = simDir+'/sim_' + masterDate + '_' + rlks + 'rlks.UTM_TO_RDC'
    RDCDEM = simDir+'/sim_' + masterDate + '_' + rlks + 'rlks.rdc.dem'
    UTMDEM = simDir+'/sim_' + masterDate + '_' + rlks + 'rlks.utm.dem'
    UTMPAR = simDir+'/sim_' + masterDate + '_' + rlks + 'rlks.utm.dem.par'

    
    
#    if not os.path.isfile(UTM2RDC):
#        print 'Start to generate subset look-up table and subset-DEM >>>'
#        call_str = 'CreateRdcDem_Sub_Gammapy.py ' + igramDir
#        print call_str
#        os.system(call_str)
#    else:
#        print 'Subet lookup table %s is existed!' % UTM2RDC
    
    Dem_Format = UseGamma(UTMPAR, 'read', 'data_format:') 
    
    if Dem_Format=='REAL*4':
        dtype_utmdem='f4'
    else:
        dtype_utmdem='i2'
    
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

############### timeseries file define ##################     
    
    if 'IFG_list' in templateContents: IFG_list = templateContents['IFG_list']
    else: IFG_list = processDir + '/IFG*/diff_filt*rlks.int'
    if 'UNW_list' in templateContents: UNW_list = templateContents['UNW_list']
    else: UNW_list = processDir + '/IFG*/diff_filt*rlks.unw'
    if 'COR_list' in templateContents: COR_list = templateContents['COR_list']
    else: COR_list = processDir + '/IFG*/diff_filt*rlks.cor'
    if 'MASK_list' in templateContents: MASK_list = templateContents['MASK_list']
    else: MASK_list = processDir + '/IFG*/diff_filt*rlks.unw'    
    if 'RSC_list' in templateContents: RSC_list = templateContents['RSC_list']
    else: RSC_list = processDir + '/IFG*/*rlks.rsc'

    MM=MASK_list[0]
    if MM.split('.')[len(MM.split('.'))-1]=='bmp':
        dtype_mask ='u1'
    else:
        dtype_mask ='f4'
      
    if 'Byte_order' in  templateContents: byteoder = templateContents['Byte_order']
    else: byteorder = 'big'
    
    if byteorder =='big':
        sign = '>'
    else:
        sign ='<'

    dtype_inf = sign + 'c8'
    dtype_unw = sign + 'f4'
    dtype_utmdem = sign + dtype_utmdem
    dtype_rdcdem = sign + 'f4'
    dtype_lt = sign + 'c8'
    dtype_mask = sign + dtype_mask
    dtype_cor = sign + 'f4'
    
####################  start to load data ########################
    InfList = read_list(IFG_list)   
    NInf = len(InfList)
       
    print 'RSC_Name is : ' + RSC_list
    RSCList = read_list(RSC_list)
    RSC =RSCList[0]
    rsc_dic = read_roipac_rsc(RSC)
    nWidth = rsc_dic['WIDTH']
    nLine  = rsc_dic['FILE_LENGTH']
    UNWList = read_list(UNW_list)  
    CORList = read_list(COR_list) 
    Flag_K = 0
    if inps.coherence:
        Flag_K = 1
        print ''
        print 'COR_Name is : ' + COR_list   
        load_gamma2multi_group_h5('coherence','coherence', CORList, RSCList, dtype_cor)
    elif inps.wrapIfgram:
        Flag_K = 1
        print ''
        print 'IFG_Name is : ' + IFG_list 
        load_gamma2multi_group_h5('wrapped','wrapIfgram', InfList, RSCList, dtype_inf)
    elif inps.unwrapIfgram:
        Flag_K = 1
        print ''
        print 'UNW_Name is : ' + UNW_list
        load_gamma2multi_group_h5('interferograms','unwrapIfgram', UNWList, RSCList, dtype_unw)
    elif inps.demGeo:
        Flag_K = 1
        print ''
        print 'Start to write GEO-DEM into h5 file >>> ' + UTMDEM
        data = read_data(UTMDEM, dtype_utmdem, nWidthUTM, nLineUTM)
        H5FILE = 'demGeo.h5'
        f =h5py.File(H5FILE,'w')
        group=f.create_group('dem')
        dset = group.create_dataset('dem', data=data, compression='gzip')
        group.attrs['WIDTH'] = nWidthUTM
        group.attrs['FILE_LENGTH'] = nLineUTM
        group.attrs['X_FIRST'] = Corner_LON    # X: latitude    Y: longitude
        group.attrs['Y_FIRST'] = Corner_LAT
        group.attrs['X_STEP'] = post_Lon
        group.attrs['Y_STEP'] = post_Lat
        group.attrs['X_UNIT'] = 'degrees'
        group.attrs['Y_UNIT'] = 'degrees'
        group.attrs['X_MIN'] = '0'
        group.attrs['X_MAX'] = str(int(nWidthUTM)-1)
        group.attrs['Y_MIN'] = '0'
        group.attrs['Y_MAX'] = str(int(nLineUTM)-1)
        group.attrs['DATATYPE'] = dtype_utmdem
        group.attrs['COORD'] = 'geo'
        group.attrs['PROCCESSOR'] = 'gamma'
        f.close()
    elif inps.demRdc:
        Flag_K = 1
        print ''
        print 'Start to write RDC-DEM into h5 file >>> ' + RDCDEM
        data = read_data(RDCDEM, dtype_rdcdem, nWidth, nLine)
        H5FILE = 'demRdc.h5'
        f =h5py.File(H5FILE,'w')
        group=f.create_group('dem')
        dset = group.create_dataset('dem', data=data, compression='gzip')
        group.attrs['PROCCESSOR'] = 'gamma'
        group.attrs['WIDTH'] = nWidth
        group.attrs['FILE_LENGTH'] = nLine
        group.attrs['X_MIN'] = '0'
        group.attrs['X_MAX'] = str(int(nWidth)-1)
        group.attrs['Y_MIN'] = '0'
        group.attrs['Y_MAX'] = str(int(nLine)-1)
        group.attrs['DATATYPE'] = dtype_rdcdem
        group.attrs['COORD'] ='radar'
        f.close()
    elif inps.geo2rdc:
        Flag_K = 1
        print ''
        print 'Start to write GEO2RDC into h5 file >>> ' + UTM2RDC
        data = read_data(UTM2RDC,dtype_lt,nWidthUTM,nLineUTM)   # real: range     imaginary: azimuth
        H5FILE = 'geo2rdc.h5'
        f =h5py.File(H5FILE,'w')
        group=f.create_group('lt')
        dset = group.create_dataset('lt', data=data, compression='gzip')
        group.attrs['WIDTH'] = nWidthUTM
        group.attrs['FILE_LENGTH'] = nLineUTM
        group.attrs['X_FIRST'] = Corner_LON    # X: latitude    Y: longitude
        group.attrs['Y_FIRST'] = Corner_LAT
        group.attrs['X_STEP'] = post_Lon
        group.attrs['Y_STEP'] = post_Lat
        group.attrs['X_UNIT'] = 'degrees'
        group.attrs['Y_UNIT'] = 'degrees'
        group.attrs['X_MIN'] = '0'
        group.attrs['X_MAX'] = str(int(nWidthUTM)-1)
        group.attrs['Y_MIN'] = '0'
        group.attrs['Y_MAX'] = str(int(nLineUTM)-1)
        group.attrs['DATATYPE'] = dtype_utmdem
        group.attrs['COORD'] = 'geo'
        group.attrs['PROCCESSOR'] = 'gamma'
        f.close()
    
    
    
    if not os.path.isfile('wrapIfgram.h5') and Flag_K==0:
        print ''
        print 'IFG_Name is : ' + IFG_list 
        load_gamma2multi_group_h5('wrapped','wrapIfgram', InfList, RSCList, dtype_inf)
    else:
        print ''
        print 'wrapIfgram.h5 has existed, loading wrapped interferograms is skipped.'
    

      
    if not os.path.isfile('unwrapIfgram.h5') and Flag_K==0:
        print ''
        print 'UNW_Name is : ' + UNW_list
        load_gamma2multi_group_h5('interferograms','unwrapIfgram', UNWList, RSCList, dtype_unw)
    else:
        print ''
        print 'unwrapIfgram.h5 has existed, loading unwrapped interferograms is skipped.'
    
    
    if not os.path.isfile('coherence.h5') and Flag_K==0:        
        print ''
        print 'COR_Name is : ' + COR_list   
        load_gamma2multi_group_h5('coherence','coherence', CORList, RSCList, dtype_cor)
    else:
        print ''
        print 'coherence.h5 has existed, loading coherence is skipped.'
    
    
#########  load DEM and lookup table ##########  
    
    if not os.path.isfile('demGeo.h5') and Flag_K==0:
        print ''
        print 'Start to write GEO-DEM into h5 file >>> ' + UTMDEM
        data = read_data(UTMDEM, dtype_utmdem, nWidthUTM, nLineUTM)
        H5FILE = 'demGeo.h5'
        f =h5py.File(H5FILE,'w')
        group=f.create_group('dem')
        dset = group.create_dataset('dem', data=data, compression='gzip')
        group.attrs['WIDTH'] = nWidthUTM
        group.attrs['FILE_LENGTH'] = nLineUTM
        group.attrs['X_FIRST'] = Corner_LON    # X: latitude    Y: longitude
        group.attrs['Y_FIRST'] = Corner_LAT
        group.attrs['X_STEP'] = post_Lon
        group.attrs['Y_STEP'] = post_Lat
        group.attrs['X_UNIT'] = 'degrees'
        group.attrs['Y_UNIT'] = 'degrees'
        group.attrs['X_MIN'] = '0'
        group.attrs['X_MAX'] = str(int(nWidthUTM)-1)
        group.attrs['Y_MIN'] = '0'
        group.attrs['Y_MAX'] = str(int(nLineUTM)-1)
        group.attrs['DATATYPE'] = dtype_utmdem
        group.attrs['COORD'] = 'geo'
        group.attrs['PROCCESSOR'] = 'gamma'
        f.close()
    else:
        print ''
        print 'demGeo.h5 has existed, loading GEO-DEM is skipped.'
    
    
    if not os.path.isfile('demRdc.h5') and Flag_K==0:
        print ''
        print 'Start to write RDC-DEM into h5 file >>> ' + RDCDEM
        data = read_data(RDCDEM, dtype_rdcdem, nWidth, nLine)
        H5FILE = 'demRdc.h5'
        f =h5py.File(H5FILE,'w')
        group=f.create_group('dem')
        dset = group.create_dataset('dem', data=data, compression='gzip')
        group.attrs['PROCCESSOR'] = 'gamma'
        group.attrs['WIDTH'] = nWidth
        group.attrs['FILE_LENGTH'] = nLine
        group.attrs['X_MIN'] = '0'
        group.attrs['X_MAX'] = str(int(nWidth)-1)
        group.attrs['Y_MIN'] = '0'
        group.attrs['Y_MAX'] = str(int(nLine)-1)
        group.attrs['DATATYPE'] = dtype_rdcdem
        group.attrs['COORD'] ='radar'
        f.close()
    else:
        print ''
        print 'demRdc.h5 has existed, loading RDC-DEM is skipped.'
    
    
    if not os.path.isfile('geo2rdc.h5') and Flag_K==0:
        print ''
        print 'Start to write GEO2RDC into h5 file >>> ' + UTM2RDC
        data = read_data(UTM2RDC,dtype_lt,nWidthUTM,nLineUTM)   # real: range     imaginary: azimuth
        H5FILE = 'geo2rdc.h5'
        f =h5py.File(H5FILE,'w')
        group=f.create_group('lt')
        dset = group.create_dataset('lt', data=data, compression='gzip')
        group.attrs['WIDTH'] = nWidthUTM
        group.attrs['FILE_LENGTH'] = nLineUTM
        group.attrs['X_FIRST'] = Corner_LON    # X: latitude    Y: longitude
        group.attrs['Y_FIRST'] = Corner_LAT
        group.attrs['X_STEP'] = post_Lon
        group.attrs['Y_STEP'] = post_Lat
        group.attrs['X_UNIT'] = 'degrees'
        group.attrs['Y_UNIT'] = 'degrees'
        group.attrs['X_MIN'] = '0'
        group.attrs['X_MAX'] = str(int(nWidthUTM)-1)
        group.attrs['Y_MIN'] = '0'
        group.attrs['Y_MAX'] = str(int(nLineUTM)-1)
        group.attrs['DATATYPE'] = dtype_utmdem
        group.attrs['COORD'] = 'geo'
        group.attrs['PROCCESSOR'] = 'gamma'
        f.close()
    else:
        print ''
        print 'geo2rdc.h5 has existed, loading lookup table is skipped.'
           
    print ''
    print 'Done.\nLoading data spend ' + str(time.time()-total) +' secs'
    sys.exit(1)    


##############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
