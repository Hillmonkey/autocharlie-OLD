# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29, 2016

NNN-cron.py

"""

import local
#from UploadArchiveLib import new2current, closeConnection
import UploadArchiveLib as UAL
import datetime as DT
from dateutil.relativedelta import relativedelta
    
remotePath = local.remote
           

print '===================================================================='
print 'NNN-cron.py ', str(DT.datetime.now() + relativedelta(microsecond=0))
print '===================================================================='    

	    
rootFolder = ''.join((local.remoteStub,'Audio3/'))

# datetime object to time tuple:
# time_tuple = dt_obj.timetuple()

# Nearly Noon News, this job should run Mon - Fri @ 12:15
# Running this at a particular time is controlled by editing crontab
# http://www.unixgeeks.org/security/newbie/unix/cron-1.html

now = DT.datetime.now() + relativedelta(microsecond=0)
aday = UAL.num2dayShort[now.weekday()] # 3 letter string (ex: 'Mon')
nowtuple = now.timetuple()

#time is in military time (from 00:00 to 23:59, every day!)
startTuple =(11, 55, 0) # 11:55am
endTuple = (12, 2, 30) # 12:02:30 -just past noon
start = UAL.fullTimeTuple(startTuple, DT.datetime.now()).timetuple()
end = UAL.fullTimeTuple( endTuple, DT.datetime.now()).timetuple()

# let's look at how the line below crafts a target folder 
targetFolder = ''.join((rootFolder, 'NNN/',aday,'/'))
# next line simply creates a new current.mp3 file and writes over the old one
sftp, success = UAL.new2current(start, end, targetFolder)


UAL.closeConnection(sftp)

print        
print '++++++++++++++++++++++++++++++++++++++++++++++'
print 'END of NNN-cron -> ', str(DT.datetime.now() + relativedelta(microsecond=0))
print '++++++++++++++++++++++++++++++++++++++++++++++'
print



        
