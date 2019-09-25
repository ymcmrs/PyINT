############################################################
# Program is part of PyINT V2.1                            #
# Copyright 2017-2019 Yunmeng Cao                          #
# Contact: ymcmrs@gmail.com                                #
############################################################
#from datetime import datetime
import datetime
import urllib.request
import os
import numpy as np
import random
import h5py
from pathlib import Path
import linecache
import time
import glob

from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

#######################  update template #############################
def update_template(template_file):
    
    templateDict = {}
    templateDict['start_swath'] = '1' 
    templateDict['end_swath'] = '3'
    
    templateDict['start_burst'] = '1'    
    templateDict['end_burst'] = '20'
    
    templateDict['dem_lat_ovr'] = '0.5'  # get 30m resolution of lookup table, 0.5 to 60m, 2 to 15m
    templateDict['dem_lon_ovr'] = '0.5'  # get 30m resolution of lookup table
    
    templateDict['Igram_Spsflg'] = '1'  # Range spectral filtering
    templateDict['Igram_Azfflg'] = '1'  # Azimuth common band filtering
    
    templateDict['rwin4cor'] = '256'  # range window length for coregistration
    templateDict['azwin4cor'] = '256'  # azimuth window length for coregistration
    
    templateDict['rsample4cor']  = '32'        #  range samples used for fitting the coregistration parameters
    templateDict['azsample4cor']  = '32'        #  azimuth samples used for fitting the coregistration parameters
    
    templateDict['thresh4cor']   = '0.15'      # 2016 GAMMA or higher version, for 2015 GAMMA or lower version should be SNR

    templateDict['coreCoarse']  = 'both'  # initial coregistration method, [options: orbit, ampcor, both]
    templateDict['coreMethod']  = 'DEM'   # coregistration method [option: DEM, init]  DEM means with DEM assistant
    
    templateDict['Igram_Cor_rwin'] = '5' # used for cc_wave
    templateDict['Igram_Cor_awin'] = '5'  # used for cc_wave
    
    templateDict['Igram_Cor_Win'] = '5' # used for adf
    templateDict['adf_alpha'] = '0.4' # used for adf
    ######## sim phase ##################
    templateDict['Igram_Flag_TDM'] = 'N'
    templateDict['Simphase_rpos'] = '-'
    templateDict['Simphase_azpos'] = '-'               
    templateDict['Simphase_rwin'] = '256'
    templateDict['Simphase_azwin'] = '256'
    templateDict['Simphase_thresh'] = '-'
    
    #### unwrap phase ###########
    templateDict['mcf_triangular'] = '0'    # triangular type of mcf [0: regular; 1: delaunay;] 
    templateDict['unwrap_patr'] = '1'
    templateDict['unwrap_pataz'] = '1'
    templateDict['unwrapThreshold'] = '0.1'  # minimum coherence used for unwrap
    
    #### geocode #########
    templateDict['geo_interp'] = '0' #  [0: nearest; 1: bicubic spline]
    
    ############## interferometry ################
    templateDict['int_flag'] = '1'       # 1 means do interferometry 
    templateDict['diff_flag'] = '1'      # differential process, i.e., remove DEM phase
    templateDict['unw_flag'] = '1'       # unwrap process
    templateDict['geo_flag'] = '0'       # geocode process  
    
    ############## select network #############
    templateDict['endDate'] = '99999999'
    templateDict['startDate'] = '19000101'
    templateDict['network_method'] = 'sbas'     # sbas, sequential, delaunay, stars
    templateDict['conNumb'] = '2'               # connect number for sequential
    templateDict['max_tb'] = '50000'  
    templateDict['max_sb'] = '50000'
    
     ############## time-series ################
    templateDict['coreg_all'] = '1'     
    templateDict['select_pairs'] = '1'  
    templateDict['load_data'] = '0'
    
    templateDict0 = read_template(template_file, delimiter='=')
    for key, value in templateDict0.items():
        templateDict[key] = str(value)
    
    return templateDict
    
