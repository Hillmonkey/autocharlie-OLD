# -*- coding: utf-8 -*-
"""
Created on Wed May 11 15:58:25 2016

@author: lmadeo

HourlyCronLib.py
"""


def getCharlieSched():
    '''
    returns newest charlieSched from folder specified in key.charlieSched
    '''
    #save current working dir
    current = os.getcwd()
    charlieSched = SPlib.OpenPickle(SPlib.newestPickle(local.charlieSchedPath), 
                                    local.charlieSchedPath)
    #return to current working dir 
    os.chdir(current)
    return charlieSched
    
def getCurrentTime(endDelta):
    '''
    accepts:
        endDelta(int) represents minutes before or after the end of the show
            typically comes from local.endDelta
    returns:
        LastHour(int (0 .. 23))
        fullDayString (ex: 'Sunday')
    uses relative delta, so 1am minus two hours is 11pm, previous day
    '''
    Now = DT.datetime.now() + relativedelta(hour=0, minute=0, second=0, microsecond=0)
    ThisHour = DT.datetime.now() + relativedelta( minute=0, second=0, microsecond=0)
    print  'GT.ThisHour -> ',str(ThisHour)
    # if end of archive will spill over into next hour, wait an hour before 
    # building archive, otherwise you will be grabbing 60 mon audio archives 
    # that don't exist yet
    if endDelta > 0: 
        if endDelta < local.startHourlyCron: # tail end of show ends in time to build archive
            LastHourRaw = ThisHour + relativedelta(hours = -0)
            print 'line 113'
        else: # tail end of show ends AFTER archiver is ready for it
            LastHourRaw = ThisHour + relativedelta(hours = -0)
            print 'line 116'
    else: # no tail added to show archive, so no spill over to next hour 
        LastHourRaw = ThisHour + relativedelta(hours = -1)   
        print 'line 119'
    print 'GT.LastHourRaw -> ', str(LastHourRaw)
    print 'GT.LastHour.weekday() -> ', str(LastHourRaw.weekday())
    today = num2day[LastHourRaw.weekday()]
    print 'GT.today -> ', str(today)

    timeTuple = str(LastHourRaw).split(':')[0]
    LastHour = int(timeTuple.split(' ')[1])
    return LastHour, today
    
def day2spinDay(fullDayStr, hour, startSpinDay):
    '''
    adjust for the fact that Spinitron day starts at 6am instead of midnight
    accepts:
        full day name string (ex: 'Sunday')
        hour: integer in range [0 .. 23]
        startSpinDay: integer in range [0 .. 23]
    
    returns adjusted full day name string
    #TODO: does this need to be implemented in datetime module???
    '''
    day2num = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3,
           'Friday':4, 'Saturday':5, 'Sunday':6}
    num2day = { 7: 'SaturdayAFTER', -1: 'Sunday' , 0 : 'Monday' , 
            1 : 'Tuesday' , 2 :'Wednesday',  3 : 'Thursday' , 
            4 : 'Friday' , 5 :'Saturday', 6 : 'Sunday'}
    if startSpinDay != 0:
        if hour <= startSpinDay:
            yesterday = num2day[((day2num[fullDayStr] - 1) % 7)]
            fullDayStr = yesterday
    return fullDayStr
    
def spinDay2day(spinDay, hour, startSpinDay):
    '''
    converts spinitron day to real day, which only happens between
    midnight and start of broadcast day (often 6am or midnight)
    accepts:
        spinDay: full string day, ex: "Sunday"
        hour: int [0 .. 23] = this is the hour that the show ends
            #commnt to self: could be beginning or end hour of show, anyway ...
        startSpinDay: int range [0..23] represents the hour that radio broadcast
            day starts, typically either 6am or midnight
    returns:
        day string, adjusted back from spinday to realday
    '''
    day2num = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3,
           'Friday':4, 'Saturday':5, 'Sunday':6}
    num2day = { 7: 'SaturdayAFTER', -1: 'Sunday' , 0 : 'Monday' , 
            1 : 'Tuesday' , 2 :'Wednesday',  3 : 'Thursday' , 
            4 : 'Friday' , 5 :'Saturday', 6 : 'Sunday'}  
    realDayStr = spinDay
    if startSpinDay != 0:
        if hour <= startSpinDay:
            realDayStr = num2day[((day2num[spinDay] + 1) % 7)]
    return realDayStr
    
