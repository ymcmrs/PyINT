#! /usr/bin/env python
############################################################                                                     
# Program is part of TSSAR   v1.2                          #
# Copyright(c) 2017, Yunmeng Cao                           #
# Author :  Yunmeng Cao                                    # 
# Company:  Central South University                       #                                                       
############################################################

import os
import sys
import glob
import time
import argparse
import getopt

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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def read_data(inFile, dtype, nWidth, nLength):
    data = np.fromfile(inFile, dtype, int(nLength)*int(nWidth)).reshape(int(nLength),int(nWidth))  
    return data    
    
def usage():
    print '''
******************************************************************************************************
 
           Unwrap subset interferograms based on H5 file of interferograms.

           usage:
   
                 unwarp_sub_tssar.py -f INFH5 -w CORH5 -o OUTFILE --threshold CORTHRESHOLD
      
           e.g.  unwarp_sub_tssar.py -f wrapIfgram_proc.h5 -w coherence_proc.h5 -o unwrap_tssar.h5 -m 0.3
           e.g.  unwarp_sub_tssar.py -f wrapIfgram_proc.h5 -w coherence_proc.h5
          
                 -f : wrapped interferograms h5 file
                 -w : weight h5 file
                 -o : output h5 file
                 -m : cohrence threshold for unwrapping 
*******************************************************************************************************
    '''   

def main(argv):
    
    total = time.time()
    unwThreshold = ''
    OUTFILE = ''
    if len(sys.argv)> 2:
        try:opts,args=getopt.getopt(argv,"f:w:o:m:")
        except getopt.GetoptError: print 'Error while getting args'; usage();sys.exit(1)
        
        for opt,arg in opts:
            if   opt in ['h','--help']: usage();sys.exit(1)
            elif opt in '-f': INFH5       = arg
            elif opt in '-w': CORH5       = arg
            elif opt in '-o': OUTFILE     = arg    
            elif opt in '-m': unwThreshold   = arg
    elif len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
    else:
        usage();sys.exit(1)

    f_inf = h5py.File(INFH5,'r')
    f_cor = h5py.File(CORH5,'r')
    
    if len(OUTFILE)>0:
        UNWH5 = OUTFILE
    else:
        UNWH5 = 'unwrapIfgram_mcf_proc.h5'
    print 'Output unwrapped h5 file %s.' % UNWH5
    
    f_unw = h5py.File(UNWH5,'w')
    group = f_unw.create_group('interferograms')
    
    TS_INF = f_inf[f_inf.keys()[0]].keys()
    TS_COR = f_cor[f_cor.keys()[0]].keys()
    atr = f_inf[f_inf.keys()[0]][TS_INF[0]].attrs
    projectName = atr['PROJECT']
#    projectName = 'PichinchaSMT51TsxD'
    nWidth = atr['WIDTH']
    nLine = atr['FILE_LENGTH']
    DATATYPE = atr['DATATYPE']
#    DATATYPE = '>c8'
    sign = DATATYPE[0]
    dtype_unw = sign + 'f4'
    
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    if 'UnwrappedThreshold' in templateContents: unwThreshold0 = templateContents['UnwrappedThreshold']
    else: unwThreshold0 = '0.3'
    
    if not is_number(unwThreshold):
        unwThreshold = unwThreshold0
    
    print 'Unwrap threshold is %s.' % unwThreshold
    
    fileNum = len(TS_INF)
    
    for i in range(len(TS_INF)):
        
        MASK =np.ones([int(nLine),int(nWidth)])
        INF = TS_INF[i]
        COR = TS_COR[i]
        MASKNAME = COR.replace('cor','bmp')
        UNWNAME = COR.replace('cor','unw')
        
        print_progress(i+1, fileNum, prefix='Unwrapping ', suffix=os.path.basename(INF))
        atr = f_inf[f_inf.keys()[0]][TS_INF[i]].attrs
        
        gg = group.create_group(UNWNAME)
        for key,value in atr.iteritems():   gg.attrs[key] = value
            
        data_inf = f_inf[f_inf.keys()[0]][INF].get(INF)[()]
        data_cor = f_cor[f_cor.keys()[0]][COR].get(COR)[()]
        ndx = data_cor < float(unwThreshold)
        MASK[ndx]=0
        if not sys.byteorder == 'big':
            MASK.byteswap(True)
        
        data_inf.tofile(INF)
        data_cor.tofile(COR)

        
        call_str = 'rascc_mask ' + COR + ' - ' + nWidth + ' - - - - - ' +  unwThreshold + ' - - - - - - ' + MASKNAME + '> tt'
        os.system(call_str)
        
        call_str = 'mcf ' + INF + ' ' + COR + ' ' + MASKNAME + ' ' + UNWNAME + ' ' + nWidth + ' 1 - - > tt'
        os.system(call_str)
        data = read_data(UNWNAME, dtype_unw, nWidth, nLine)
        dset  = gg.create_dataset(UNWNAME, data = data, compression='gzip')
        gg.attrs['DATATYPE'] = dtype_unw
        
    f_inf.close()
    f_cor.close()
    f_unw.close()
    call_str = 'rm *diff*'
    os.system(call_str)
    
    print ''
    print 'Done.\nUnwrapping subset interferograms spend ' + str(time.time()-total) +' secs'    
    sys.exit(1)

##############################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
