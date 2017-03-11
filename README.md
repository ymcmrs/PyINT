# PyGAMMA
Generating interferograms based on python and GAMMA

Following rules should be obey:

1) $SCRATCHDIR and $TEMPLATEDIR should be available in your system environment. $SCRATCHDIR for processing, $TEMPLATEDIR for template files  
    e.g., setenv SCRATCHDIR /Users/Yunmeng/Documents/SCRATCH  
          setenv TEMPLATEDIR /Users/Yunmeng/Documents/development/TEMPLATEDIR  
          
2) The correct folders sequence should be:   
     $SCRATCHDIR/PROJECTNAME/SLC       (SLC folder should be available!!!)  
     $SCRATCHDIR/PROJECTNAME/PROCESS/ifgramDir  
     ...
  
 3) pysar based _readfile.py  should be available.  So you'd better have pysar: 
      git clone https://github.com/ymcmrs/PySAR.git
      
 4) ifgramDir should be named like:  IFGRAM_PacayaT120F107AlosA_20080101-20090101_0111-0123
 
 
 If you set all the above OK, then these scripts shoul work for you!  Good luck.
 Any problems, do not hesitate to contact: ymcmrs@gmail.com
 
 March 10, 2017   Yunmeng