def spinDay22day(spinDay, time, startSpinDay):
    '''
    better spinDay2day
    converts spinitron day to real day, which only happens between
    midnight and start of broadcast day (typically midnight or 6am)
    accepts:
        spinDay: full str day, with day ending @ 6am
        time: in datetime.time format (this is the time the show ends)
        startSpinDay = int in range [0..23] ex 6 = 6:00am
    returns:
        realDayStr = a full day string (ex: 'Sunday')
        **NOT* *date* in datetime.date format
        perhaps other formats, if it is discovered that these are needed
    '''
    day2num = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3,
           'Friday':4, 'Saturday':5, 'Sunday':6}
    num2day = { 7: 'SaturdayAFTER', -1: 'Sunday' , 0 : 'Monday' , 
            1 : 'Tuesday' , 2 :'Wednesday',  3 : 'Thursday' , 
            4 : 'Friday' , 5 :'Saturday', 6 : 'Sunday'}  
    cutoff = DT.time(startSpinDay, 0, 0)
    realDayStr = spinDay
    if not(time >= cutoff):
        realDayStr = num2day[((day2num[spinDay] + 1) % 7)]
    return realDayStr        
    
def getShows2Archive (sched, LastHour, spinDay):
    '''
    accepts:
        sched = schedule in CharlieSched format
        LastHour int in range from 0 ..23
        spinDay = full string day name, spinDays end @ 6am
    returns:
        a list of all shows that ended during the last hour,
    '''
    retList = []
        
    for show in sched[spinDay]:
        #print
        #print 'GS2A show -> ',str(show)
        #print 'GS2A sched[day][show] -> ', str(sched[day][show])
        showHour = int(str(sched[spinDay][show]['OffairTime']).split(':')[0]) 
        #showHour = int(str(show['OffairTime']).split(':')[0])
        if showHour == LastHour:
            retList.append(sched[spinDay][show])
    return retList   
    
def strTime2timeObject(strTime):
    '''
    #I don't think this is getting used now, I'm not really using DT.time class
        anywhere else in the code base, see mytime2DT, below, which is very
        similar to this function, but uses the DT.datetime class
    accepts:
        strTime: string in this format: "00:00:00"
    returns:
        datetime.time object (hours, minutes, seconds, no date info)
    '''
    #below code is inefficient.  Oh well
    myHour = int(str(strTime).split(':')[0])
    myMin = int(str(strTime).split(':')[1])
    mySec = int(str(strTime).split(':')[2])
    DTtime = DT.time(myHour, myMin, mySec)
    return DTtime   

def mytime2DT(time):
    '''
    accepts: 
        time: string in "00:00:00" format
        spinDay: full string (ex: "Sunday")
    returns:
        time in datetime format
    '''
    
    myHour = int(str(time).split(':')[0])
    myMinute = int(str(time).split(':')[1])
    mySecond = int(str(time).split(':')[2])
    DTtime = DT.datetime.now() + relativedelta(hour=myHour, minute=myMinute,
         second=mySecond, microsecond=0) 

    #nowDay = num2day[DTtime.weekday()]
    now = DT.datetime.now()
    # assuming that shows are archived less than 24 hours after they are
    # broadcast, now < DTtime only if "time" occured yesterday
    if now < DTtime: 
        DTtime = DTtime - DT.timedelta(days=1)
    return DTtime

def numArchives(start,end):
    '''
    accepts:
        start, end: type = datetime.datetime
    '''
    partialEnd = False
    startHour = start.timetuple().tm_hour
    endHour = end.timetuple().tm_hour
    if start.timetuple().tm_mday != end.timetuple().tm_mday:
        endHour += 24
    numHours = endHour - startHour
    #partialEnd is True if the last archived hour to grab needs to have its 
        # end truncated
        # if show ends in the 59th minute, we consider show to end on the hour
    if end.timetuple().tm_min > 0 and end.timetuple().tm_min < 59:
        numHours +=1
        partialEnd = True
    return numHours, partialEnd
    
