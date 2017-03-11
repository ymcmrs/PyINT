# PyGAMMA   

###Bratch processing for generating Interferograms based on python and GAMMA.      

Available SAR sensors:  ERS, ASAR, ALOS-1/2, Sentinal-1A/B..   All possible Sensors should be updated into these scripts.          

If you want to make the scripts work smooth, you should obey the following rules :            

####1) $SCRATCHDIR and $TEMPLATEDIR should be available in your system environment. $SCRATCHDIR for processing, $TEMPLATEDIR for template files:            
      setenv SCRATCHDIR /Users/Yunmeng/Documents/SCRATCH       
      setenv TEMPLATEDIR /Users/Yunmeng/Documents/development/TEMPLATEDIR    
      ...    
          
####2) The correct folders sequence should be:   
     $SCRATCHDIR/PROJECTNAME/SLC       (SLC folder should be available!!!)  
     $SCRATCHDIR/PROJECTNAME/PROCESS/ifgramDir  
     ...     
        
        
####3) pysar based _readfile.py  should be available.  So you'd better have pysar:       
      git clone https://github.com/ymcmrs/PySAR.git    
      ...    
      
####4) ifgramDir should be named like:  IFGRAM_PacayaT120F107AlosA_20080101-20090101_0111-0123   
     
     
If you set all the above OK, then these scripts shoul work for you! If you can share some advices or ideas about python, GAMMA, InSAR processing ..., I would be very grateful and glad to communicate with you!        
   
   
Wish these scripts can help you for InSAR processing!! Enjoy it!  Any advices or problems would be very welcomed!  Do not hesitate to contact me: ymcmrs@gmail.com        
 
   
   
 March 10, 2017   Yunmeng    