####################### time-related function ################

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def print_process_time(start, end):
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Total process time: "+"{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    return

def date_add1d(date0):
    format_str = '%Y%m%d' # The format
    date_obj = datetime.datetime.strptime(date0,format_str)
    date1 = (date_obj + datetime.timedelta(days=1)).date().strftime('%Y%m%d')
    return date1

def date_minus1d(date0):
    format_str = '%Y%m%d' # The format
    date_obj = datetime.datetime.strptime(date0,format_str)
    date1 = (date_obj - datetime.timedelta(days=1)).date().strftime('%Y%m%d')
    return date1


def generate_random_name(sufix):
    
    nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S") #generate the present time
    randomNum = random.randint(0,100)
    randomNum1 = random.randint(0,100)
    Nm = nowTime + str(randomNum)+ str(randomNum1)  + sufix
    
    return Nm

def yyyymmdd2yyyyddd(date):
    dt = datetime.datetime.strptime(date, "%Y%m%d") # get datetime object
    day_of_year = (dt - datetime.datetime(dt.year, 1, 1))  # Jan the 1st is day 1
    doy = day_of_year.days + 1
    year = dt.year
    
    doy = str(doy)
    if len(doy) ==1:
        doy = '00' + doy
    elif len(doy) ==2:
        doy ='0'+ doy
    year = str(year)
    
    return year, doy

def read_txt2list(txt):
    A = np.loadtxt(txt,dtype=np.str)
    if isinstance(A[0],bytes):
        A = A.astype(str)
    A = list(A)    
    return A

def read_txt2array(txt):
    A = np.loadtxt(txt,dtype=np.str)
    if isinstance(A[0],bytes):
        A = A.astype(str)
    #A = list(A)    
    return A

def get_filelist_filesize(url0):
    ttt = generate_random_name('.txt')
    call_str = 'curl -s ' + url0 + ' > ' + ttt 
    os.system(call_str)
    A = read_txt2array(ttt)
    
    A_size = A[:,4]
    A_size = A_size.astype(int)
    A_size = A_size/1024/1024  #bytes to Mb
    A_name = A[:,8]
    if os.path.isfile(ttt):
        os.remove(ttt)
        
    return A_name, A_size

def yyyymmdd(date0):
    if len(date0) ==6:
        if float(date0[0:2]) > 90:
            date1 = '19' + date0
        else:
            date1 = '20' + date0         
    elif len(date0) ==8:
        date1 = date0
    else:
        print('The input date is invalid!!')
        date1 = ''
    return date1
    
def yymmdd(date0):
    if len(date0) ==6:
        date1 = date0        
    elif len(date0) ==8:
        date1 = date0[2:8]
    else:
        print('The input date is invalid!!')
        date1 = ''
    return date1
    
def parallel_process(array, function, n_jobs=16, use_kwargs=False):
    """
        A parallel version of the map function with a progress bar. 

        Args:
            array (array-like): An array to iterate over.
            function (function): A python function to apply to the elements of array
            n_jobs (int, default=16): The number of cores to use
            use_kwargs (boolean, default=False): Whether to consider the elements of array as dictionaries of 
                keyword arguments to function 
        Returns:
            [function(array[0]), function(array[1]), ...]
    """
    #We run the first few iterations serially to catch bugs
    #If we set n_jobs to 1, just run a list comprehension. This is useful for benchmarking and debugging.
    if n_jobs==1:
        return [function(**a) if use_kwargs else function(a) for a in tqdm(array[:])]
    #Assemble the workers
    with ProcessPoolExecutor(max_workers=n_jobs) as pool:
        #Pass the elements of array into function
        if use_kwargs:
            futures = [pool.submit(function, **a) for a in array[:]]
        else:
            futures = [pool.submit(function, a) for a in array[:]]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }
        #Print out the progress as tasks complete
        for f in tqdm(as_completed(futures), **kwargs):
            pass
    out = []
    #Get the results from the futures. 
    for i, future in tqdm(enumerate(futures)):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return out    

def sort_unique_list(numb_list):
    list_out = sorted(set(numb_list))
    return list_out 


############################# download data ###################################
def StrNum(S):
    S = str(S)
    if len(S)==1:
        S='0' +S
    return S

