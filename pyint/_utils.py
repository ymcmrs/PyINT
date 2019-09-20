############################################################
# Program is part of PyINT                                 #
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

from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

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


############################# write & read #####################################
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

#######################################################################

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