def buildChunkList(show, spinDay):
    '''
    accepts:
        show in showsToArchive format
        spinDay: fullStrDay (ex: 'Sunday'), spinDay ends @ 6am
    returns:
        ChunkList (a list of hour long archives that will be used to build
            mp3 archive for a particular show)
        Each element of the ChunkList is a dict containing the following:
            'StartTime' : type = datetime.datetime.timetuple()
            'Delta': type = datetime.timedelta
    '''
    print '============================================'
    print 'buildChunkList'
    print '============================================'
    
    #determine start and end of show, with deltas added in
    startHour = strTime2timeObject(show['OnairTime'])

    print 'startHour -> ', str(startHour)
    print 'spinDay22day(spinDay, startHour) ->',
    print spinDay22day(spinDay, startHour, startSpinDay)
    print 'showStart(showOnairTime) -> ', str(show['OnairTime'])
    print 'showStart(day) -> ',str(spinDay22day(spinDay, startHour, startSpinDay))
    
    showStart = mytime2DT(show['OnairTime']) + relativedelta(minutes=startDelta)
    #endHour = strTime2timeObject(show['OffairTime'])
    showEnd = mytime2DT(show['OffairTime']) + relativedelta(minutes=endDelta)

    print 'showStart -> ', str(showStart)
    print 'showEnd -> ', str(showEnd)
    print type(showEnd)
    print
    
    # if start time > end time, then show must stradle midnight hour
    if showStart > showEnd:
        # I think this will fix matters if a show straddles midnight
        # otherwise, maybe get a 24 hour + audio archive ?!?!
        showStart = showStart + relativedelta(days=-1)
        
    duration = showEnd - showStart
    duraSeconds = duration.seconds
    print 'duraSeconds -> ', duraSeconds

    print 'show duration: -> ', str(duration)
    print 'type(duration) -> ', str(type(duration))
    print 'showStart -> ', str(showStart)
    print 'showEnd -> ', str(showEnd)
    
    showHours, partialEnd = numArchives(showStart, showEnd)
    print showHours #start counting @ zero
    print range(showHours)
    partialOffset = 0
    if partialEnd:
        partialOffset = 1
    
    
    chunkList = []
    chunk= {}
    count = 0
    #if the show is an hour or less, does not stradle an hour, and doesn't end
        # at the end of an hour, this is an edge case ...
    if showHours == 1 and partialEnd == True:
        chunk['StartTime'] = showStart
        chunk['TimeDelta'] = showEnd - showStart
    
    else: #not an edge case
        # offset = time from beginning of show to end of first hour
            # ex: show starts at 2:15, offset is 45 minutes
        offset = (showStart + relativedelta(hours=+1, 
                            minute =0, second=0)) -showStart
          
        if count < showHours:
            chunk['StartTime'] = showStart
            chunk['TimeDelta'] = offset
            chunkList.append(chunk)
            count += 1
        
        while count + partialOffset < showHours: # working with a complete hour
            chunk = {}   
            chunk['StartTime'] = chunkList[-1]['StartTime'] + \
                            chunkList[-1]['TimeDelta']
            chunk['TimeDelta'] = DT.timedelta(seconds=3600)
            chunkList.append(chunk)
            count += 1
        
        if partialEnd:
            chunk = {}
            chunk['StartTime'] = chunkList[-1]['StartTime'] + \
                            chunkList[-1]['TimeDelta']
            chunk['TimeDelta'] = showEnd - chunk['StartTime']
            chunkList.append(chunk)
                                        
    return chunkList

def pad(shortStr, padChar = '0', fullLen = 2):
    '''
    accepts:
        a string 
        padChar (a single character string)
        len (int) desired length of output string
    returns:
        a string with padding prepended
    '''
    padding = ''
    for i in range(fullLen - len(shortStr)):
        padding = ''.join((padding, padChar ))
    retStr = ''.join((padding, shortStr))
    return retStr
        
    
        
def buildmp3(show, spinDay):
    '''
    accepts:
        show in showsToArchive format
        spinDay: fullStrDay (ex: 'Sunday'), spinDay ends @ 6am
    returns:
        an mp3 for archiving
    '''

    #each hour has a start and end time within the hour
        # convert start & end times to datetime format, add in time deltas
        
    #if len(chunkList) == 0:
        #errorNow = DT.datetime.now() + relativedelta(hour=0, minute=0, second=0, microsecond=0)
    #elif len(chunkList) == 1:
        #pick start & end points to create mp3Out
        #for this hour long archive (aka "chunk"), create start and end attributes
    #else (two or more archives to grab):
        #for first archive:
            #modify start attribute
        #for last archive in list:
            #modify end attribute
    pass

def cleanOutFolder(folder, extension=''):
    '''
    remove all files in designated folder (absolute path, please), optionally 
        filtered to files with the specified extension (extension must include 
        leading dot)
    previous working directory is restored 
    return value = list containing filenames of deleted files
    '''
    current = os.getcwd()
    os.chdir(folder)
    rex = ''.join(('*',extension))
    hatchetList = list(glob.iglob(rex))
    for el in hatchetList:
        os.remove(''.join((folder,'/',el)))
    os.chdir(current)
    return hatchetList

