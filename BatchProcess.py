#! /usr/bin/env python

#'''
######################################################################
###         Author:    Yun-Meng Cao                                ### 
###         Date  :   March, 2017                                  ###  
###         Email :   ymcmrs@gmail.com                             ###   
###          Batch processing in pegasus                           ###    
######################################################################
#'''


import numpy as np
import os
import sys
import getopt
import array

#########################################################################

def usage():
    print 
    '''
******************************************************************************************************
 
                           Batch processing for one job
                         

   usage:
   
            BatchProcess.py -p run_txt -m memory -t walltime
      e.g.  BatchProcess.py -p /Users/Yunmeng/run_slc2ifg -m 3700 -t 2:00
          
            -p  : run txt
            -m  : memory used for processing
            -t  : maximum time used for processing

*******************************************************************************************************
'''   

def main(argv):
    
    Memory   = '3700'
    Walltime = '2:00'
    
    if len(sys.argv)> 2:
        try:opts,args=getopt.getopt(argv,'p:m:t:h:')
        except getopt.GetoptError: print 'Error while getting args'; usage();sys.exit(1)
        
        for opt,arg in opts:
            if   opt in ['h','--help']: usage();sys.exit(1)
            elif opt in '-p': RunFile     =  arg
            elif opt in '-m': Memory      =  arg
            elif opt in '-b': Walltime    =  arg    
                    
    elif len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        elif argv[0] in ['-p']: RunFile = argv[0]
    
    else:
        usage();sys.exit(1)
   
    call_str='$INT_SCR/createBatch.pl ' + RunFile + ' memory=' + Memory + ' walltime=' + Walltime
    os.system(call_str)
                        
    print "Batch processing done!"
    sys.exit(1)
    
    

if __name__ == '__main__':
    main(sys.argv[1:])