def download_s1_orbit(date,save_path,satellite='A'):
    
    DATE = date
    if len(DATE)==6:
        DATE = '20' + DATE
    ST = satellite
    YEAR = int(DATE[0:4])
    MON = int(DATE[4:6])
    DAY = int(DATE[6:8])
 
    MON_DAY = [31,28,31,30,31,30,31,31,30,31,30,31]
    
    if YEAR%4==0:
        MON_DAY[1]=29
      
    if MON ==1 and DAY ==1:
        DAY0 = 31
        MON0 = 12
        YEAR0 =YEAR -1
    elif MON!=1 and DAY ==1:
        DAY0 = MON_DAY[MON-2]
        MON0 = MON-1
        YEAR0 = YEAR
    else:
        DAY0 = DAY -1
        MON0 = MON
        YEAR0 = YEAR
    
    MONDAY0 = MON_DAY[MON0-1]
    
    TT = [1,4,7,10,13,16,19,22,25,28,MONDAY0] 

    T0 = []
    for k in range(len(TT)):
        T0.append(TT[k])
        TT[k] = TT[k]-DAY0

    for k in range(len(TT)):
        if k == len(TT)-1:
            if TT[k]==0: 
                ff = k-1
        else:
            if TT[k]<=0 and TT[k+1]>0:
                ff = k
            
  
    DAY1 = T0[ff]
    DAY2 = T0[ff+1]
    
    S1 = StrNum(YEAR0) + '-' + StrNum(MON0)
    S2 = StrNum(YEAR0) + '-' + StrNum(MON0) + '-' + StrNum(DAY1)
    S3 = StrNum(YEAR0) + '-' + StrNum(MON0) + '-' + StrNum(DAY2)
    S4 = StrNum(YEAR0) + '-' + StrNum(MON0) + '-' + StrNum(DAY0)
    
    #SS = 'https://qc.sentinel1.eo.esa.int/aux_poeorb/?mission=S1' + ST + '&validity_start_time=' + StrNum(YEAR0) + '&validity_start_time=' + S1 + '&validity_start_time=' + S2 + '..' + S3 + '&validity_start_time=' + S4
    SS = 'https://qc.sentinel1.eo.esa.int/aux_poeorb/?validity_start=' + StrNum(YEAR0) + '&validity_start=' + S1 + '&validity_start=' + S2 + '..' + S3 + '&validity_start=' +S4 + '&sentinel1__mission=S1'+ST+ '&sentinel1_mission=S1'+ST+ '&sentinel1_mission=S1'+ST+ '&sentinel1_mission=S1'+ST

    tt ='tt_orb_' + date
    tt0 ='tt0_orb_' + date
    tt00 ='tt00_orb_' + date
    tt000 ='tt000_orb_' + date
    SS = "'" + SS + "'"
    #print(SS)
    call_str = 'curl -s -l ' + SS + ' > ' + tt
    os.system(call_str)
    
    call_str = "grep 'EOF' -C 0 " + tt + " >" + tt0
    os.system(call_str)
    
    call_str="awk -F'href=' '{print $2}' " + tt0 +' >' + tt00
    os.system(call_str)
    
    call_str= "awk -F'>' '{print $1}' " + tt00 + '> ' + tt000
    os.system(call_str)
    
    SS=linecache.getline(tt000, 1)
    SS = SS.split('"')[1]
    filename = os.path.basename(SS)
    call_str = 'wget -q --no-check-certificate ' + SS + ' -O ' + save_path + '/' +filename
    os.system(call_str)
    
    filename = os.path.basename(SS)
    os.remove(tt)
    os.remove(tt0)
    os.remove(tt00)
    os.remove(tt000)
    
    return filename
    

############################# write & read #####################################
def copy_file(file0,file1):
    call_str = 'cp ' + file0 + ' ' + file1
    os.system(call_str)
    
    return

def get_project_slcList(projectName):
    scratchDir = os.getenv('SCRATCHDIR')    
    slcDir     = scratchDir + '/' + projectName + "/SLC"    
    slc_list0 = [os.path.basename(fname) for fname in sorted(glob.glob(slcDir + '/*'))]
    
    slc_list = []
    for k0 in slc_list0:
        if is_number(k0):
            slc_list.append(k0)
    slc_list = sorted(slc_list)
    
    return slc_list
            
def createBlankFile(strFile):
    f = open(strFile,'w')
    for i in range (10):
        f.write('\n')
    f.close()
    
def read_attr(fname):
    # read hdf5
    with h5py.File(fname, 'r') as f:
        atr = dict(f.attrs)
        
    return atr

def read_hdf5(fname, datasetName=None, box=None):
    # read hdf5
    with h5py.File(fname, 'r') as f:
        data = f[datasetName][:]
        atr = dict(f.attrs)
        
    return data, atr

def get_dataNames(FILE):
    with h5py.File(FILE, 'r') as f:
        dataNames = []
        for k0 in f.keys():
            dataNames.append(k0)
    return dataNames

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

def read_gamma_par(inFile, task, keyword):
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
        