def audioConcat(sourceFolder, destFolder, postfix = '.mp3'):
    '''
    concatenate all audio files with the specified postfix
        (audio source files sorted alphabetically)
    copy concatenated audio file into destFolder, name = "New.<postfix>"
    returns 1 on success
    '''
    current = os.getcwd()
    os.chdir(sourceFolder)
    targetFile = ''.join((destFolder,'new',postfix))
    #grab list of files in sourceFolder
    rex = ''.join(('*',postfix))
    concatList = sorted(list(glob.iglob(rex)))
    #if there are multiple audio files in the folder where we expect them ..
    if len(concatList) > 1:
        #then build sox command
        cmd = concatList
        cmd.insert(0,'sox')
        cmd.append(targetFile)
        print '+++++++++++++++++++++++++++++++++++++'
        print 'audioConcat: ', cmd
        print '+++++++++++++++++++++++++++++++++++++'
        #execute sox command to concat audio files
        call(cmd)
    #else, if there is only one audio file, rename it and move it
    elif len(concatList) == 1:
        sourceFile = ''.join((sourceFolder,concatList[0]))
        os.rename(sourceAudio, targetFile)
    else: # no audio files in folder
        print 'ERROR: no audio files in ',sourceFolder, ' to concat'
    #return to current working dir 
    os.chdir(current)
    print 'END: audioConcat'

def createAudioChunks(chunkList, tmpFolder):
    '''
    using chunkList, populate tmpFolder with mp3 chunks for subsequent
    concatenation.
    mp3s named 0.mp3, 1.mp3, ...
    no return value ...
    '''
    hatchetList = cleanOutFolder(tmpFolder,'.mp3')
    if len(hatchetList):
        print 'removed -> ', str(hatchetList), ' from ', tmpFolder
    else:
        print tmpFolder, ' started empty.'
    for x, chunk in enumerate(chunkList):
        print 'chunk #' + str(x)
        year = str(chunk['StartTime'].timetuple().tm_year)
        month = pad(str(chunk['StartTime'].timetuple().tm_mon))
        day = pad(str(chunk['StartTime'].timetuple().tm_mday))
        hour = pad(str(chunk['StartTime'].timetuple().tm_hour))
        minute = pad(str(chunk['StartTime'].timetuple().tm_min))
        SourceOgg = ''.join((local.archiveSource, year, '/', month, '/',
                               day, '/', hour, '-00-00.ogg'))
        #fullHour is a boolean
        DeltaSeconds = chunk['TimeDelta'].total_seconds()
        fullHour = (3540 < DeltaSeconds < 3660 )        
        targetMp3 = ''.join((tmpFolder, '/', str(x), '.mp3'))
        if fullHour: # no trim necesary, just convert to mp3
            print tab,'fullHour [',str(x),']'
            print tab,'    ','SourceOgg -> ', str(SourceOgg)
            print tab,'    ', 'targetMp3 -> ', str(targetMp3)
            cmd = ['sox', SourceOgg, targetMp3]
            print cmd
            call(cmd)
        else: #trim the hour long archive down to size
            startTrim = str(60 * int(minute))
            print tab,'Not fullHour [',str(x),']'
            print tab,'    SourceOgg -> ', str(SourceOgg)
            print tab,'    targetMp3 -> ', str(targetMp3)
            print tab,'    startTrim -> ', str(startTrim)
            print tab,'    DeltaSeconds -> ', str(DeltaSeconds)
            cmd = ['sox', SourceOgg, targetMp3, 'trim', startTrim, str(DeltaSeconds)]
            print cmd
            call(cmd)    
    
def addNewRemoteFolders(charlieSched):
    '''
    accepts:
        schedule in charlieSched format
    action:
        if a necessary folder on the website doesn't exist, create it
    returns:
        nothing
    '''
    def createRemoteFolder(timeslot):
        '''
        accepts a timeslot string, example format:
           "Sat-20:00:00-22:00:00" = show starts Saturday @ 8pm 
        makes folder as follows:
           "Sat2000" (but only if it doesn't already exist)
        returns:
            name of folder (whether or not it already exists)
        '''
        tempList = timeslot.split('-') #split timeslot @ dashes ex: 'Sat-20:00:00-22:00:00'
        timeList = tempList[1].split(':') #split start time ex: 15:00:00
        subFolder = ''.join((tempList[0],timeList[0], timeList[1]))
        destFolder =  ''.join((local.archiveDest, subFolder))

        try:
            sftp.mkdir(destFolder)
            print "NEW AUDIO ARCHIVE FOLDER CREATED -> ",destFolder
        except IOError:
            # I hope this indicates that folder has already been created
            # IOError is pretty wide open ...
            pass
        return destFolder
    
    #ftp = ftplib.FTP(key.host, key.username, key.passwd)
    sftp = pysftp.Connection(host=key.host, username=key.username, password=key.passwd)
    #ftp.connect(host = key.host, port=key.port)
    for day in charlieSched:
        for timeslot in charlieSched[day]:
             createRemoteFolder(timeslot)
                
    
import os
import local
import key
import SpinPapiLib as SPlib

import datetime as DT
from dateutil.relativedelta import *
import calendar

import pprint

from subprocess import call

from contextlib import contextmanager
import sys

import glob
import ftplib
import pysftp
