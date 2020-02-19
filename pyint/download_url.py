#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.0                      ### 
###  Copy Right (c): 2019, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : King Abdullah University of Science & Technology ###   
#################################################################
## This script is modified from SSARA

from __future__ import print_function
import os
import sys
import json
import datetime
import time
import csv
from xml.dom import minidom
import itertools
import operator
import re
import optparse
import threading
import subprocess as sub
try:
    # For Python 3.0 and later
    from urllib.request import urlopen,HTTPCookieProcessor,HTTPPasswordMgrWithDefaultRealm,HTTPBasicAuthHandler,HTTPDigestAuthHandler,build_opener,install_opener
    from urllib.parse import urlencode
    from urllib.error import HTTPError
    from queue import Queue
except ImportError:
    # Fall back to Python2
    from urllib2 import urlopen,HTTPCookieProcessor,HTTPPasswordMgrWithDefaultRealm,HTTPBasicAuthHandler,HTTPDigestAuthHandler,build_opener,install_opener,HTTPError
    from urllib import urlencode
    from Queue import Queue
import ssl

import argparse
from pyint import _utils as ut
        
###################################################################################################

INTRODUCTION = '''
Download file based on url list.

'''

EXAMPLE = '''EXAMPLES:

    download_url.py url_list username password
    download_url.py Tsx_r51_url ymcmrs cym6331099

'''    
    


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download file based on url list.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('url_list_txt',help='GPS station name.')
    parser.add_argument('user_name',help='user name.')
    parser.add_argument('password',help='password')
    parser.add_argument('--parallel', dest='parallelNumb', type=int, default=1, help='Enable parallel processing and Specify the number of processors.')
    inps = parser.parse_args()

    
    return inps

####################################################################################################
def main(argv):
    
    inps = cmdLineParse()
    url_txt = inps.url_list_txt
    user_name = inps.user_name
    password = inps.password
    url_list = ut.read_txt2list(url_txt)
    parallel0 = inps.parallelNumb
    
    print('Download file list: '+str(len(url_list)))
    
    print('Downloading data now, %s at a time.' % str(parallel0))
    #create a queue for parallel downloading
    queue = Queue()
    #spawn a pool of threads, and pass them queue instance 
    for i in range(parallel0):
        t = ThreadDownload(queue)
        t.setDaemon(True)
        t.start()
    #populate queue with data   
    for d in sorted(url_list):
        queue.put([d, user_name, password])
    #wait on the queue until everything has been processed     
    queue.join()
            
def url_dl(url0, user_name, password):
    user_name = user_name
    user_password = password
    url = url0
    filename = os.path.basename(url)
    if '.gz' in filename:
        filename = filename.replace('.gz','')
    path0 = os.getcwd()
    filename0 = path0 + '/' + filename
    secp_path = os.getenv('SSARAHOME')+"/data_utils/secp"
    cmd = """%s -C %s:%s %s""" % (secp_path,user_name,user_password,url0)
    print("Downloading:",url)
    start = time.time()
    pipe = sub.Popen(cmd, shell=True, stdout=sub.PIPE, stderr=sub.STDOUT).stdout
    pipe.read()
    total_time = time.time() - start
    mb_sec = (os.path.getsize(filename0) / (1024 * 1024.0)) / total_time
    print("%s download time: %.2f secs (%.2f MB/sec)" % (filename, total_time, mb_sec))
    
class ThreadDownload(threading.Thread):
    """Threaded SAR data download"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url0, user_name, password = self.queue.get()
            url_dl(url0, user_name, password)
            self.queue.task_done()
        
if __name__ == '__main__':
    main(sys.argv[1:])