def write_h5(datasetDict, out_file, metadata=None, ref_file=None, compression=None):

    if os.path.isfile(out_file):
        print('delete exsited file: {}'.format(out_file))
        os.remove(out_file)

    print('create HDF5 file: {} with w mode'.format(out_file))
    dt = h5py.special_dtype(vlen=np.dtype('float64'))

    
    with h5py.File(out_file, 'w') as f:
        for dsName in datasetDict.keys():
            data = datasetDict[dsName]
            ds = f.create_dataset(dsName,
                              data=data,
                              compression=compression)
        
        for key, value in metadata.items():
            f.attrs[key] = str(value)
            #print(key + ': ' +  value)
    print('finished writing to {}'.format(out_file))
        
    return out_file 
    
######################################################################
class progressBar:
    """Creates a text-based progress bar. Call the object with 
    the simple print command to see the progress bar, which looks 
    something like this:
    [=======> 22%       ]
    You may specify the progress bar's min and max values on init.

    note:
        modified from mintPy (https://github.com/insarlab/MintPy/wiki)
        Code originally from http://code.activestate.com/recipes/168639/

    example:
        from mintpy.utils import ptime
        date12_list = ptime.list_ifgram2date12(ifgram_list)
        prog_bar = ptime.progressBar(maxValue=1000, prefix='calculating:')
        for i in range(1000):
            prog_bar.update(i+1, suffix=date)
            prog_bar.update(i+1, suffix=date12_list[i])
        prog_bar.close()
    """

    def __init__(self, maxValue=100, prefix='', minValue=0, totalWidth=70, print_msg=True):
        self.prog_bar = "[]"  # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.suffix = ''
        self.prefix = prefix

        self.print_msg = print_msg
        ## calculate total width based on console width
        #rows, columns = os.popen('stty size', 'r').read().split()
        #self.width = round(int(columns) * 0.7 / 10) * 10
        self.width = totalWidth
        self.reset()

    def reset(self):
        self.start_time = time.time()
        self.amount = 0  # When amount == max, we are 100% done
        self.update_amount(0)  # Build progress bar string

    def update_amount(self, newAmount=0, suffix=''):
        """ Update the progress bar with the new amount (with min and max
        values set at initialization; if it is over or under, it takes the
        min or max value as a default. """
        if newAmount < self.min:
            newAmount = self.min
        if newAmount > self.max:
            newAmount = self.max
        self.amount = newAmount

        # Figure out the new percent done, round to an integer
        diffFromMin = np.float(self.amount - self.min)
        percentDone = (diffFromMin / np.float(self.span)) * 100.0
        percentDone = np.int(np.round(percentDone))

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2 - 18
        numHashes = (percentDone / 100.0) * allFull
        numHashes = np.int(np.round(numHashes))

        # Build a progress bar with an arrow of equal signs; special cases for
        # empty and full
        if numHashes == 0:
            self.prog_bar = '%s[>%s]' % (self.prefix, ' '*(allFull-1))
        elif numHashes == allFull:
            self.prog_bar = '%s[%s]' % (self.prefix, '='*allFull)
            if suffix:
                self.prog_bar += ' %s' % (suffix)
        else:
            self.prog_bar = '[%s>%s]' % ('='*(numHashes-1), ' '*(allFull-numHashes))
            # figure out where to put the percentage, roughly centered
            percentPlace = int(len(self.prog_bar)/2 - len(str(percentDone)))
            percentString = ' ' + str(percentDone) + '% '
            # slice the percentage into the bar
            self.prog_bar = ''.join([self.prog_bar[0:percentPlace],
                                     percentString,
                                     self.prog_bar[percentPlace+len(percentString):]])
            # prefix and suffix
            self.prog_bar = self.prefix + self.prog_bar
            if suffix:
                self.prog_bar += ' %s' % (suffix)
            # time info - elapsed time and estimated remaining time
            if percentDone > 0:
                elapsed_time = time.time() - self.start_time
                self.prog_bar += '%5ds / %5ds' % (int(elapsed_time),
                                                  int(elapsed_time * (100./percentDone-1)))

    def update(self, value, every=1, suffix=''):
        """ Updates the amount, and writes to stdout. Prints a
         carriage return first, so it will overwrite the current
          line in stdout."""
        if value % every == 0 or value >= self.max:
            self.update_amount(newAmount=value, suffix=suffix)
            if self.print_msg:
                sys.stdout.write('\r' + self.prog_bar)
                sys.stdout.flush()

    def close(self):
        """Prints a blank space at the end to ensure proper printing
        of future statements."""
        if self.print_msg:
            print(' ')